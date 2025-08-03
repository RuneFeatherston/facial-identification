"""Mock WebSocket Server for Frontend Testing.

This server simulates the WebSocket API that the frontend expects for facial recognition.
It should be used for integration testing and development.
"""

import asyncio
import json
import logging
import random
import time
from base64 import b64encode
from typing import Dict, Any

import websockets
from websockets.server import WebSocketServerProtocol

logger = logging.getLogger(__name__)


class MockFacialRecognitionServer:
    """Mock WebSocket server that simulates facial recognition API."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.connected_clients: Dict[WebSocketServerProtocol, Dict] = {}
        
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle a new client connection."""
        client_info = {
            'connected_at': time.time(),
            'username': None,
            'frame_count': 0
        }
        self.connected_clients[websocket] = client_info
        
        logger.info(f"Client connected from {websocket.remote_address}")
        
        # Send welcome message
        await self.send_message(websocket, {
            'type': 'connected',
            'message': 'Connected to mock facial recognition server',
            'timestamp': time.time()
        })
        
        try:
            async for message in websocket:
                await self.handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client {websocket.remote_address} disconnected")
        finally:
            if websocket in self.connected_clients:
                del self.connected_clients[websocket]
    
    async def handle_message(self, websocket: WebSocketServerProtocol, message):
        """Handle incoming message from client."""
        try:
            # Check if message is binary (video frame) or JSON
            if isinstance(message, bytes):
                try:
                    # Try to parse as JSON first
                    data = json.loads(message.decode('utf-8'))
                    await self.handle_json_message(websocket, data)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    # It's binary video frame data
                    await self.handle_binary_frame(websocket, message)
            else:
                # It's a text message (JSON)
                data = json.loads(message)
                await self.handle_json_message(websocket, data)
                
        except json.JSONDecodeError:
            logger.error("Failed to parse message as JSON")
            await self.send_error(websocket, "Invalid message format")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_error(websocket, f"Server error: {str(e)}")
    
    async def handle_json_message(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle JSON messages."""
        message_type = data.get('type')
        client_info = self.connected_clients[websocket]
        
        logger.info(f"Received JSON message: {message_type}")
        
        if message_type == 'auth_challenge':
            await self.handle_auth_challenge(websocket, data)
        elif message_type == 'video_frame_metadata':
            await self.handle_frame_metadata(websocket, data)
        elif message_type == 'authenticate':
            # Legacy support
            await self.handle_auth_challenge(websocket, data)
        elif message_type == 'disconnect':
            logger.info("Client requesting disconnect")
            await websocket.close()
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def handle_binary_frame(self, websocket: WebSocketServerProtocol, frame_data: bytes):
        """Handle binary video frame data."""
        client_info = self.connected_clients[websocket]
        client_info['frame_count'] += 1
        
        logger.info(f"📹 Received binary video frame: {len(frame_data)} bytes (frame #{client_info['frame_count']})")
        
        # In a real implementation, this would process the frame for face recognition
        # For now, just acknowledge receipt
    
    async def handle_frame_metadata(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle video frame metadata."""
        frame_number = data.get('frameNumber', 0)
        width = data.get('width', 0)
        height = data.get('height', 0)
        size = data.get('size', 0)
        
        logger.info(f"📹 Frame #{frame_number} metadata: {width}x{height}, {size} bytes")
    
    async def handle_auth_challenge(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Handle authentication challenge."""
        username = data.get('username', 'unknown')
        client_info = self.connected_clients[websocket]
        client_info['username'] = username
        
        logger.info(f"🔍 Processing authentication for user: {username}")
        
        # Simulate processing delay
        await asyncio.sleep(2 + random.random() * 2)  # 2-4 seconds
        
        # Simulate random success/failure for testing (80% success rate)
        is_success = random.random() > 0.2
        
        if is_success:
            # Generate a mock JWT-like token
            token_payload = {
                'username': username,
                'exp': int(time.time()) + (24 * 60 * 60),  # 24 hours
                'iat': int(time.time())
            }
            token = f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{b64encode(json.dumps(token_payload).encode()).decode()}.mock_signature_{int(time.time())}"
            
            await self.send_message(websocket, {
                'type': 'auth_success',
                'token': token,
                'username': username,
                'timestamp': time.time()
            })
            
            logger.info(f"✅ Authentication successful for user: {username}")
        else:
            await self.send_message(websocket, {
                'type': 'auth_failed',
                'message': 'Facial recognition failed. Please try again.',
                'username': username,
                'timestamp': time.time()
            })
            
            logger.info(f"❌ Authentication failed for user: {username}")
    
    async def send_message(self, websocket: WebSocketServerProtocol, data: Dict[str, Any]):
        """Send JSON message to client."""
        try:
            await websocket.send(json.dumps(data))
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Tried to send message to closed connection")
    
    async def send_error(self, websocket: WebSocketServerProtocol, message: str):
        """Send error message to client."""
        await self.send_message(websocket, {
            'type': 'error',
            'message': message,
            'timestamp': time.time()
        })
    
    async def start(self):
        """Start the WebSocket server."""
        logger.info(f"🚀 Starting mock WebSocket server on ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"✅ Mock server running on ws://{self.host}:{self.port}")
            # Keep server running
            await asyncio.Future()  # Run forever


def main():
    """Run the mock server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Mock WebSocket server for facial recognition")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and start server
    server = MockFacialRecognitionServer(host=args.host, port=args.port)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")


if __name__ == "__main__":
    main()
