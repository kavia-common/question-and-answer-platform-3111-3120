from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.api.config import get_settings
from src.api.database import get_db
from src.api.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# PUBLIC_INTERFACE
def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """Create a JWT access token using configured secret and algorithm."""
    settings = get_settings()
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes or settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email.ilike(email)).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)


# PUBLIC_INTERFACE
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Decode JWT token and return the authenticated user."""
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if sub is None:
            raise credentials_exception
        user_id = int(sub)
    except JWTError:
        raise credentials_exception
    user = get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    return user
