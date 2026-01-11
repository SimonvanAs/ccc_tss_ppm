# TSS PPM v3.0 - Whisper Service Client
"""HTTP client for the faster-whisper-server transcription service."""

import io
import logging
from typing import Optional

import httpx

from src.config import settings


logger = logging.getLogger(__name__)


class WhisperServiceError(Exception):
    """Raised when whisper service is unavailable or returns an error."""

    pass


class WhisperClient:
    """Async HTTP client for the faster-whisper-server.

    Uses the OpenAI-compatible API provided by faster-whisper-server.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: float = 30.0):
        """Initialize the whisper client.

        Args:
            base_url: Whisper service URL (defaults to settings.whisper_service_url)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url or settings.whisper_service_url
        self.timeout = timeout

    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        response_format: str = 'json',
    ) -> dict:
        """Transcribe audio data using the whisper service.

        Args:
            audio_data: Audio bytes (WebM, WAV, MP3, etc.)
            language: Language hint (en, nl, es) or None for auto-detection
            response_format: Response format (json, text, verbose_json)

        Returns:
            Dict with transcription result, containing at minimum 'text' key

        Raises:
            WhisperServiceError: If service is unavailable or returns error
        """
        url = f'{self.base_url}/v1/audio/transcriptions'

        # Prepare form data
        files = {
            'file': ('audio.webm', io.BytesIO(audio_data), 'audio/webm'),
        }
        data = {
            'response_format': response_format,
        }

        if language:
            data['language'] = language

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, files=files, data=data)

                if response.status_code != 200:
                    logger.error(
                        'Whisper service error',
                        extra={
                            'status_code': response.status_code,
                            'response': response.text[:200],
                        }
                    )
                    raise WhisperServiceError(
                        f'Whisper service returned status {response.status_code}'
                    )

                return response.json()

        except httpx.ConnectError as e:
            logger.error('Cannot connect to whisper service', extra={'error': str(e)})
            raise WhisperServiceError(
                f'Whisper service unavailable: connection refused'
            ) from e

        except httpx.TimeoutException as e:
            logger.error('Whisper service timeout', extra={'error': str(e)})
            raise WhisperServiceError(
                f'Whisper service unavailable: request timeout'
            ) from e

        except Exception as e:
            logger.error('Whisper service error', extra={'error': str(e)})
            raise WhisperServiceError(
                f'Whisper service unavailable: {str(e)}'
            ) from e

    async def health_check(self) -> bool:
        """Check if whisper service is healthy.

        Returns:
            True if service is responding, False otherwise
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f'{self.base_url}/')
                return response.status_code == 200
        except Exception:
            return False


# Global client instance for convenience
_client: Optional[WhisperClient] = None


def get_whisper_client() -> WhisperClient:
    """Get or create the global whisper client instance."""
    global _client
    if _client is None:
        _client = WhisperClient()
    return _client
