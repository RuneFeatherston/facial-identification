"""Mock ML Service for API Contract Testing.

This mock server simulates the ML service for testing the gateway service.
It responds to the same HTTP endpoints as the real ML service.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import base64


class MockMLServiceHandler(BaseHTTPRequestHandler):
    """Handle ML service API requests with mock responses."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "healthy", "service": "ml-service"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(body.decode())
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return
        
        if self.path == "/extract-embedding":
            self._handle_extract_embedding(request_data)
        elif self.path == "/authenticate":
            self._handle_authenticate(request_data)
        else:
            self.send_response(404)
            self.end_headers()
    
    def _handle_extract_embedding(self, request_data):
        """Mock face embedding extraction."""
        username = request_data.get("username", "unknown")
        image_data = request_data.get("imageData")
        
        if not image_data:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"success": False, "error": "No image data provided"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Simulate processing delay
        time.sleep(0.1)
        
        # Mock successful embedding extraction
        mock_embedding = base64.b64encode(f"mock-embedding-{username}".encode()).decode()
        
        response = {
            "success": True,
            "embedding": mock_embedding,
            "quality": "high",
            "confidence": 0.95
        }
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def _handle_authenticate(self, request_data):
        """Mock face authentication."""
        username = request_data.get("username", "unknown")
        image_data = request_data.get("imageData")
        known_embeddings = request_data.get("knownEmbeddings", [])
        
        if not image_data:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"success": False, "error": "No image data provided"}
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Simulate processing delay
        time.sleep(0.2)
        
        # Mock authentication logic - succeed if we have known embeddings
        success = len(known_embeddings) > 0
        confidence = 0.87 if success else 0.23
        
        response = {
            "success": success,
            "confidence": confidence
        }
        
        if not success:
            response["error"] = "Face not recognized"
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Suppress request logging during tests."""
        pass


class MockMLService:
    """Mock ML service server for testing."""
    
    def __init__(self, port=8081):
        self.port = port
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the mock ML service."""
        self.server = HTTPServer(("localhost", self.port), MockMLServiceHandler)
        self.thread = Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()
        
        # Wait a bit for server to start
        time.sleep(0.1)
    
    def stop(self):
        """Stop the mock ML service."""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)


if __name__ == "__main__":
    # For standalone testing
    mock_service = MockMLService()
    mock_service.start()
    print("Mock ML service running on http://localhost:8081")
    try:
        input("Press Enter to stop...\n")
    finally:
        mock_service.stop()
