# TSS PPM v3.0 - Whisper Client Tests
"""Tests for the whisper service client."""

from unittest.mock import AsyncMock, patch, MagicMock
import pytest

from src.config import settings


class TestWhisperClient:
    """Tests for the whisper service HTTP client."""

    @pytest.fixture
    def sample_audio_data(self):
        """Sample audio data for testing."""
        # WebM audio header bytes (simplified)
        return b'\x1a\x45\xdf\xa3' + b'\x00' * 100

    @pytest.fixture
    def mock_transcription_response(self):
        """Mock transcription response from whisper service."""
        return {
            'text': 'Hello, this is a test transcription.',
        }

    async def test_client_connects_to_whisper_service(self, sample_audio_data, mock_transcription_response):
        """Client should successfully connect to and call whisper service."""
        from src.services.whisper_client import WhisperClient

        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_transcription_response
            mock_post.return_value = mock_response

            client = WhisperClient()
            result = await client.transcribe(sample_audio_data, language='en')

            assert result is not None
            assert 'text' in result
            mock_post.assert_called_once()

    async def test_audio_chunks_forwarded_to_whisper_service(self, sample_audio_data, mock_transcription_response):
        """Audio data should be forwarded to whisper service in correct format."""
        from src.services.whisper_client import WhisperClient

        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_transcription_response
            mock_post.return_value = mock_response

            client = WhisperClient()
            await client.transcribe(sample_audio_data, language='en')

            # Verify the call was made to the correct URL
            call_args = mock_post.call_args
            assert '/v1/audio/transcriptions' in str(call_args)

    async def test_transcription_response_received(self, sample_audio_data, mock_transcription_response):
        """Transcription text should be returned from whisper service."""
        from src.services.whisper_client import WhisperClient

        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_transcription_response
            mock_post.return_value = mock_response

            client = WhisperClient()
            result = await client.transcribe(sample_audio_data, language='en')

            assert result['text'] == 'Hello, this is a test transcription.'

    async def test_connection_error_when_service_unavailable(self, sample_audio_data):
        """Client should handle connection errors gracefully."""
        from src.services.whisper_client import WhisperClient, WhisperServiceError

        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.side_effect = Exception('Connection refused')

            client = WhisperClient()
            with pytest.raises(WhisperServiceError) as exc_info:
                await client.transcribe(sample_audio_data, language='en')

            assert 'unavailable' in str(exc_info.value).lower() or 'connection' in str(exc_info.value).lower()

    async def test_language_parameter_passed_correctly(self, sample_audio_data, mock_transcription_response):
        """Language parameter should be passed to whisper service."""
        from src.services.whisper_client import WhisperClient

        with patch('httpx.AsyncClient.post') as mock_post:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_transcription_response
            mock_post.return_value = mock_response

            client = WhisperClient()
            await client.transcribe(sample_audio_data, language='nl')

            # Verify language was included in the request
            call_args = mock_post.call_args
            # The language should be in the form data
            assert call_args is not None

    async def test_health_check_returns_status(self):
        """Health check should return whisper service status."""
        from src.services.whisper_client import WhisperClient

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            client = WhisperClient()
            is_healthy = await client.health_check()

            assert is_healthy is True

    async def test_health_check_returns_false_when_unavailable(self):
        """Health check should return False when service unavailable."""
        from src.services.whisper_client import WhisperClient

        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = Exception('Connection refused')

            client = WhisperClient()
            is_healthy = await client.health_check()

            assert is_healthy is False
