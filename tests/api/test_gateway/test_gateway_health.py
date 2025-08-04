"""Gateway Service Health Endpoint Tests."""

import pytest
import requests


class TestGatewayHealth:
    """Test cases for Gateway service health endpoint."""

    def test_health_endpoint_success(self, gateway_client):
        """Test health endpoint returns healthy status."""
        response = gateway_client.health()
        
        assert response["status"] == "healthy"
        assert response["service"] == "gateway-service"

    def test_health_endpoint_direct_request(self, gateway_server):
        """Test health endpoint with direct HTTP request."""
        response = requests.get("http://localhost:18080/health")
        
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "gateway-service"

    def test_health_endpoint_cors_headers(self, gateway_server):
        """Test CORS headers are properly set."""
        response = requests.options("http://localhost:18080/health")

        assert response.status_code == 200
        assert response.headers.get("Access-Control-Allow-Origin") == "*"
        assert "GET" in response.headers.get("Access-Control-Allow-Methods", "")
        assert "Content-Type" in response.headers.get("Access-Control-Allow-Headers", "")
