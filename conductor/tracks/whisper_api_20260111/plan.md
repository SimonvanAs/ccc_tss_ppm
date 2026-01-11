# Plan: Backend API Whisper Setup

## Phase 1: Project Setup & Configuration [checkpoint: cd8cd19]

- [x] Task: Add WebSocket and HTTP client dependencies to requirements.txt (d32153a)
  - [x] Add `websockets` package for WebSocket support in FastAPI
  - [x] Add `httpx[http2]` for async HTTP client to whisper service (if not present)
- [x] Task: Create voice service configuration in backend settings (fe4b4c4)
  - [x] Add WHISPER_SERVICE_URL environment variable (default: http://whisper:8001)
  - [x] Add VOICE_SESSION_TIMEOUT setting (default: 30 seconds)
  - [x] Add VOICE_RATE_LIMIT setting (default: 10 per minute)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Project Setup & Configuration' (Protocol in workflow.md)

## Phase 2: WebSocket Authentication [checkpoint: 00ddce6]

- [x] Task: Write failing tests for WebSocket JWT authentication (5199e46)
  - [x] Test: Connection with valid JWT succeeds
  - [x] Test: Connection with expired JWT rejected with close code 4001
  - [x] Test: Connection with missing token rejected with close code 4001
  - [x] Test: Connection with malformed token rejected with close code 4001
  - [x] Test: User claims (user_id, opco_id) extracted from valid token
- [x] Task: Implement WebSocket JWT authentication middleware (139d991)
  - [x] Create `src/services/websocket_auth.py` with token validation
  - [x] Support token via query parameter `?token=<jwt>`
  - [x] Reuse existing Keycloak JWT validation logic from auth module
  - [x] Return appropriate WebSocket close codes for auth failures
- [x] Task: Conductor - User Manual Verification 'Phase 2: WebSocket Authentication' (Protocol in workflow.md)

## Phase 3: WebSocket Endpoint Foundation [checkpoint: 6e2c261]

- [x] Task: Write failing tests for WebSocket endpoint lifecycle (5570572)
  - [x] Test: Endpoint accepts connection at /api/v1/voice/transcribe
  - [x] Test: Connection stays open after successful auth
  - [x] Test: Connection closes after timeout period of inactivity
  - [x] Test: Binary messages are accepted (audio chunks)
  - [x] Test: Text messages are accepted (control messages with language hint)
- [x] Task: Implement WebSocket endpoint (139d991)
  - [x] Create `src/routers/voice.py` with WebSocket route
  - [x] Register router in main.py
  - [x] Implement connection lifecycle (accept, maintain, close)
  - [x] Add inactivity timeout handling
- [x] Task: Conductor - User Manual Verification 'Phase 3: WebSocket Endpoint Foundation' (Protocol in workflow.md)

## Phase 4: Whisper Service Client [checkpoint: 923a638]

- [x] Task: Write failing tests for whisper service client (285d4f5)
  - [x] Test: Client connects to whisper service HTTP endpoint
  - [x] Test: Audio chunks are forwarded to whisper service
  - [x] Test: Transcription responses are received from whisper service
  - [x] Test: Connection error handling when service unavailable
  - [x] Test: Language parameter is passed correctly
- [x] Task: Implement whisper service client (a2420b6)
  - [x] Create `src/services/whisper_client.py`
  - [x] Implement async HTTP client to faster-whisper-server
  - [x] Handle connection errors gracefully
  - [x] Implement audio forwarding via POST
  - [x] Parse transcription responses (JSON format)
- [x] Task: Conductor - User Manual Verification 'Phase 4: Whisper Service Client' (Protocol in workflow.md)

## Phase 5: End-to-End Audio Pipeline

- [ ] Task: Write failing tests for full transcription pipeline
  - [ ] Test: Audio from client reaches whisper service
  - [ ] Test: Transcription from whisper service reaches client
  - [ ] Test: Partial transcriptions streamed in real-time
  - [ ] Test: Final transcription sent with correct message format
  - [ ] Test: Language hint flows through entire pipeline
- [ ] Task: Integrate whisper client with WebSocket endpoint
  - [ ] Connect client audio stream to whisper client
  - [ ] Stream transcription responses back to client
  - [ ] Implement message format: `{"type": "partial|final", "text": "...", "language": "..."}`
- [ ] Task: Conductor - User Manual Verification 'Phase 5: End-to-End Audio Pipeline' (Protocol in workflow.md)

## Phase 6: Error Handling & Resilience

- [ ] Task: Write failing tests for error scenarios
  - [ ] Test: Graceful handling when whisper service unavailable
  - [ ] Test: Error message format sent to client
  - [ ] Test: Rate limiting rejects excessive connections
  - [ ] Test: Backpressure handling when whisper service is slow
  - [ ] Test: Clean resource cleanup on disconnect
- [ ] Task: Implement error handling and resilience
  - [ ] Add whisper service health check before accepting audio
  - [ ] Implement error response format: `{"type": "error", "code": "...", "message": "..."}`
  - [ ] Add rate limiting per user (10 sessions/minute)
  - [ ] Implement backpressure handling with buffering
  - [ ] Ensure proper cleanup of all resources on disconnect
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Error Handling & Resilience' (Protocol in workflow.md)

## Phase 7: Observability & Documentation

- [ ] Task: Write failing tests for observability features
  - [ ] Test: Connection events logged with user ID
  - [ ] Test: Transcription requests logged to audit_logs table
  - [ ] Test: Health check endpoint returns whisper service status
- [ ] Task: Implement observability features
  - [ ] Add structured logging for connect/disconnect events
  - [ ] Create audit log entries for transcription sessions
  - [ ] Add `/api/v1/voice/health` endpoint for whisper service status
- [ ] Task: Update API documentation
  - [ ] Document WebSocket endpoint in OpenAPI (manual addition)
  - [ ] Add usage examples for WebSocket client integration
- [ ] Task: Conductor - User Manual Verification 'Phase 7: Observability & Documentation' (Protocol in workflow.md)
