"""Test configuration and shared fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from user_management.core.config import settings
from user_management.database.base import Base, get_db
from user_management.main import app
from user_management.models.user import User
from user_management.services.auth import AuthService

# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override."""
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
    }


@pytest.fixture
def sample_user_update_data():
    """Sample user update data for testing."""
    return {
        "name": "Jane Smith",
        "email": "jane.smith@example.com", 
        "phone": "+0987654321",
    }


@pytest.fixture
def auth_headers():
    """Get authentication headers for testing."""
    # Create a test token
    token = AuthService.create_access_token(data={"sub": "test_user"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def create_test_user(db_session, sample_user_data):
    """Create a test user in the database."""
    user = User(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def create_multiple_test_users(db_session):
    """Create multiple test users for pagination testing."""
    users = []
    for i in range(25):
        user = User(
            name=f"User {i:02d}",
            email=f"user{i:02d}@example.com",
            phone=f"+123456789{i:02d}",
        )
        db_session.add(user)
        users.append(user)
    
    db_session.commit()
    for user in users:
        db_session.refresh(user)
    
    return users


@pytest.fixture
def login_data():
    """Sample login data for testing."""
    return {"username": "admin", "password": "admin123"}