"""
Air Quality Platform - Authentication Routes
User registration, login, logout with JWT tokens.
"""

import os
import sys
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.models import User, UserRole
from backend.auth.jwt_handler import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, decode_token, blacklist_token
)

router = APIRouter()


# ===================== SCHEMAS =====================

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    email: str = Field(..., max_length=120)
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    full_name: Optional[str]
    created_at: str


# ===================== ROUTES =====================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user account."""
    # Check existing user
    existing = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered"
        )

    # Create user
    user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password),
        role=UserRole.VIEWER,
        full_name=request.full_name,
        phone=request.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name,
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login with username and password."""
    user = db.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()

    # Generate tokens
    token_data = {"sub": str(user.id), "username": user.username, "role": user.role.value}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name,
        }
    )


@router.post("/logout")
async def logout(token: str = ""):
    """Logout and invalidate token."""
    if token:
        blacklist_token(token)
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user(db: Session = Depends(get_db)):
    """Get current user profile (demo mode - returns first user or default)."""
    user = db.query(User).first()
    if user:
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.value,
            "full_name": user.full_name,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
    return {
        "id": 0,
        "username": "demo_user",
        "email": "demo@airquality.io",
        "role": "viewer",
        "full_name": "Demo User",
    }
