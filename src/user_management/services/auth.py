"""Authentication service."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from user_management.core.config import settings
from user_management.schemas.auth import TokenData

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict[str, Any]) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> TokenData | None:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            sub: str = payload.get("sub")
            exp: int = payload.get("exp")
            iat: int = payload.get("iat")
            
            if sub is None or exp is None or iat is None:
                return None
            
            return TokenData(sub=sub, exp=exp, iat=iat)
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_demo_user(username: str, password: str) -> bool:
        """Authenticate demo user (for demo purposes only)."""
        # Demo credentials - in a real app, this would check against a user database
        demo_users = {
            "admin": "admin123",
            "demo": "demo123",
            "user": "user123",
        }
        
        return demo_users.get(username) == password