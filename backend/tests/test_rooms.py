"""Tests für Room-Endpoints."""

import pytest
from tests.conftest import HEADERS


@pytest.mark.asyncio
async def test_list_rooms_empty(client):
    """Leere Raum-Liste."""
    resp = await client.get("/api/rooms", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_room(client):
    """Raum erstellen."""
    resp = await client.post(
        "/api/rooms",
        headers=HEADERS,
        json={"name": "Küche", "icon": "mdi:silverware-fork-knife"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Küche"
    assert data["point_multiplier"] == 1.0


@pytest.mark.asyncio
async def test_update_room(client):
    """Raum aktualisieren."""
    create_resp = await client.post(
        "/api/rooms", headers=HEADERS, json={"name": "Alt"}
    )
    room_id = create_resp.json()["id"]
    resp = await client.patch(
        f"/api/rooms/{room_id}",
        headers=HEADERS,
        json={"name": "Neu", "point_multiplier": 1.5},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Neu"
    assert resp.json()["point_multiplier"] == 1.5


@pytest.mark.asyncio
async def test_delete_room(client):
    """Raum löschen."""
    create_resp = await client.post(
        "/api/rooms", headers=HEADERS, json={"name": "ZumLöschen"}
    )
    room_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/rooms/{room_id}", headers=HEADERS)
    assert resp.status_code == 204

    # Raum sollte weg sein
    list_resp = await client.get("/api/rooms", headers=HEADERS)
    assert all(r["id"] != room_id for r in list_resp.json())


@pytest.mark.asyncio
async def test_sync_rooms(client):
    """Raum-Sync aus HA-Areas."""
    resp = await client.post(
        "/api/rooms/sync",
        headers=HEADERS,
        json={
            "areas": [
                {"area_id": "kueche_1", "name": "Küche"},
                {"area_id": "bad_1", "name": "Bad"},
            ]
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["created"]) == 2
    assert len(data["updated"]) == 0

    # Zweiter Sync: Umbenennung
    resp2 = await client.post(
        "/api/rooms/sync",
        headers=HEADERS,
        json={
            "areas": [
                {"area_id": "kueche_1", "name": "Küche NEU"},
                {"area_id": "bad_1", "name": "Bad"},
            ]
        },
    )
    data2 = resp2.json()
    assert len(data2["created"]) == 0
    assert len(data2["updated"]) == 1
    assert data2["updated"][0]["name"] == "Küche NEU"
