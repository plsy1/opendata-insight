from enum import Enum, auto

class ChangePasswordResult(Enum):
    OK = auto()
    USER_NOT_FOUND = auto()
    INVALID_PASSWORD = auto()

class TokenResult(Enum):
    VALID = auto()
    EXPIRED = auto()
    INVALID = auto()

class LoginResult(Enum):
    SUCCESS = auto()
    INVALID_CREDENTIALS = auto()
    USER_NOT_FOUND = auto()