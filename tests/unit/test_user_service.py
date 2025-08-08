"""Unit tests for user service."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from user_management.models.user import User
from user_management.schemas.user import UserCreate, UserUpdate
from user_management.services.user import UserService


class TestUserService:
    """Test user service."""
    
    def test_create_user_success(self, db_session, sample_user_data):
        """Test successful user creation."""
        user_data = UserCreate(**sample_user_data)
        
        user = UserService.create_user(db_session, user_data)
        
        assert user.id is not None
        assert user.name == sample_user_data["name"]
        assert user.email == sample_user_data["email"]
        assert user.phone == sample_user_data["phone"]
        assert user.created_at is not None
        assert user.updated_at is not None
    
    def test_create_user_duplicate_email(self, db_session, sample_user_data):
        """Test user creation with duplicate email."""
        user_data = UserCreate(**sample_user_data)
        
        # Create first user
        UserService.create_user(db_session, user_data)
        
        # Try to create second user with same email
        with pytest.raises(ValueError, match="Email already exists"):
            UserService.create_user(db_session, user_data)
    
    def test_get_user_by_id_exists(self, db_session, create_test_user):
        """Test getting user by ID when user exists."""
        user = UserService.get_user_by_id(db_session, create_test_user.id)
        
        assert user is not None
        assert user.id == create_test_user.id
        assert user.email == create_test_user.email
    
    def test_get_user_by_id_not_exists(self, db_session):
        """Test getting user by ID when user doesn't exist."""
        user = UserService.get_user_by_id(db_session, 999)
        
        assert user is None
    
    def test_get_user_by_email_exists(self, db_session, create_test_user):
        """Test getting user by email when user exists."""
        user = UserService.get_user_by_email(db_session, create_test_user.email)
        
        assert user is not None
        assert user.id == create_test_user.id
        assert user.email == create_test_user.email
    
    def test_get_user_by_email_not_exists(self, db_session):
        """Test getting user by email when user doesn't exist."""
        user = UserService.get_user_by_email(db_session, "nonexistent@example.com")
        
        assert user is None
    
    def test_update_user_success(self, db_session, create_test_user, sample_user_update_data):
        """Test successful user update."""
        user_data = UserUpdate(**sample_user_update_data)
        
        updated_user = UserService.update_user(db_session, create_test_user.id, user_data)
        
        assert updated_user is not None
        assert updated_user.id == create_test_user.id
        assert updated_user.name == sample_user_update_data["name"]
        assert updated_user.email == sample_user_update_data["email"]
        assert updated_user.phone == sample_user_update_data["phone"]
    
    def test_update_user_partial(self, db_session, create_test_user):
        """Test partial user update."""
        user_data = UserUpdate(name="Updated Name")
        
        updated_user = UserService.update_user(db_session, create_test_user.id, user_data)
        
        assert updated_user is not None
        assert updated_user.name == "Updated Name"
        # Other fields should remain unchanged
        assert updated_user.email == create_test_user.email
        assert updated_user.phone == create_test_user.phone
    
    def test_update_user_not_exists(self, db_session, sample_user_update_data):
        """Test updating user that doesn't exist."""
        user_data = UserUpdate(**sample_user_update_data)
        
        updated_user = UserService.update_user(db_session, 999, user_data)
        
        assert updated_user is None
    
    def test_delete_user_success(self, db_session, create_test_user):
        """Test successful user deletion."""
        user_id = create_test_user.id
        
        success = UserService.delete_user(db_session, user_id)
        
        assert success is True
        
        # Verify user is deleted
        user = UserService.get_user_by_id(db_session, user_id)
        assert user is None
    
    def test_delete_user_not_exists(self, db_session):
        """Test deleting user that doesn't exist."""
        success = UserService.delete_user(db_session, 999)
        
        assert success is False
    
    def test_search_users_no_query(self, db_session, create_multiple_test_users):
        """Test searching users without query (list all)."""
        result = UserService.search_users(db_session)
        
        assert len(result.items) == 25
        assert result.total == 25
        assert result.page == 1
        assert result.pages == 1
        assert result.per_page == 50
        assert not result.has_next
        assert not result.has_prev
    
    def test_search_users_with_query(self, db_session, create_multiple_test_users):
        """Test searching users with query."""
        result = UserService.search_users(db_session, search="User 0")
        
        # Should find users with "User 0" in name (User 00-09)
        assert len(result.items) == 10
        assert result.total == 10
    
    def test_search_users_pagination(self, db_session, create_multiple_test_users):
        """Test user search with pagination."""
        # First page
        result = UserService.search_users(db_session, page=1, limit=10)
        
        assert len(result.items) == 10
        assert result.total == 25
        assert result.page == 1
        assert result.pages == 3
        assert result.per_page == 10
        assert result.has_next
        assert not result.has_prev
        
        # Second page
        result = UserService.search_users(db_session, page=2, limit=10)
        
        assert len(result.items) == 10
        assert result.page == 2
        assert result.has_next
        assert result.has_prev
        
        # Last page
        result = UserService.search_users(db_session, page=3, limit=10)
        
        assert len(result.items) == 5  # Remaining 5 users
        assert result.page == 3
        assert not result.has_next
        assert result.has_prev
    
    def test_search_users_sorting(self, db_session, create_multiple_test_users):
        """Test user search with sorting."""
        # Sort by name ascending
        result = UserService.search_users(
            db_session, 
            sort_by="name", 
            sort_order="asc", 
            limit=5
        )
        
        names = [user.name for user in result.items]
        assert names == sorted(names)
        
        # Sort by name descending
        result = UserService.search_users(
            db_session, 
            sort_by="name", 
            sort_order="desc", 
            limit=5
        )
        
        names = [user.name for user in result.items]
        assert names == sorted(names, reverse=True)
    
    def test_get_user_statistics(self, db_session, create_multiple_test_users):
        """Test getting user statistics."""
        stats = UserService.get_user_statistics(db_session)
        
        assert "total_users" in stats
        assert "users_created_today" in stats
        assert stats["total_users"] == 25
        assert stats["users_created_today"] == 25  # All created today in test