# TSS PPM v3.0 - WebSocket Authentication
"""JWT token validation for WebSocket connections."""

from typing import Optional

from starlette.websockets import WebSocket

from src.auth import CurrentUser, get_jwks, decode_token


# Custom WebSocket close codes for authentication errors
WS_CLOSE_AUTH_REQUIRED = 4001  # Authentication required / invalid token


async def validate_websocket_token(token: str) -> CurrentUser:
    """Validate a JWT token for WebSocket authentication.

    Reuses the existing Keycloak JWT validation logic from the auth module.

    Args:
        token: The JWT token string

    Returns:
        CurrentUser object with user details

    Raises:
        Exception: If token is invalid, expired, or malformed
    """
    jwks = await get_jwks()
    payload = decode_token(token, jwks)

    # Extract roles from realm_access
    realm_access = payload.get('realm_access', {})
    roles = realm_access.get('roles', [])

    # Extract custom opco_id claim
    opco_id = payload.get('opco_id')

    return CurrentUser(
        keycloak_id=payload.get('sub', ''),
        email=payload.get('email', ''),
        name=payload.get('name', ''),
        roles=roles,
        opco_id=opco_id,
    )


def get_token_from_query(websocket: WebSocket) -> Optional[str]:
    """Extract JWT token from WebSocket query parameters.

    Args:
        websocket: The WebSocket connection

    Returns:
        The token string if present, None otherwise
    """
    return websocket.query_params.get('token')


async def authenticate_websocket(websocket: WebSocket) -> Optional[CurrentUser]:
    """Authenticate a WebSocket connection using JWT token.

    Extracts token from query parameter and validates it.

    Args:
        websocket: The WebSocket connection

    Returns:
        CurrentUser if authentication succeeds, None otherwise
    """
    token = get_token_from_query(websocket)

    if not token:
        return None

    try:
        return await validate_websocket_token(token)
    except Exception:
        return None
