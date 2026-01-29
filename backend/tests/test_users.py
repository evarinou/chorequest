"""Tests für User-Endpoints."""

import pytest
from tests.conftest import HEADERS


@pytest.mark.asyncio
async def test_list_users_empty(client):
    """Leere User-Liste."""
    resp = await client.get("/api/users", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_user(client):
    """Benutzer erstellen."""
    resp = await client.post(
        "/api/users",
        headers=HEADERS,
        json={"username": "testuser", "display_name": "Test User"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "testuser"
    assert data["display_name"] == "Test User"
    assert data["total_points"] == 0


@pytest.mark.asyncio
async def test_create_user_auto_display_name(client):
    """Display-Name wird automatisch gesetzt wenn nicht angegeben."""
    resp = await client.post(
        "/api/users",
        headers=HEADERS,
        json={"username": "lukas"},
    )
    assert resp.status_code == 201
    assert resp.json()["display_name"] == "Lukas"


@pytest.mark.asyncio
async def test_create_user_duplicate(client):
    """Duplikat-Benutzername gibt 409 zurück."""
    await client.post("/api/users", headers=HEADERS, json={"username": "dup"})
    resp = await client.post("/api/users", headers=HEADERS, json={"username": "dup"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_get_user(client):
    """Einzelnen Benutzer abrufen."""
    create_resp = await client.post(
        "/api/users", headers=HEADERS, json={"username": "getme"}
    )
    user_id = create_resp.json()["id"]
    resp = await client.get(f"/api/users/{user_id}", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["username"] == "getme"


@pytest.mark.asyncio
async def test_get_user_not_found(client):
    """Nicht existierender Benutzer gibt 404 zurück."""
    resp = await client.get("/api/users/9999", headers=HEADERS)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_user(client):
    """Benutzer aktualisieren."""
    create_resp = await client.post(
        "/api/users", headers=HEADERS, json={"username": "updme"}
    )
    user_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/users/{user_id}",
        headers=HEADERS,
        json={"display_name": "Neuer Name"},
    )
    assert resp.status_code == 200
    assert resp.json()["display_name"] == "Neuer Name"


@pytest.mark.asyncio
async def test_user_stats(client):
    """User-Stats abrufen."""
    create_resp = await client.post(
        "/api/users", headers=HEADERS, json={"username": "statsuser"}
    )
    user_id = create_resp.json()["id"]
    resp = await client.get(f"/api/users/{user_id}/stats", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert data["tasks_completed_total"] == 0
    assert data["tasks_completed_this_week"] == 0
    assert data["achievements_count"] == 0
