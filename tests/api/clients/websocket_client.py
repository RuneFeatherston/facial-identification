"""WebSocket API Client for testing facial recognition endpoint."""

import asyncio
import json
import logging
import os
from typing import Dict, Any, Optional, Callable, List
import websockets
from websockets.client import WebSocketClientProtocol

logger = logging.getLogger(__name__)


class WebSocketClient:
    """Client for testing WebSocket facial recognition API."""

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the WebSocket client.
        
        Args:
            base_url: Base WebSocket URL. If None, uses WEBSOCKET_BASE_URL env var
                     or defaults to ws://localhost:8080
        """
        self.base_url = base_url or os.getenv("WEBSOCKET_BASE_URL", "ws://localhost:8080")
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.messages: List[Dict[str, Any]] = []
        self.connection_timeout = 10
        self.message_timeout = 30

    async def connect(self) -> bool:
        """Connect to the WebSocket server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.websocket = await asyncio.wait_for(
                websockets.connect(self.base_url),
                timeout=self.connection_timeout
            )
            logger.info(f"Connected to WebSocket: {self.base_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            return False

    async def disconnect(self):
        """Disconnect from the WebSocket server."""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
            logger.info("Disconnected from WebSocket")

    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send a JSON message to the server.
        
        Args:
            message: Dictionary to send as JSON
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.websocket:
            logger.error("WebSocket not connected")
            return False
            
        try:
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Sent message: {message.get('type', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    async def send_binary_data(self, data: bytes) -> bool:
        """Send binary data to the server.
        
        Args:
            data: Binary data to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.websocket:
            logger.error("WebSocket not connected")
            return False
            
        try:
            await self.websocket.send(data)
            logger.debug(f"Sent binary data: {len(data)} bytes")
            return True
        except Exception as e:
            logger.error(f"Failed to send binary data: {e}")
            return False

    async def receive_message(self, timeout: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Receive a single message from the server.
        
        Args:
            timeout: Timeout in seconds, uses default if None
            
        Returns:
            Parsed message dictionary or None if timeout/error
        """
        if not self.websocket:
            logger.error("WebSocket not connected")
            return None
            
        timeout = timeout or self.message_timeout
        
        try:
            message = await asyncio.wait_for(
                self.websocket.recv(),
                timeout=timeout
            )
            
            if isinstance(message, str):
                parsed = json.loads(message)
                self.messages.append(parsed)
                logger.debug(f"Received message: {parsed.get('type', 'unknown')}")
                return parsed
            else:
                logger.warning("Received non-text message (binary data)")
                return None
                
        except asyncio.TimeoutError:
            logger.warning(f"No message received within {timeout} seconds")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message as JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return None

    async def wait_for_message_type(self, message_type: str, timeout: float = 10.0) -> Optional[Dict[str, Any]]:
        """Wait for a specific message type.
        
        Args:
            message_type: The message type to wait for
            timeout: Maximum time to wait
            
        Returns:
            The message of the specified type, or None if timeout
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            message = await self.receive_message(timeout=1.0)
            if message and message.get('type') == message_type:
                return message
                
        logger.warning(f"Timeout waiting for message type: {message_type}")
        return None

    def get_messages_by_type(self, message_type: str) -> List[Dict[str, Any]]:
        """Get all received messages of a specific type.
        
        Args:
            message_type: The message type to filter by
            
        Returns:
            List of messages matching the type
        """
        return [msg for msg in self.messages if msg.get('type') == message_type]

    def clear_messages(self):
        """Clear the message history."""
        self.messages.clear()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
