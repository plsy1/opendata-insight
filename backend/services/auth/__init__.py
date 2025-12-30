from sqlalchemy.orm import Session
from modules.auth import (
    verify_password,
    hash_password,
    is_token_expired,
    create_access_token,
)
from database import User
from config import _config
from datetime import timedelta
from .enums import ChangePasswordResult, TokenResult, LoginResult


class AuthService:

    @classmethod
    def change_password(
        cls, db: Session, username: str, old_password: str, new_password: str
    ) -> ChangePasswordResult:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return ChangePasswordResult.USER_NOT_FOUND
        if not verify_password(old_password, user.password):
            return ChangePasswordResult.INVALID_PASSWORD
        user.password = hash_password(new_password)
        db.commit()
        return ChangePasswordResult.OK

    @classmethod
    def is_token_valid(cls, token: str) -> TokenResult:
        if is_token_expired(token):
            return TokenResult.EXPIRED
        return TokenResult.VALID

    @classmethod
    def login(
        cls, db: Session, username: str, password: str
    ) -> tuple[LoginResult, str | None]:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return LoginResult.USER_NOT_FOUND, None
        if not verify_password(password, user.password):
            return LoginResult.INVALID_CREDENTIALS, None
        expires = timedelta(minutes=int(_config.get("ACCESS_TOKEN_EXPIRE_MINUTES")))
        token = create_access_token({"sub": username}, expires)
        return LoginResult.SUCCESS, token
