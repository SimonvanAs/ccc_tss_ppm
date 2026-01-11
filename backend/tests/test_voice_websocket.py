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
        """Binary messages (audio chunks) should be accepted and accumulated."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Send binary audio data - should be accumulated silently
                audio_chunk = b'\x00\x01\x02\x03\x04\x05'
                websocket.send_bytes(audio_chunk)

                # Verify connection is still active with a ping
                websocket.send_json({'type': 'ping'})
                response = websocket.receive_json()
                assert response.get('type') == 'pong'

    def test_text_messages_with_language_hint(self, mock_current_user):
        """Text messages with language hint should be accepted."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            client = TestClient(app)
            with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                # Send language configuration message
                websocket.send_json({'type': 'set_language', 'language': 'nl'})
                response = websocket.receive_json()
                assert response.get('type') == 'ack'

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


class TestTranscriptionPipeline:
    """Tests for the end-to-end audio transcription pipeline."""

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

    @pytest.fixture
    def sample_audio_chunk(self):
        """Sample audio data chunk."""
        return b'\x1a\x45\xdf\xa3' + b'\x00' * 100

    def test_audio_chunks_reach_whisper_service(self, mock_current_user, sample_audio_chunk):
        """Audio sent via WebSocket should be forwarded to whisper service."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            with patch('src.routers.voice.get_whisper_client') as mock_get_client:
                mock_client = MagicMock()
                mock_client.transcribe = AsyncMock(return_value={'text': 'Test transcription'})
                mock_get_client.return_value = mock_client

                client = TestClient(app)
                with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                    # Send audio chunks
                    websocket.send_bytes(sample_audio_chunk)
                    websocket.send_bytes(sample_audio_chunk)

                    # Signal end of audio
                    websocket.send_json({'type': 'end_audio'})

                    # Should get transcription response
                    response = websocket.receive_json()
                    assert response.get('type') == 'final'

                    # Verify whisper client was called
                    mock_client.transcribe.assert_called_once()

    def test_transcription_response_reaches_client(self, mock_current_user, sample_audio_chunk):
        """Transcription from whisper service should be returned to client."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            with patch('src.routers.voice.get_whisper_client') as mock_get_client:
                mock_client = MagicMock()
                mock_client.transcribe = AsyncMock(return_value={'text': 'Hello world transcription'})
                mock_get_client.return_value = mock_client

                client = TestClient(app)
                with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                    websocket.send_bytes(sample_audio_chunk)
                    websocket.send_json({'type': 'end_audio'})

                    response = websocket.receive_json()
                    assert response.get('text') == 'Hello world transcription'

    def test_final_transcription_format(self, mock_current_user, sample_audio_chunk):
        """Final transcription should have correct message format."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            with patch('src.routers.voice.get_whisper_client') as mock_get_client:
                mock_client = MagicMock()
                mock_client.transcribe = AsyncMock(return_value={'text': 'Final text'})
                mock_get_client.return_value = mock_client

                client = TestClient(app)
                with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                    websocket.send_bytes(sample_audio_chunk)
                    websocket.send_json({'type': 'end_audio'})

                    response = websocket.receive_json()
                    assert response.get('type') == 'final'
                    assert 'text' in response
                    assert 'language' in response

    def test_language_hint_flows_through_pipeline(self, mock_current_user, sample_audio_chunk):
        """Language hint should be passed to whisper service."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            with patch('src.routers.voice.get_whisper_client') as mock_get_client:
                mock_client = MagicMock()
                mock_client.transcribe = AsyncMock(return_value={'text': 'Hallo wereld'})
                mock_get_client.return_value = mock_client

                client = TestClient(app)
                with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                    # Set language before sending audio
                    websocket.send_json({'type': 'set_language', 'language': 'nl'})
                    response = websocket.receive_json()
                    assert response.get('type') == 'ack'

                    websocket.send_bytes(sample_audio_chunk)
                    websocket.send_json({'type': 'end_audio'})

                    response = websocket.receive_json()
                    assert response.get('type') == 'final'

                    # Verify language was passed to transcribe
                    call_kwargs = mock_client.transcribe.call_args
                    assert call_kwargs.kwargs.get('language') == 'nl'

    def test_audio_accumulation_before_transcription(self, mock_current_user):
        """Multiple audio chunks should be accumulated before transcription."""
        with patch('src.services.websocket_auth.validate_websocket_token') as mock_validate:
            mock_validate.return_value = mock_current_user

            with patch('src.routers.voice.get_whisper_client') as mock_get_client:
                mock_client = MagicMock()
                mock_client.transcribe = AsyncMock(return_value={'text': 'Combined audio'})
                mock_get_client.return_value = mock_client

                chunk1 = b'\x00\x01\x02\x03'
                chunk2 = b'\x04\x05\x06\x07'
                chunk3 = b'\x08\x09\x0a\x0b'

                client = TestClient(app)
                with client.websocket_connect('/api/v1/voice/transcribe?token=valid-token') as websocket:
                    websocket.send_bytes(chunk1)
                    websocket.send_bytes(chunk2)
                    websocket.send_bytes(chunk3)
                    websocket.send_json({'type': 'end_audio'})

                    response = websocket.receive_json()
                    assert response.get('type') == 'final'

                    # Verify all chunks were combined
                    call_args = mock_client.transcribe.call_args
                    audio_data = call_args.args[0]
                    assert audio_data == chunk1 + chunk2 + chunk3
