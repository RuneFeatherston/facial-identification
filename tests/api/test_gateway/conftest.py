"""Test fixtures for Gateway API contract testing."""

import os
import subprocess
import time
import pytest
import signal
import psutil
from typing import Generator

from ..mocks.mock_ml_service import MockMLService
from ..mocks.mock_database import reset_mock_database
from ..clients.gateway_client import GatewayClient


@pytest.fixture(scope="session")
def mock_ml_service() -> Generator[MockMLService, None, None]:
    """Start mock ML service for the test session."""
    service = MockMLService(port=8081)
    service.start()
    
    # Wait for service to be ready
    time.sleep(0.5)
    
    yield service
    
    service.stop()


@pytest.fixture(scope="session")
def mock_database():
    """Provide mock database for testing."""
    # Reset database for clean state
    db = reset_mock_database()
    yield db
    db.close()


@pytest.fixture(scope="session") 
def gateway_server(mock_ml_service, mock_database) -> Generator[subprocess.Popen, None, None]:
    """Start real Go gateway service with mocked dependencies."""
    
    # Set environment variables to point to mocks
    env = os.environ.copy()
    env.update({
        "TEST_MODE": "true",  # Enable test mode to skip database
        "SERVER_PORT": "18080",  # Use different port for testing
        "ML_SERVICE_URL": "http://localhost:8081",
        "JWT_SECRET": "test-secret-key"
    })    # Change to gateway-service directory and build/run
    gateway_dir = os.path.join(os.path.dirname(__file__), "..", "..", "..", "gateway-service")
    
    # Build the gateway service
    build_process = subprocess.run(
        ["go", "build", "-o", "gateway-test", "./cmd/main.go"],
        cwd=gateway_dir,
        capture_output=True,
        text=True
    )
    
    if build_process.returncode != 0:
        pytest.fail(f"Failed to build gateway service: {build_process.stderr}")
    
    # Start the gateway service
    process = subprocess.Popen(
        ["./gateway-test"],
        cwd=gateway_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for service to start
    time.sleep(2)
    
    # Check if process is still running
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        pytest.fail(f"Gateway service failed to start. STDOUT: {stdout}, STDERR: {stderr}")
    
    yield process
    
    # Cleanup: kill the process and any children
    try:
        parent = psutil.Process(process.pid)
        for child in parent.children(recursive=True):
            child.kill()
        parent.kill()
    except psutil.NoSuchProcess:
        pass
    
    # Clean up binary
    try:
        os.remove(os.path.join(gateway_dir, "gateway-test"))
    except OSError:
        pass


@pytest.fixture
def gateway_client(gateway_server) -> GatewayClient:
    """Provide gateway client connected to test server."""
    return GatewayClient("http://localhost:18080")


@pytest.fixture
def test_user_data():
    """Provide test user data for API tests."""
    return {
        "username": "testuser",
        "full_name": "Test User", 
        "email": "test@example.com"
    }


@pytest.fixture
def mock_jpeg_frame():
    """Provide mock JPEG frame data for WebSocket testing."""
    # Mock JPEG header + some data
    return b'\xff\xd8\xff\xe0\x00\x10JFIF' + b'mock-frame-data' * 100
