"""Gateway Service WebSocket API Tests."""

import pytest
import json
import time


class TestGatewayWebSocket:
    """Test cases for Gateway service WebSocket functionality."""

    def test_websocket_connection(self, gateway_client):
        """Test WebSocket connection establishment."""
        with gateway_client.create_websocket_connection() as ws_client:
            # Should receive connected message
            connected_msg = ws_client.wait_for_message(timeout=3.0)
            
            assert connected_msg is not None
            assert connected_msg["type"] == "connected"
            assert "message" in connected_msg
            assert "timestamp" in connected_msg

    def test_auth_challenge_flow(self, gateway_client, test_user_data):
        """Test authentication challenge flow."""
        with gateway_client.create_websocket_connection() as ws_client:
            # Wait for connected message
            connected_msg = ws_client.wait_for_message_type("connected", timeout=3.0)
            assert connected_msg["type"] == "connected"
            
            # Send auth challenge
            auth_challenge = {
                "type": "auth_challenge",
                "username": test_user_data["username"],
                "timestamp": int(time.time() * 1000)
            }
            ws_client.send_json(auth_challenge)
            
            # Should receive video frame request first (new flow)
            frame_request = ws_client.wait_for_message(timeout=10.0)
            
            assert frame_request is not None
            # The gateway now requests a video frame for authentication
            assert frame_request["type"] == "video_frame_metadata"
            assert frame_request["username"] == test_user_data["username"]
            assert "message" in frame_request
            assert "timestamp" in frame_request
            
            # For test purposes, we can send a dummy binary frame
            # In real usage, this would be actual video frame data
            dummy_frame_data = b'\xff\xd8\xff\xe0\x00\x10JFIF'  # JPEG header
            ws_client.send_binary(dummy_frame_data)
            
            # Now should receive auth response after frame processing
            auth_response = ws_client.wait_for_message(timeout=15.0)
            
            assert auth_response is not None
            assert auth_response["type"] in ["auth_success", "auth_failed"]
            assert auth_response["username"] == test_user_data["username"]
            assert "timestamp" in auth_response
            
            if auth_response["type"] == "auth_success":
                assert "token" in auth_response
                assert len(auth_response["token"]) > 0
            else:
                assert "message" in auth_response

    def test_video_frame_metadata(self, gateway_client):
        """Test video frame metadata handling."""
        with gateway_client.create_websocket_connection() as ws_client:
            # Wait for connected message
            ws_client.wait_for_message(timeout=2.0)
            
            # Send video frame metadata
            frame_metadata = {
                "type": "video_frame_metadata",
                "username": "testuser",
                "frameNumber": 42,
                "timestamp": int(time.time() * 1000),
                "width": 640,
                "height": 480,
                "format": "jpeg",
                "size": 15248
            }
            ws_client.send_json(frame_metadata)
            
            # The server should process this without error
            # (no response expected for metadata)
            time.sleep(0.5)

    def test_binary_frame_data(self, gateway_client, mock_jpeg_frame):
        """Test binary video frame data handling."""
        with gateway_client.create_websocket_connection() as ws_client:
            # Wait for connected message
            ws_client.wait_for_message(timeout=2.0)
            
            # Send binary frame data
            ws_client.send_binary(mock_jpeg_frame)
            
            # The server should process this without error
            # (processing happens in background)
            time.sleep(0.5)

    def test_legacy_authenticate_message(self, gateway_client):
        """Test legacy authenticate message support."""
        with gateway_client.create_websocket_connection() as ws_client:
            # Wait for connected message
            ws_client.wait_for_message(timeout=2.0)
            
            # Send legacy authenticate message
            legacy_auth = {
                "type": "authenticate",
                "username": "testuser",
                "timestamp": "2024-01-01T12:00:00Z"
            }
            ws_client.send_json(legacy_auth)
            
            # Should receive video frame request first (new flow)
            frame_request = ws_client.wait_for_message(timeout=10.0)
            
            assert frame_request is not None
            # Legacy auth should also trigger video frame request
            assert frame_request["type"] == "video_frame_metadata"
            assert frame_request["username"] == "testuser"
            assert "message" in frame_request
            
            # Send dummy frame data for testing
            dummy_frame_data = b'\xff\xd8\xff\xe0\x00\x10JFIF'  # JPEG header
            ws_client.send_binary(dummy_frame_data)
            
            # Should receive auth response after frame processing
            auth_response = ws_client.wait_for_message(timeout=15.0)
            
            assert auth_response is not None
            assert auth_response["type"] in ["auth_success", "auth_failed"]

    def test_invalid_message_format(self, gateway_client):
        """Test handling of invalid message formats."""
        with gateway_client.create_websocket_connection() as ws_client:
            # Wait for connected message
            ws_client.wait_for_message(timeout=2.0)
            
            # Send invalid JSON
            ws_client.ws.send("invalid-json")
            
            # Should receive error message
            error_response = ws_client.wait_for_message(timeout=2.0)
            
            # The server might send an error or just log it
            # Either way, connection should remain stable
            time.sleep(0.5)

    def test_missing_message_type(self, gateway_client):
        """Test handling of messages without type field."""
        with gateway_client.create_websocket_connection() as ws_client:
            # Wait for connected message
            ws_client.wait_for_message(timeout=2.0)
            
            # Send message without type
            invalid_msg = {"username": "testuser"}
            ws_client.send_json(invalid_msg)
            
            # Should receive error message
            error_response = ws_client.wait_for_message(timeout=2.0)
            
            if error_response:
                assert error_response["type"] == "auth_failed"
                assert "type" in error_response.get("message", "")

    def test_unknown_message_type(self, gateway_client):
        """Test handling of unknown message types."""
        with gateway_client.create_websocket_connection() as ws_client:
            # Wait for connected message
            ws_client.wait_for_message(timeout=2.0)
            
            # Send unknown message type
            unknown_msg = {
                "type": "unknown_message_type",
                "data": "some data"
            }
            ws_client.send_json(unknown_msg)
            
            # Should receive error message
            error_response = ws_client.wait_for_message(timeout=2.0)
            
            if error_response:
                assert error_response["type"] == "auth_failed"
                assert "unknown_message_type" in error_response.get("message", "")
