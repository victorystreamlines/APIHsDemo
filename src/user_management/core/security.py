"""Security utilities."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from user_management.database.base import get_db
from user_management.services.auth import AuthService

# HTTP Bearer security scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> str:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token_data = AuthService.verify_token(credentials.credentials)
        if token_data is None:
            raise credentials_exception
        
        username: str = token_data.sub
        if username is None:
            raise credentials_exception
        
        return username
    except Exception:
        raise credentials_exception


def get_optional_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> str | None:
    """Get current user if authenticated, otherwise None."""
    if credentials is None:
        return None
    
    try:
        token_data = AuthService.verify_token(credentials.credentials)
        if token_data is None:
            return None
        
        return token_data.sub
    except Exception:
        return None