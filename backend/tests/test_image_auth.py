import unittest
from types import SimpleNamespace
from unittest.mock import patch

import httpx
from fastapi import Depends, FastAPI, HTTPException, Response

import routers.auth as auth_router
import routers.system as system_router
from database import get_db
from routers.dependencies.auth_dependencies import (
    image_cookie_interceptor,
    token_interceptor,
)
from services.auth import AuthService, LoginResult, TokenResult


class ImageAuthenticationTests(unittest.TestCase):
    def test_valid_image_cookie_is_accepted(self):
        with patch.object(
            AuthService,
            "is_token_valid",
            return_value=TokenResult.VALID,
        ):
            self.assertIsNone(image_cookie_interceptor("valid-token"))

    def test_missing_or_invalid_image_cookie_is_rejected(self):
        for token in (None, "invalid-token"):
            with self.subTest(token=token), patch.object(
                AuthService,
                "is_token_valid",
                return_value=TokenResult.INVALID,
            ):
                with self.assertRaises(HTTPException) as raised:
                    image_cookie_interceptor(token)
                self.assertEqual(raised.exception.status_code, 401)

    def test_login_sets_http_only_image_cookie(self):
        response = Response()
        form = SimpleNamespace(username="admin", password="secret")
        with patch.object(
            AuthService,
            "login",
            return_value=(LoginResult.SUCCESS, "signed-jwt"),
        ):
            result = auth_router.login(response, form, object())

        cookie = response.headers["set-cookie"]
        self.assertEqual(result["access_token"], "signed-jwt")
        self.assertIn("image_access=signed-jwt", cookie)
        self.assertIn("HttpOnly", cookie)
        self.assertIn("Path=/api/v1/system", cookie)
        self.assertIn("SameSite=lax", cookie)

    def test_logout_expires_image_cookie(self):
        response = Response()
        auth_router.logout(response)

        cookie = response.headers["set-cookie"]
        self.assertIn("image_access=", cookie)
        self.assertIn("Max-Age=0", cookie)
        self.assertIn("Path=/api/v1/system", cookie)


class ImageCookieFlowTests(unittest.IsolatedAsyncioTestCase):
    async def test_existing_bearer_session_bootstraps_image_cookie(self):
        app = FastAPI()
        app.include_router(system_router.router, prefix="/api/v1/system")

        @app.get(
            "/api/v1/protected",
            dependencies=[Depends(token_interceptor)],
        )
        def protected_endpoint():
            return {"ok": True}

        def override_db():
            yield object()

        app.dependency_overrides[get_db] = override_db
        transport = httpx.ASGITransport(app=app)
        with patch.object(
            AuthService,
            "is_token_valid",
            return_value=TokenResult.VALID,
        ), patch.object(system_router, "get_image_source", return_value=None):
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                protected = await client.get(
                    "/api/v1/protected",
                    headers={"Authorization": "Bearer existing-jwt"},
                )
                image = await client.get(
                    f"/api/v1/system/images/{'a' * 64}"
                )

        self.assertEqual(protected.status_code, 200)
        self.assertIn("image_access=existing-jwt", protected.headers["set-cookie"])
        self.assertEqual(image.status_code, 404)

    async def test_login_cookie_is_automatically_used_and_cleared(self):
        app = FastAPI()
        app.include_router(auth_router.router, prefix="/api/v1/auth")
        app.include_router(system_router.router, prefix="/api/v1/system")

        def override_db():
            yield object()

        app.dependency_overrides[get_db] = override_db
        transport = httpx.ASGITransport(app=app)
        with patch.object(
            AuthService,
            "login",
            return_value=(LoginResult.SUCCESS, "signed-jwt"),
        ), patch.object(
            AuthService,
            "is_token_valid",
            return_value=TokenResult.VALID,
        ), patch.object(system_router, "get_image_source", return_value=None):
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://testserver",
            ) as client:
                login = await client.post(
                    "/api/v1/auth/login",
                    data={"username": "admin", "password": "secret"},
                )
                authenticated_image = await client.get(
                    f"/api/v1/system/images/{'a' * 64}"
                )
                logout = await client.post("/api/v1/auth/logout")
                unauthenticated_image = await client.get(
                    f"/api/v1/system/images/{'a' * 64}"
                )

        self.assertEqual(login.status_code, 200)
        self.assertEqual(authenticated_image.status_code, 404)
        self.assertEqual(logout.status_code, 204)
        self.assertEqual(unauthenticated_image.status_code, 401)


if __name__ == "__main__":
    unittest.main()
