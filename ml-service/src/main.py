#!/usr/bin/env python3
"""
ML Service - ML Inference Service

This service provides machine learning inference capabilities.
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            response = {"status": "healthy", "service": "ml-service"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Override to reduce log noise in tests"""
        pass


def main():
    """Start the ML service"""
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, HealthHandler)
    print("ML service starting on :8000")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
