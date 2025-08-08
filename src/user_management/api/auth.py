"""Authentication API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from user_management.core.config import settings
from user_management.schemas.auth import LoginRequest, Token
from user_management.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBasic()


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest) -> Token:
    """Login and get access token."""
    # Authenticate user
    if not AuthService.authenticate_demo_user(login_data.username, login_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = AuthService.create_access_token(
        data={"sub": login_data.username}
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/demo-users")
async def get_demo_users() -> dict:
    """Get demo user credentials for testing."""
    return {
        "demo_users": [
            {"username": "admin", "password": "admin123"},
            {"username": "demo", "password": "demo123"},
            {"username": "user", "password": "user123"},
        ],
        "note": "These are demo credentials for testing purposes only",
    }