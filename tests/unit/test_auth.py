"""Unit tests for authentication service."""

from __future__ import annotations

import pytest
from jose import jwt

from user_management.core.config import settings
from user_management.services.auth import AuthService


class TestAuthService:
    """Test authentication service."""
    
    def test_password_hashing(self):
        """Test password hashing and verification."""
        password = "test_password123"
        hashed = AuthService.get_password_hash(password)
        
        # Hash should be different from original password
        assert hashed != password
        
        # Should verify correctly
        assert AuthService.verify_password(password, hashed)
        
        # Should not verify with wrong password
        assert not AuthService.verify_password("wrong_password", hashed)
    
    def test_create_access_token(self):
        """Test access token creation."""
        data = {"sub": "test_user"}
        token = AuthService.create_access_token(data)
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Should be able to decode token
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert payload["sub"] == "test_user"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        data = {"sub": "test_user"}
        token = AuthService.create_access_token(data)
        
        token_data = AuthService.verify_token(token)
        
        assert token_data is not None
        assert token_data.sub == "test_user"
        assert token_data.exp is not None
        assert token_data.iat is not None
    
    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        
        token_data = AuthService.verify_token(invalid_token)
        
        assert token_data is None
    
    def test_verify_token_malformed(self):
        """Test token verification with malformed token."""
        malformed_token = jwt.encode(
            {"sub": "test_user"}, 
            "wrong_secret", 
            algorithm=settings.algorithm
        )
        
        token_data = AuthService.verify_token(malformed_token)
        
        assert token_data is None
    
    def test_authenticate_demo_user_valid(self):
        """Test demo user authentication with valid credentials."""
        assert AuthService.authenticate_demo_user("admin", "admin123")
        assert AuthService.authenticate_demo_user("demo", "demo123")
        assert AuthService.authenticate_demo_user("user", "user123")
    
    def test_authenticate_demo_user_invalid(self):
        """Test demo user authentication with invalid credentials."""
        assert not AuthService.authenticate_demo_user("admin", "wrong_password")
        assert not AuthService.authenticate_demo_user("wrong_user", "admin123")
        assert not AuthService.authenticate_demo_user("", "")
        assert not AuthService.authenticate_demo_user("admin", "")