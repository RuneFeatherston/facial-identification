"""Gateway Service API Client."""

import json
import os
import requests
import websocket
from typing import Dict, Any, Optional, Callable
from threading import Thread
import time


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
        
    def health(self) -> Dict[str, Any]:
        """Check the health status of the gateway service."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get user profile by username."""
        response = self.session.get(
            f"{self.base_url}/api/user/profile",
            params={"username": username}
        )
        response.raise_for_status()
        return response.json()
    
    def create_websocket_connection(self) -> 'WebSocketTestClient':
        """Create a WebSocket connection for testing."""
        ws_url = self.base_url.replace("http://", "ws://") + "/ws"
        return WebSocketTestClient(ws_url)


class WebSocketTestClient:
    """WebSocket client for testing gateway WebSocket functionality."""
    
    def __init__(self, url: str):
        """Initialize WebSocket test client."""
        self.url = url
        self.ws = None
        self.received_messages = []
        self.message_handlers = {}
        self._running = False
        self._thread = None
    
    def connect(self):
        """Connect to WebSocket server."""
        self.ws = websocket.WebSocket()
        self.ws.connect(self.url)
        self._running = True
        self._thread = Thread(target=self._message_loop)
        self._thread.daemon = True
        self._thread.start()
        
        # Wait for connection to establish and initial message
        time.sleep(0.5)
    
    def disconnect(self):
        """Disconnect from WebSocket server."""
        self._running = False
        if self.ws:
            self.ws.close()
        if self._thread:
            self._thread.join(timeout=1)
    
    def send_json(self, data: Dict[str, Any]):
        """Send JSON message to server."""
        if self.ws:
            self.ws.send(json.dumps(data))
    
    def send_binary(self, data: bytes):
        """Send binary data to server."""
        if self.ws:
            self.ws.send_binary(data)
    
    def wait_for_message(self, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Wait for the next JSON message."""
        start_time = time.time()
        initial_count = len(self.received_messages)
        
        while time.time() - start_time < timeout:
            if len(self.received_messages) > initial_count:
                return self.received_messages[-1]
            time.sleep(0.01)
        
        # If no new messages but we have messages, return the last one
        if self.received_messages:
            return self.received_messages[-1]
            
        return None
    
    def wait_for_message_type(self, message_type: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        """Wait for a message of a specific type."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            # Check if we have any messages of this type
            matching_messages = self.get_messages_by_type(message_type)
            if matching_messages:
                return matching_messages[-1]
            time.sleep(0.01)
        
        return None
    
    def get_messages_by_type(self, message_type: str) -> list:
        """Get all received messages of a specific type."""
        return [msg for msg in self.received_messages if msg.get("type") == message_type]
    
    def _message_loop(self):
        """Background thread to receive messages."""
        while self._running and self.ws:
            try:
                # Set a timeout for recv to avoid blocking indefinitely
                self.ws.settimeout(0.1)
                message = self.ws.recv()
                if message:
                    try:
                        parsed = json.loads(message)
                        self.received_messages.append(parsed)
                    except json.JSONDecodeError:
                        # Handle non-JSON messages if needed
                        pass
            except websocket.WebSocketTimeoutException:
                # Continue loop on timeout
                continue
            except Exception:
                break
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
