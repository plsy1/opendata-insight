import bcrypt
import secrets
import string


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )

def generate_random_password(length: int = 32) -> tuple[str, str]:
    alphabet = string.ascii_letters + string.digits + string.punctuation
    raw_password = "".join(secrets.choice(alphabet) for _ in range(length))
    return hash_password(raw_password), raw_password
