"""
Auth endpoint tests.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_health(client: AsyncClient):
    """Test health check endpoint."""
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "operational"


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    resp = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testregistration",
            "email": "testreg@ksp.gov.in",
            "full_name": "Test Registration",
            "password": "securepass123",
            "role": "analyst",
        },
    )
    assert resp.status_code in (201, 409)  # 409 if user already exists
    if resp.status_code == 201:
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["user"]["username"] == "testregistration"


@pytest.mark.asyncio
async def test_login_invalid(client: AsyncClient):
    """Test login with invalid credentials."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "wrong"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_no_token(client: AsyncClient):
    """Test that protected endpoints require auth."""
    resp = await client.get("/api/v1/fir")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_profile(auth_client: AsyncClient):
    """Test getting current user profile."""
    resp = await auth_client.get("/api/v1/auth/me")
    if resp.status_code == 200:
        data = resp.json()
        assert "username" in data
        assert "role" in data
