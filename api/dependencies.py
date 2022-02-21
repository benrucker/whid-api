from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, status, HTTPException
from .database import SessionLocal

auth_scheme = HTTPBearer()
with open('.usertokens') as f:
    usertokens = [x.strip() for x in f.readlines()]


def token(creds: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if creds.credentials not in usertokens:
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
