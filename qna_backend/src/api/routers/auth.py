from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.api.auth import get_password_hash, verify_password, create_access_token, get_current_user, get_user_by_email
from src.api.database import get_db
from src.api.models import User
from src.api.schemas import UserCreate, UserOut, Token
router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=UserOut, summary="User signup", description="Create a new user account.")
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    PUBLIC_INTERFACE
    Signup endpoint. Creates a new user with hashed password.

    Parameters:
    - user_in: UserCreate - email, full_name, password

    Returns:
    - UserOut: id, email, full_name
    """
    existing = get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token, summary="User login", description="Authenticate user and obtain JWT access token.")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    PUBLIC_INTERFACE
    Login endpoint.

    Accepts:
    - OAuth2PasswordRequestForm (username=email, password)

    Returns:
    - Token: access_token, token_type
    """
    user = get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password.")
    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut, summary="Get current user", description="Retrieve the authenticated user's profile.")
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    PUBLIC_INTERFACE
    Returns the current authenticated user's profile.
    """
    return current_user
