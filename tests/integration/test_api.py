"""Integration tests for API endpoints."""

from __future__ import annotations

import pytest


class TestAuthAPI:
    """Test authentication API endpoints."""
    
    def test_login_success(self, client, login_data):
        """Test successful login."""
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrong_password"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Incorrect username or password"
    
    def test_get_demo_users(self, client):
        """Test getting demo users endpoint."""
        response = client.get("/api/v1/auth/demo-users")
        
        assert response.status_code == 200
        data = response.json()
        assert "demo_users" in data
        assert len(data["demo_users"]) == 3


class TestUserAPI:
    """Test user management API endpoints."""
    
    def test_create_user_success(self, client, auth_headers, sample_user_data):
        """Test successful user creation."""
        response = client.post(
            "/api/v1/users/",
            json=sample_user_data,
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User created successfully"
        assert data["data"]["name"] == sample_user_data["name"]
        assert data["data"]["email"] == sample_user_data["email"]
        assert data["data"]["phone"] == sample_user_data["phone"]
        assert "id" in data["data"]
        assert "created_at" in data["data"]
        assert "updated_at" in data["data"]
    
    def test_create_user_no_auth(self, client, sample_user_data):
        """Test user creation without authentication."""
        response = client.post("/api/v1/users/", json=sample_user_data)
        
        assert response.status_code == 401
    
    def test_create_user_invalid_data(self, client, auth_headers):
        """Test user creation with invalid data."""
        invalid_data = {
            "name": "",  # Empty name
            "email": "invalid-email",  # Invalid email
            "phone": "123"  # Invalid phone
        }
        
        response = client.post(
            "/api/v1/users/",
            json=invalid_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_list_users_no_auth(self, client, create_multiple_test_users):
        """Test listing users without authentication (public endpoint)."""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert data["total"] == 25
        assert len(data["items"]) == 25
    
    def test_list_users_with_pagination(self, client, create_multiple_test_users):
        """Test listing users with pagination."""
        response = client.get("/api/v1/users/?page=1&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["pages"] == 3
        assert data["has_next"] is True
        assert data["has_prev"] is False
    
    def test_list_users_with_search(self, client, create_multiple_test_users):
        """Test listing users with search."""
        response = client.get("/api/v1/users/?search=User 0")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 10  # User 00-09
        assert len(data["items"]) == 10
    
    def test_list_users_with_sorting(self, client, create_multiple_test_users):
        """Test listing users with sorting."""
        response = client.get("/api/v1/users/?sort_by=name&sort_order=asc&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        names = [user["name"] for user in data["items"]]
        assert names == sorted(names)
        
        # Test descending order
        response = client.get("/api/v1/users/?sort_by=name&sort_order=desc&limit=5")
        data = response.json()
        names = [user["name"] for user in data["items"]]
        assert names == sorted(names, reverse=True)
    
    def test_list_users_invalid_sort_field(self, client):
        """Test listing users with invalid sort field."""
        response = client.get("/api/v1/users/?sort_by=invalid_field")
        
        assert response.status_code == 400
        data = response.json()
        assert "Sort field must be one of" in data["detail"]
    
    def test_get_user_success(self, client, create_test_user):
        """Test getting user by ID."""
        response = client.get(f"/api/v1/users/{create_test_user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == create_test_user.id
        assert data["data"]["name"] == create_test_user.name
        assert data["data"]["email"] == create_test_user.email
    
    def test_get_user_not_found(self, client):
        """Test getting user that doesn't exist."""
        response = client.get("/api/v1/users/999")
        
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "User not found"
    
    def test_update_user_success(self, client, auth_headers, create_test_user, sample_user_update_data):
        """Test successful user update."""
        response = client.put(
            f"/api/v1/users/{create_test_user.id}",
            json=sample_user_update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User updated successfully"
        assert data["data"]["name"] == sample_user_update_data["name"]
        assert data["data"]["email"] == sample_user_update_data["email"]
    
    def test_update_user_partial(self, client, auth_headers, create_test_user):
        """Test partial user update."""
        partial_data = {"name": "Updated Name Only"}
        
        response = client.put(
            f"/api/v1/users/{create_test_user.id}",
            json=partial_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "Updated Name Only"
        # Email should remain unchanged
        assert data["data"]["email"] == create_test_user.email
    
    def test_update_user_no_auth(self, client, create_test_user, sample_user_update_data):
        """Test user update without authentication."""
        response = client.put(
            f"/api/v1/users/{create_test_user.id}",
            json=sample_user_update_data
        )
        
        assert response.status_code == 401
    
    def test_update_user_not_found(self, client, auth_headers, sample_user_update_data):
        """Test updating user that doesn't exist."""
        response = client.put(
            "/api/v1/users/999",
            json=sample_user_update_data,
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    def test_delete_user_success(self, client, auth_headers, create_test_user):
        """Test successful user deletion."""
        user_id = create_test_user.id
        
        response = client.delete(f"/api/v1/users/{user_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["message"] == "User deleted successfully"
        
        # Verify user is deleted
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 404
    
    def test_delete_user_no_auth(self, client, create_test_user):
        """Test user deletion without authentication."""
        response = client.delete(f"/api/v1/users/{create_test_user.id}")
        
        assert response.status_code == 401
    
    def test_delete_user_not_found(self, client, auth_headers):
        """Test deleting user that doesn't exist."""
        response = client.delete("/api/v1/users/999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_user_statistics(self, client, create_multiple_test_users):
        """Test getting user statistics."""
        response = client.get("/api/v1/users/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_users" in data["data"]
        assert "users_created_today" in data["data"]
        assert data["data"]["total_users"] == 25


class TestApplicationAPI:
    """Test application-level API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs_url" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_not_found_endpoint(self, client):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.options("/api/v1/users/")
        
        # Should have CORS headers
        assert "access-control-allow-origin" in response.headers
        assert "access-control-allow-methods" in response.headers
    
    def test_process_time_header(self, client):
        """Test that process time header is added."""
        response = client.get("/health")
        
        assert "x-process-time" in response.headers
        # Should be a float value
        process_time = float(response.headers["x-process-time"])
        assert process_time >= 0