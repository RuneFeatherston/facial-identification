"""Gateway Service API Client."""

import os
import requests
from typing import Dict, Any, Optional


class GatewayClient:
    """Client for interacting with the Gateway Service API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the Gateway client.
        
        Args:
            base_url: Base URL for the gateway service. If None, uses GATEWAY_BASE_URL env var
                     or defaults to http://localhost:8080
        """
        self.base_url = base_url or os.getenv("GATEWAY_BASE_URL", "http://localhost:8080")
        self.session = requests.Session()
        self.session.timeout = 30
        
    def health(self):
        """Check the health status of the gateway service."""
        pass
