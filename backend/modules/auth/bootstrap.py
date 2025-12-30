from sqlalchemy.orm import Session
from database import User, SessionLocal
from utils.logs import LOG_INFO
from .password import generate_random_password


def create_root_user_if_not_exists(db: Session):
    root_user = db.query(User).filter(User.username == "root").first()

    if root_user:
        return

    hashed_password, raw_password = generate_random_password()
    new_user = User(
        username="root",
        password=hashed_password,
    )

    db.add(new_user)
    db.commit()

    LOG_INFO(f"root 用户已创建，密码为: {raw_password}")


def init_user():
    db = SessionLocal()
    try:
        create_root_user_if_not_exists(db)
    finally:
        db.close()
