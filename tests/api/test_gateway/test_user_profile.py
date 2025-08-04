"""Gateway Service User Profile API Tests."""

import pytest
import requests


class TestGatewayUserProfile:
    """Test cases for Gateway service user profile API."""

    def test_get_user_profile_success(self, gateway_client, test_user_data):
        """Test successful user profile retrieval."""
        profile = gateway_client.get_user_profile(test_user_data["username"])
        
        assert "user" in profile
        assert "faceEntries" in profile
        
        user = profile["user"]
        assert user["username"] == test_user_data["username"]
        assert "id" in user
        assert "createdAt" in user
        assert "updatedAt" in user

    def test_get_user_profile_missing_username(self, gateway_server):
        """Test user profile request without username parameter."""
        response = requests.get("http://localhost:18080/api/user/profile")
        
        assert response.status_code == 400
        assert "username" in response.text.lower()

    def test_get_user_profile_nonexistent_user(self, gateway_client):
        """Test user profile request for nonexistent user."""
        with pytest.raises(requests.exceptions.HTTPError) as exc_info:
            gateway_client.get_user_profile("nonexistent_user")
        
        assert exc_info.value.response.status_code == 404

    def test_user_profile_with_face_entries(self, gateway_client):
        """Test user profile includes face entries."""
        # Use a test user that should have face entries
        profile = gateway_client.get_user_profile("testuser")
        
        face_entries = profile["faceEntries"]
        assert isinstance(face_entries, list)
        
        if len(face_entries) > 0:
            entry = face_entries[0]
            assert "id" in entry
            assert "quality" in entry
            assert entry["quality"] in ["high", "medium", "low"]
            assert "isActive" in entry
            assert "createdAt" in entry

    def test_user_profile_cors_headers(self, gateway_server):
        """Test CORS headers on user profile endpoint."""
        response = requests.options("http://localhost:18080/api/user/profile")

        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") == "*"

    def test_user_profile_response_format(self, gateway_client, test_user_data):
        """Test user profile response has correct format."""
        profile = gateway_client.get_user_profile(test_user_data["username"])
        
        # Validate top-level structure
        assert isinstance(profile, dict)
        assert "user" in profile
        assert "faceEntries" in profile
        
        # Validate user structure
        user = profile["user"]
        required_user_fields = ["id", "username", "fullName", "email", "joinDate", "createdAt", "updatedAt"]
        for field in required_user_fields:
            assert field in user, f"Missing required user field: {field}"
        
        # Validate face entries structure
        face_entries = profile["faceEntries"]
        assert isinstance(face_entries, list)
        
        for entry in face_entries:
            required_entry_fields = ["id", "quality", "isActive", "createdAt"]
            for field in required_entry_fields:
                assert field in entry, f"Missing required face entry field: {field}"
