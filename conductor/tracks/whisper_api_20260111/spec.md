# Spec: Backend API Whisper Setup

## Overview

Create a FastAPI WebSocket endpoint that proxies audio streams from the frontend VoiceInput component to the faster-whisper-server for real-time speech-to-text transcription. The endpoint will authenticate users via Keycloak JWT tokens and provide bi-directional communication for streaming audio chunks and receiving transcription results.

## Functional Requirements

### FR-1: WebSocket Endpoint
- Create a WebSocket endpoint at `/api/v1/voice/transcribe`
- Accept WebSocket connections from authenticated frontend clients
- Maintain connection state during the hold-to-dictate session

### FR-2: JWT Authentication
- Validate Keycloak JWT token on WebSocket connection handshake
- Token can be passed via:
  - Query parameter: `?token=<jwt>`
  - Or Sec-WebSocket-Protocol header
- Reject connections with invalid/expired tokens with appropriate WebSocket close codes
- Extract `opco_id` and user claims from token for audit logging

### FR-3: Audio Streaming
- Receive audio chunks as binary WebSocket messages from the frontend
- Support WebM/Opus codec (browser MediaRecorder default)
- Forward audio chunks to faster-whisper-server at `http://whisper:8001`
- Handle backpressure if whisper service is slow

### FR-4: Transcription Response
- Receive transcription results from faster-whisper-server
- Stream partial/final transcription text back to frontend as JSON messages
- Message format: `{"type": "partial|final", "text": "transcribed text", "language": "en"}`

### FR-5: Language Support
- Support language hint from frontend: EN, NL, ES
- Pass language parameter to faster-whisper-server
- Default to auto-detection if not specified

### FR-6: Error Handling
- Handle whisper service unavailability gracefully
- Send error messages to frontend: `{"type": "error", "code": "SERVICE_UNAVAILABLE", "message": "..."}`
- Implement connection timeout (configurable, default 30s of inactivity)
- Clean up resources on disconnect

## Non-Functional Requirements

### NFR-1: Performance
- Latency: < 200ms from audio chunk receipt to whisper service forward
- Support concurrent WebSocket connections (target: 50 simultaneous)

### NFR-2: Security
- All connections must be authenticated
- Rate limiting: max 10 transcription sessions per user per minute
- Audio data is not persisted (streaming only)

### NFR-3: Observability
- Log connection events (connect/disconnect) with user ID
- Log transcription requests to audit_logs table
- Expose health check for whisper service connectivity

## Acceptance Criteria

1. **AC-1**: WebSocket connection with valid JWT token succeeds and stays open
2. **AC-2**: WebSocket connection with invalid/missing JWT token is rejected with close code 4001
3. **AC-3**: Audio chunks sent via WebSocket are forwarded to faster-whisper-server
4. **AC-4**: Transcription results are streamed back to the client in real-time
5. **AC-5**: Connection gracefully closes after 30s of inactivity
6. **AC-6**: Error response is sent when whisper service is unavailable
7. **AC-7**: Language hint (en/nl/es) is correctly passed to whisper service

## Out of Scope

- Frontend VoiceInput component changes (separate track)
- GPU acceleration for whisper service
- Audio file upload endpoint (streaming only)
- Transcription history/storage
- Multi-language auto-detection within a single session
