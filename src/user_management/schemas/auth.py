"""Authentication schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Token(BaseModel):
    """Token response schema."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """Token data schema."""
    
    sub: str = Field(..., description="Subject (user identifier)")
    exp: int = Field(..., description="Expiration timestamp")
    iat: int = Field(..., description="Issued at timestamp")


class LoginRequest(BaseModel):
    """Login request schema."""
    
    username: str = Field(..., description="Username (for demo purposes)")
    password: str = Field(..., description="Password (for demo purposes)")