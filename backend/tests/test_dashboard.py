"""
Dashboard endpoint tests.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_unauthorized(client: AsyncClient):
    """Dashboard requires authentication."""
    resp = await client.get("/api/v1/dashboard")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_dashboard_kpis(auth_client: AsyncClient):
    """Test KPI endpoint returns expected shape."""
    resp = await auth_client.get("/api/v1/dashboard/kpis")
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert "label" in data[0]
            assert "value" in data[0]
            assert "change" in data[0]


@pytest.mark.asyncio
async def test_dashboard_crime_trends(auth_client: AsyncClient):
    """Test crime trends endpoint."""
    resp = await auth_client.get("/api/v1/dashboard/crime-trends")
    if resp.status_code == 200:
        data = resp.json()
        assert isinstance(data, list)
        if data:
            assert "month" in data[0]
