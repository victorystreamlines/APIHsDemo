"""Common schemas."""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=50, ge=1, le=100, description="Items per page")
    search: str = Field(default="", description="Search query")
    sort_by: str = Field(default="created_at", description="Sort field")
    sort_order: str = Field(default="desc", regex="^(asc|desc)$", description="Sort order")


class PaginationResponse(BaseModel, Generic[T]):
    """Paginated response."""
    
    items: list[T]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    pages: int = Field(description="Total number of pages")
    per_page: int = Field(description="Items per page")
    has_next: bool = Field(description="Has next page")
    has_prev: bool = Field(description="Has previous page")


class ErrorResponse(BaseModel):
    """Error response."""
    
    success: bool = False
    message: str
    detail: str | None = None


class SuccessResponse(BaseModel, Generic[T]):
    """Success response."""
    
    success: bool = True
    message: str
    data: T | None = None