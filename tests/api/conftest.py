"""pytest configuration and shared fixtures for API tests."""

import pytest
import os
from clients.gateway_client import GatewayClient
from clients.ml_client import MLClient
from clients.websocket_client import WebSocketClient


@pytest.fixture
def gateway_client():
    """Fixture providing a configured Gateway API client."""
    return GatewayClient()


@pytest.fixture
def ml_client():
    """Fixture providing a configured ML API client."""
    return MLClient()


@pytest.fixture
def gateway_base_url():
    """Fixture providing the gateway base URL."""
    return os.getenv("GATEWAY_BASE_URL", "http://localhost:8080")


@pytest.fixture
def ml_base_url():
    """Fixture providing the ml base URL."""
    return os.getenv("ML_BASE_URL", "http://localhost:8000")
