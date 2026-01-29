"""Tests für den Health-Check-Endpoint."""

import pytest
from tests.conftest import HEADERS


@pytest.mark.asyncio
async def test_health_check(client):
    """Health-Check gibt OK zurück (kein Auth nötig)."""
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["app"] == "ChoreQuest"


@pytest.mark.asyncio
async def test_auth_required_without_key(client):
    """Endpoints ohne Auth-Header geben 401 zurück."""
    resp = await client.get("/api/users")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_auth_required_with_wrong_key(client):
    """Endpoints mit falschem API-Key geben 401 zurück."""
    resp = await client.get("/api/users", headers={"Authorization": "Bearer wrong-key"})
    assert resp.status_code == 401
