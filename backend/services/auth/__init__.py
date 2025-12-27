import bcrypt, secrets, string
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import User, SessionLocal
from datetime import datetime, timedelta, timezone
from config import _config
from utils.logs import LOG_INFO


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def change_password(db: Session, username: str, old_password: str, new_password: str):

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not verify_password(old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect old password",
        )

    user.password = hash_password(new_password)

    db.commit()

    return {"message": "Password updated successfully"}


def get_user(db, username: str):
    if username in db:
        return db[username]


def verify_token_expiration(token: str, credentials_exception):
    try:
        payload = jwt.decode(
            token, _config.get("SECRET_KEY"), algorithms=[_config.get("ALGORITHM")]
        )
        expiration: str = payload.get("exp")
        if expiration is None:
            raise credentials_exception
        if datetime.now() > datetime.fromtimestamp(expiration):
            raise credentials_exception
        return True

    except JWTError as e:
        raise credentials_exception


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone(timedelta(hours=8))) + expires_delta
    else:
        expire = datetime.now(timezone(timedelta(hours=8))) + timedelta(
            minutes=_config.get("ACCESS_TOKEN_EXPIRE_MINUTES")
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, _config.get("SECRET_KEY"), algorithm=_config.get("ALGORITHM")
    )
    return encoded_jwt


def tokenInterceptor(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_token_expiration(token, credentials_exception)


def generate_random_password(length=32) -> str:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(alphabet) for _ in range(length))
    return hash_password(password), password


def create_root_user_if_not_exists(db: Session):
    root_user = db.query(User).filter(User.username == "root").first()

    if root_user:
        return
    else:
        password, rawPass = generate_random_password()
        new_user = User(username="root", password=password)
        db.add(new_user)
        db.commit()

        LOG_INFO(f"root 用户已创建，密码为: {rawPass}")


def initUser():
    db = SessionLocal()
    try:
        create_root_user_if_not_exists(db)
    finally:
        db.close()


def is_token_expiration(token: str) -> bool:
    try:
        payload = jwt.decode(
            token, _config.get("SECRET_KEY"), algorithms=[_config.get("ALGORITHM")]
        )
        exp = payload.get("exp")
        if exp is None:
            return False

        if datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
            return False

        return True

    except JWTError:
        return False
