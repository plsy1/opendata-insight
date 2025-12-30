from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from services.auth import AuthService, TokenResult

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def token_interceptor(token: str = Depends(oauth2_scheme)) -> None:
    if AuthService.is_token_valid(token) != TokenResult.VALID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
