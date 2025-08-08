"""User management API routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from user_management.core.security import get_current_user, get_optional_user
from user_management.database.base import get_db
from user_management.schemas.common import PaginationResponse, SuccessResponse
from user_management.schemas.user import User, UserCreate, UserSearchParams, UserUpdate
from user_management.services.user import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=SuccessResponse[User], status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> SuccessResponse[User]:
    """Create a new user (requires authentication)."""
    try:
        db_user = UserService.create_user(db, user_data)
        return SuccessResponse[User](
            message="User created successfully",
            data=User.from_orm(db_user),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.get("/", response_model=PaginationResponse[User])
async def list_users(
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    search: str = Query(default="", description="Search query"),
    sort_by: str = Query(default="created_at", description="Sort field"),
    sort_order: str = Query(default="desc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db),
    current_user: str | None = Depends(get_optional_user),
) -> PaginationResponse[User]:
    """List users with pagination, search, and sorting.
    
    Public endpoint with optional authentication for enhanced features.
    """
    # Validate sort_by field
    allowed_fields = ["id", "name", "email", "phone", "created_at", "updated_at"]
    if sort_by not in allowed_fields:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sort field must be one of: {', '.join(allowed_fields)}",
        )
    
    result = UserService.search_users(
        db=db,
        search=search,
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    # Convert to schema
    return PaginationResponse[User](
        items=[User.from_orm(user) for user in result.items],
        total=result.total,
        page=result.page,
        pages=result.pages,
        per_page=result.per_page,
        has_next=result.has_next,
        has_prev=result.has_prev,
    )


@router.get("/{user_id}", response_model=SuccessResponse[User])
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str | None = Depends(get_optional_user),
) -> SuccessResponse[User]:
    """Get user by ID.
    
    Public endpoint with optional authentication.
    """
    db_user = UserService.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return SuccessResponse[User](
        message="User retrieved successfully",
        data=User.from_orm(db_user),
    )


@router.put("/{user_id}", response_model=SuccessResponse[User])
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> SuccessResponse[User]:
    """Update user (requires authentication)."""
    try:
        db_user = UserService.update_user(db, user_id, user_data)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        
        return SuccessResponse[User](
            message="User updated successfully",
            data=User.from_orm(db_user),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.delete("/{user_id}", response_model=SuccessResponse[None])
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> SuccessResponse[None]:
    """Delete user (requires authentication)."""
    success = UserService.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return SuccessResponse[None](
        message="User deleted successfully",
    )


@router.get("/stats/summary")
async def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: str | None = Depends(get_optional_user),
) -> dict:
    """Get user statistics.
    
    Public endpoint with optional authentication.
    """
    stats = UserService.get_user_statistics(db)
    return {
        "success": True,
        "message": "Statistics retrieved successfully",
        "data": stats,
    }