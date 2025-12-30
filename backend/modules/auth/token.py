from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from config import _config


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None,
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone(timedelta(hours=8))) + expires_delta
    else:
        expire = datetime.now(timezone(timedelta(hours=8))) + timedelta(
            minutes=_config.get("ACCESS_TOKEN_EXPIRE_MINUTES")
        )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        _config.get("SECRET_KEY"),
        algorithm=_config.get("ALGORITHM"),
    )


def is_token_expired(token: str) -> bool:
    try:
        payload = jwt.decode(
            token,
            _config.get("SECRET_KEY"),
            algorithms=[_config.get("ALGORITHM")]
        )
        exp = payload.get("exp")
        if exp is None:
            return True

        now = datetime.now(timezone.utc)
        return now > datetime.fromtimestamp(exp, tz=timezone.utc)
    except JWTError:
        return True