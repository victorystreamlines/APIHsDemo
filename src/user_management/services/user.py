"""User service."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from user_management.models.user import User
from user_management.schemas.common import PaginationResponse
from user_management.schemas.user import UserCreate, UserUpdate

if TYPE_CHECKING:
    from user_management.schemas.user import User as UserSchema


class UserService:
    """User service for business logic."""
    
    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        """Create a new user."""
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            db.rollback()
            if "UNIQUE constraint failed: users.email" in str(e):
                raise ValueError("Email already exists") from e
            raise e
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User | None:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User | None:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User | None:
        """Update user."""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return None
        
        # Update only provided fields
        update_data = user_data.dict(exclude_unset=True)
        
        try:
            for field, value in update_data.items():
                setattr(db_user, field, value)
            
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError as e:
            db.rollback()
            if "UNIQUE constraint failed: users.email" in str(e):
                raise ValueError("Email already exists") from e
            raise e
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete user."""
        db_user = UserService.get_user_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True
    
    @staticmethod
    def search_users(
        db: Session,
        search: str = "",
        page: int = 1,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> PaginationResponse[UserSchema]:
        """Search users with pagination and sorting."""
        offset = (page - 1) * limit
        
        # Use the model's search method
        users, total_count = User.search(
            db=db,
            query=search,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        # Calculate pagination info
        total_pages = math.ceil(total_count / limit) if total_count > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        return PaginationResponse[UserSchema](
            items=users,
            total=total_count,
            page=page,
            pages=total_pages,
            per_page=limit,
            has_next=has_next,
            has_prev=has_prev,
        )
    
    @staticmethod
    def get_user_statistics(db: Session) -> dict:
        """Get user statistics."""
        total_users = db.query(User).count()
        
        # Get users created today
        from datetime import datetime, date
        today = date.today()
        users_today = db.query(User).filter(
            User.created_at >= datetime.combine(today, datetime.min.time())
        ).count()
        
        return {
            "total_users": total_users,
            "users_created_today": users_today,
        }