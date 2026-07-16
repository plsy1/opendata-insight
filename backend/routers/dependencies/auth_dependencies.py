from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordBearer
from config import _config
from services.auth import AuthService, TokenResult

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def set_image_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=_config.get("IMAGE_AUTH_COOKIE"),
        value=token,
        max_age=int(_config.get("ACCESS_TOKEN_EXPIRE_MINUTES")) * 60,
        httponly=True,
        secure=_config.get_bool("IMAGE_COOKIE_SECURE"),
        samesite="lax",
        path="/api/v1/system",
    )


def clear_image_auth_cookie(response: Response) -> None:
    response.delete_cookie(
        key=_config.get("IMAGE_AUTH_COOKIE"),
        path="/api/v1/system",
        secure=_config.get_bool("IMAGE_COOKIE_SECURE"),
        httponly=True,
        samesite="lax",
    )


def token_interceptor(
    response: Response,
    token: str = Depends(oauth2_scheme),
) -> None:
    if AuthService.is_token_valid(token) != TokenResult.VALID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    set_image_auth_cookie(response, token)


def image_cookie_interceptor(
    image_access: str | None = Cookie(
        default=None,
        alias=_config.get("IMAGE_AUTH_COOKIE"),
    ),
) -> None:
    if not image_access or AuthService.is_token_valid(image_access) != TokenResult.VALID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Image authentication required",
        )
