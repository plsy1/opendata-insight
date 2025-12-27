from fastapi import APIRouter, HTTPException, Depends, Form
from fastapi.security import OAuth2PasswordRequestForm
from services.auth import *
from sqlalchemy.orm import Session
from database import get_db
from config import _config

router = APIRouter()


@router.post("/login")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):

    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        minutes=int(_config.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )

    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/verify")
async def verify(access_token: str = Form(...)):

    return is_token_expiration(access_token)


@router.post("/changepassword")
def change_password_api(
    username: str = Form(...),
    old_password: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        return change_password(
            db=db,
            username=username,
            old_password=old_password,
            new_password=new_password,
        )
    except HTTPException as e:
        raise e
