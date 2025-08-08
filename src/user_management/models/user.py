"""User model."""

from __future__ import annotations

import re
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.ext.hybrid import hybrid_property

from user_management.database.base import Base

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    @hybrid_property
    def name_normalized(self) -> str:
        """Normalized name for case-insensitive search."""
        return self.name.lower() if self.name else ""
    
    @hybrid_property
    def email_normalized(self) -> str:
        """Normalized email for case-insensitive search."""
        return self.email.lower() if self.email else ""
    
    @hybrid_property
    def phone_normalized(self) -> str:
        """Normalized phone for search (digits only)."""
        if not self.phone:
            return ""
        return re.sub(r'[^\d]', '', self.phone)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}')>"
    
    @classmethod
    def search(
        cls,
        db: Session,
        query: str,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[User], int]:
        """Search users with pagination and sorting."""
        search_query = db.query(cls)
        
        # Apply search filter if query provided
        if query:
            search_term = f"%{query.lower()}%"
            search_query = search_query.filter(
                cls.name_normalized.like(search_term) |
                cls.email_normalized.like(search_term) |
                cls.phone_normalized.like(search_term)
            )
        
        # Get total count before applying pagination
        total_count = search_query.count()
        
        # Apply sorting
        sort_column = getattr(cls, sort_by, cls.created_at)
        if sort_order.lower() == "desc":
            sort_column = sort_column.desc()
        else:
            sort_column = sort_column.asc()
        
        search_query = search_query.order_by(sort_column)
        
        # Apply pagination
        users = search_query.offset(offset).limit(limit).all()
        
        return users, total_count