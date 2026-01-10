# TSS PPM v3.0 - Pytest Configuration
"""Shared test fixtures and configuration."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.fixture
async def client():
    """Async HTTP client for testing API endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture
def mock_user():
    """Mock user data for authentication tests."""
    return {
        'sub': 'test-user-id',
        'email': 'test@example.com',
        'name': 'Test User',
        'realm_access': {'roles': ['employee']},
        'opco_id': 'test-opco',
    }


@pytest.fixture
def mock_manager_user():
    """Mock manager user data for authorization tests."""
    return {
        'sub': 'test-manager-id',
        'email': 'manager@example.com',
        'name': 'Test Manager',
        'realm_access': {'roles': ['employee', 'manager']},
        'opco_id': 'test-opco',
    }
