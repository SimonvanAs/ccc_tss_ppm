# TSS PPM v3.0 - Authentication
"""Keycloak JWT validation middleware and dependencies."""

from dataclasses import dataclass
from typing import Annotated, List, Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import settings

# HTTP Bearer scheme for JWT tokens
security = HTTPBearer()


@dataclass
class CurrentUser:
    """Represents the authenticated user from the JWT token."""

    keycloak_id: str
    email: str
    name: str
    roles: List[str]
    opco_id: Optional[str] = None

    def has_role(self, role: str) -> bool:
        """Check if user has a specific role."""
        return role in self.roles

    @property
    def is_employee(self) -> bool:
        """Check if user has employee role."""
        return self.has_role('employee')

    @property
    def is_manager(self) -> bool:
        """Check if user has manager role."""
        return self.has_role('manager')

    @property
    def is_hr(self) -> bool:
        """Check if user has HR role."""
        return self.has_role('hr')

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.has_role('admin')


# Cache for JWKS keys (in production, use a proper cache with TTL)
_jwks_cache: Optional[dict] = None


async def get_jwks() -> dict:
    """Fetch JWKS from Keycloak for token verification.

    In production, this should use proper caching with TTL.
    """
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(settings.keycloak_jwks_url)
        response.raise_for_status()
        _jwks_cache = response.json()
        return _jwks_cache


def decode_token(token: str, jwks: dict) -> dict:
    """Decode and validate a JWT token.

    Args:
        token: The JWT token string
        jwks: The JWKS from Keycloak

    Returns:
        The decoded token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Get the key ID from the token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        # Find the matching key in JWKS
        rsa_key = None
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                rsa_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
                break

        if rsa_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Unable to find appropriate key',
            )

        # Decode and verify the token
        # Note: audience verification disabled for local dev - tokens from
        # Keycloak public clients don't include aud claim by default
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=['RS256'],
            issuer=settings.keycloak_issuer,
            options={'verify_aud': False},
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired',
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'Invalid token: {str(e)}',
        )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> CurrentUser:
    """FastAPI dependency to get the current authenticated user.

    Validates the JWT token and extracts user information.

    Args:
        credentials: The HTTP Bearer credentials

    Returns:
        CurrentUser object with user details

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
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


def require_role(role: str):
    """Dependency factory for role-based access control.

    Args:
        role: The required role

    Returns:
        A dependency function that validates the role
    """
    async def role_checker(
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
    ) -> CurrentUser:
        if not current_user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f'Role "{role}" required',
            )
        return current_user

    return role_checker


# Convenience dependencies for common role checks
require_employee = require_role('employee')
require_manager = require_role('manager')
require_hr = require_role('hr')
require_admin = require_role('admin')
