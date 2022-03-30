from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .database import SessionLocal
from .settings import get_settings

auth_scheme = HTTPBearer()


def token(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    tokens = [x.get_secret_value() for x in get_settings().api_tokens]
    if creds.credentials not in tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
