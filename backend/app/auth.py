import os
import secrets
from fastapi import Header, HTTPException
from pydantic import BaseModel

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "admin-demo-token")


class LoginRequest(BaseModel):
    username: str
    password: str


def login_check(data: LoginRequest) -> dict:
    username_ok = secrets.compare_digest(data.username, ADMIN_USERNAME)
    password_ok = secrets.compare_digest(data.password, ADMIN_PASSWORD)

    if not (username_ok and password_ok):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return {
        "token": ADMIN_TOKEN,
        "username": ADMIN_USERNAME,
        "role": "admin"
    }


def require_admin(authorization: str | None = Header(default=None)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = authorization[len(prefix):]
    if not secrets.compare_digest(token, ADMIN_TOKEN):
        raise HTTPException(status_code=401, detail="Invalid token")

    return {
        "username": ADMIN_USERNAME,
        "role": "admin"
    }
