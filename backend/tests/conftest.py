"""
Pytest configuration and shared fixtures.
"""

import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    """HTTP test client for FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient):
    """Authenticated test client."""
    # Register a test user
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "test@ksp.gov.in",
            "full_name": "Test User",
            "password": "testpass123",
            "role": "analyst",
        },
    )
    if resp.status_code in (201, 409):
        # Login
        resp = await client.post(
            "/api/v1/auth/login",
            json={"username": "testuser", "password": "testpass123"},
        )
    
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        client.headers["Authorization"] = f"Bearer {token}"
    
    yield client
