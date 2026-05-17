from datetime import datetime, timedelta
from typing import Literal

import bcrypt
from jose import JWTError, jwt

from config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_mini_program_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.MINI_PROGRAM_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "token_type": "mini_program"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_admin_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ADMIN_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "token_type": "admin"})
    return jwt.encode(to_encode, settings.ADMIN_SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        pass
    try:
        return jwt.decode(token, settings.ADMIN_SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def decode_token_with_secret(token: str, secret: str) -> dict | None:
    try:
        return jwt.decode(token, secret, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None