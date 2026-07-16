from fastapi import APIRouter, Form, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from services.auth import ChangePasswordResult, TokenResult, LoginResult, AuthService
from .dependencies.auth_dependencies import (
    clear_image_auth_cookie,
    set_image_auth_cookie,
)


router = APIRouter()


def map_enum_to_http(result_enum, mappings: dict):
    if result_enum in mappings:
        status_code, detail = mappings[result_enum]
        raise HTTPException(status_code=status_code, detail=detail)


@router.post("/login")
def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    result, token = AuthService.login(db, form_data.username, form_data.password)
    map_enum_to_http(
        result,
        {
            LoginResult.USER_NOT_FOUND: (401, "Incorrect username or password"),
            LoginResult.INVALID_CREDENTIALS: (401, "Incorrect username or password"),
        },
    )
    set_image_auth_cookie(response, token)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    clear_image_auth_cookie(response)


@router.post("/verify")
def verify_token(access_token: str = Form(...)):
    result = AuthService.is_token_valid(access_token)
    map_enum_to_http(
        result,
        {
            TokenResult.EXPIRED: (401, "Token expired or invalid"),
            TokenResult.INVALID: (401, "Token invalid"),
        },
    )
    return {"valid": True, "message": "Token is valid"}


@router.post("/changepassword")
def change_password(
    username: str = Form(...),
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
):
    result = AuthService.change_password(db, username, old_password, new_password)
    map_enum_to_http(
        result,
        {
            ChangePasswordResult.USER_NOT_FOUND: (404, "User not found"),
            ChangePasswordResult.INVALID_PASSWORD: (401, "Incorrect old password"),
        },
    )
    return {"message": "Password updated successfully"}
