"""User schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator


class UserBase(BaseModel):
    """Base user schema."""
    
    name: str = Field(..., min_length=1, max_length=100, description="User name")
    email: EmailStr = Field(..., description="User email")
    phone: str = Field(..., min_length=10, max_length=20, description="User phone number")
    
    @validator("phone")
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        import re
        
        # Remove all non-digit characters
        digits_only = re.sub(r'[^\d]', '', v)
        
        # Check if we have a reasonable number of digits
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number must contain 10-15 digits")
        
        # Return the original formatted phone
        return v
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Validate name format."""
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="User name")
    email: Optional[EmailStr] = Field(None, description="User email")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="User phone number")
    
    @validator("phone")
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number format."""
        if v is None:
            return v
        
        import re
        
        # Remove all non-digit characters
        digits_only = re.sub(r'[^\d]', '', v)
        
        # Check if we have a reasonable number of digits
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number must contain 10-15 digits")
        
        return v
    
    @validator("name")
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate name format."""
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty")
        return v


class User(UserBase):
    """Schema for user response."""
    
    id: int = Field(..., description="User ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        """Pydantic config."""
        
        orm_mode = True
        

class UserSearchParams(BaseModel):
    """Schema for user search parameters."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=100, description="Items per page")
    search: str = Field(default="", description="Search query")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="Sort order")
    
    @validator("sort_by")
    def validate_sort_by(cls, v: str) -> str:
        """Validate sort field."""
        allowed_fields = ["id", "name", "email", "phone", "created_at", "updated_at"]
        if v not in allowed_fields:
            raise ValueError(f"Sort field must be one of: {', '.join(allowed_fields)}")
        return v