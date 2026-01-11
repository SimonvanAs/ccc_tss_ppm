# TSS PPM v3.0 - Voice Router
"""WebSocket endpoint for voice transcription."""

import json
import logging
from typing import Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.auth import CurrentUser
from src.services.websocket_auth import (
    authenticate_websocket,
    WS_CLOSE_AUTH_REQUIRED,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/voice', tags=['voice'])


@router.websocket('/transcribe')
async def voice_transcribe(websocket: WebSocket):
    """WebSocket endpoint for voice-to-text transcription.

    Authentication:
        Requires JWT token via query parameter: ?token=<jwt>

    Messages:
        - ping: Returns pong for connection testing
        - get_user_info: Returns authenticated user information
        - Binary: Audio chunks for transcription (to be implemented)

    Close Codes:
        - 4001: Authentication required or invalid token
    """
    # Authenticate the connection
    current_user: Optional[CurrentUser] = await authenticate_websocket(websocket)

    if current_user is None:
        # Reject unauthenticated connections
        await websocket.close(code=WS_CLOSE_AUTH_REQUIRED)
        return

    # Accept the authenticated connection
    await websocket.accept()

    logger.info(
        'Voice WebSocket connected',
        extra={
            'user_id': current_user.keycloak_id,
            'opco_id': current_user.opco_id,
        }
    )

    try:
        while True:
            # Handle incoming messages
            message = await websocket.receive()

            if message['type'] == 'websocket.disconnect':
                break

            if 'text' in message:
                # Handle JSON text messages
                try:
                    data = json.loads(message['text'])
                    msg_type = data.get('type')

                    if msg_type == 'ping':
                        await websocket.send_json({'type': 'pong'})

                    elif msg_type == 'get_user_info':
                        await websocket.send_json({
                            'type': 'user_info',
                            'user_id': current_user.keycloak_id,
                            'opco_id': current_user.opco_id,
                            'email': current_user.email,
                            'name': current_user.name,
                        })

                    else:
                        await websocket.send_json({
                            'type': 'error',
                            'code': 'UNKNOWN_MESSAGE_TYPE',
                            'message': f'Unknown message type: {msg_type}',
                        })

                except json.JSONDecodeError:
                    await websocket.send_json({
                        'type': 'error',
                        'code': 'INVALID_JSON',
                        'message': 'Invalid JSON message',
                    })

            elif 'bytes' in message:
                # Handle binary audio data (to be implemented in Phase 4)
                # For now, just acknowledge receipt
                await websocket.send_json({
                    'type': 'ack',
                    'message': 'Audio chunk received',
                })

    except WebSocketDisconnect:
        pass
    finally:
        logger.info(
            'Voice WebSocket disconnected',
            extra={
                'user_id': current_user.keycloak_id,
                'opco_id': current_user.opco_id,
            }
        )
