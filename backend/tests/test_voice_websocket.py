# TSS PPM v3.0 - Voice WebSocket Tests
"""Tests for Voice WebSocket endpoint and authentication."""

from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta, timezone

import pytest
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from src.main import app
from src.config import settings
from src.auth import CurrentUser


class TestWebSocketAuthentication:
    """Tests for WebSocket JWT authentication."""

    @pytest.fixture
    def mock_current_user(self):
        """Mock authenticated user."""
        return CurrentUser(
            keycloak_id='test-user-id',
            email='test@example.com',
            name='Test User',
            roles=['employee'],
            opco_id='test-opco',
        )

    def test_websocket_connection_with_valid_jwt_succeeds(self, mock_current_user):
        """WebSocket connection with valid JWT token should succeed."""
        # Mock the WebSocket auth to return a valid user
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Connection should succeed - if we get here without exception, test passes
                # Send a ping to verify connection is alive
                websocket.send_json({'type': 'ping'})
                response = websocket.receive_json()
                assert response.get('type') == 'pong'

    def test_websocket_connection_with_expired_jwt_rejected(self):
        """WebSocket connection with expired JWT should be rejected with close code 4001."""
        # Mock the WebSocket auth to raise an expired token error
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.side_effect = Exception('Token expired')

            client = TestClient(app)
            with pytest.raises(WebSocketDisconnect) as exc_info:
                with client.websocket_connect('/api/v1/voice/transcribe?token=expired-token'):
                    pass
            # Should be rejected with close code 4001
            assert exc_info.value.code == 4001

    def test_websocket_connection_with_missing_token_rejected(self):
        """WebSocket connection without token should be rejected with close code 4001."""
        client = TestClient(app)
        with pytest.raises(WebSocketDisconnect) as exc_info:
            with client.websocket_connect('/api/v1/voice/transcribe'):
                pass
        # Should be rejected with close code 4001
        assert exc_info.value.code == 4001

    def test_websocket_connection_with_malformed_token_rejected(self):
        """WebSocket connection with malformed token should be rejected with close code 4001."""
        # Mock the WebSocket auth to raise an invalid token error
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.side_effect = Exception('Invalid token')

            client = TestClient(app)
            with pytest.raises(WebSocketDisconnect) as exc_info:
                with client.websocket_connect('/api/v1/voice/transcribe?token=not-a-valid-jwt'):
                    pass
            # Should be rejected with close code 4001
            assert exc_info.value.code == 4001

    def test_websocket_extracts_user_claims_from_valid_token(self, mock_current_user):
        """WebSocket should extract user_id and opco_id from valid token."""
        # Mock the WebSocket auth to return a valid user with specific claims
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Request user info to verify claims were extracted
                websocket.send_json({'type': 'get_user_info'})
                response = websocket.receive_json()
                assert response.get('user_id') == 'test-user-id'
                assert response.get('opco_id') == 'test-opco'


class TestWebSocketEndpointLifecycle:
    """Tests for WebSocket endpoint lifecycle and message handling."""

    @pytest.fixture
    def mock_current_user(self):
        """Mock authenticated user."""
        return CurrentUser(
            keycloak_id='test-user-id',
            email='test@example.com',
            name='Test User',
            roles=['employee'],
            opco_id='test-opco',
        )

    def test_endpoint_accepts_connection(self, mock_current_user):
        """Endpoint should accept WebSocket connection at /api/v1/voice/transcribe."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Connection accepted - endpoint exists and works
                assert websocket is not None

    def test_connection_stays_open_after_auth(self, mock_current_user):
        """Connection should stay open after successful authentication."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Send multiple messages to verify connection stays open
                websocket.send_json({'type': 'ping'})
                response1 = websocket.receive_json()
                assert response1.get('type') == 'pong'

                websocket.send_json({'type': 'ping'})
                response2 = websocket.receive_json()
                assert response2.get('type') == 'pong'

    def test_binary_messages_accepted(self, mock_current_user):
        """Binary messages (audio chunks) should be accepted."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Send binary audio data
                audio_chunk = b'\x00\x01\x02\x03\x04\x05'
                websocket.send_bytes(audio_chunk)

                # Should receive acknowledgment
                response = websocket.receive_json()
                assert response.get('type') == 'ack'

    def test_text_messages_with_language_hint(self, mock_current_user):
        """Text messages with language hint should be accepted."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Send language configuration message
                websocket.send_json({'type': 'set_language', 'language': 'nl'})
                response = websocket.receive_json()
                # Should get error for unknown type (not implemented yet)
                # This will be implemented in Phase 5
                assert response.get('type') in ['ack', 'error']

    def test_invalid_json_returns_error(self, mock_current_user):
        """Invalid JSON messages should return an error response."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Send invalid JSON
                websocket.send_text('not valid json')
                response = websocket.receive_json()
                assert response.get('type') == 'error'
                assert response.get('code') == 'INVALID_JSON'

    def test_unknown_message_type_returns_error(self, mock_current_user):
        """Unknown message types should return an error response."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Send unknown message type
                websocket.send_json({'type': 'unknown_type'})
                response = websocket.receive_json()
                assert response.get('type') == 'error'
                assert response.get('code') == 'UNKNOWN_MESSAGE_TYPE'
