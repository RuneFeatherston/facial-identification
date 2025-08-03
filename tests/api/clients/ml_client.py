"""ML Service API Client."""

import os
import requests
from typing import Optional


class MLClient:
    """Client for interacting with the ML Service API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the ML client.
        
        Args:
            base_url: Base URL for the ml service. If None, uses ML_BASE_URL env var
                     or defaults to http://localhost:8000
        """
        self.base_url = base_url or os.getenv("ML_BASE_URL", "http://localhost:8000")
        self.session = requests.Session()
        self.session.timeout = 30
        
    def health(self):
        """Check the health status of the ml service."""
        pass
