"""Tests für Task- und Instance-Endpoints."""

from datetime import date

import pytest
from tests.conftest import HEADERS


async def _create_room(client, name="Testküche"):
    """Hilfsfunktion: Raum erstellen."""
    resp = await client.post("/api/rooms", headers=HEADERS, json={"name": name})
    return resp.json()["id"]


async def _create_user(client, username="testuser"):
    """Hilfsfunktion: Benutzer erstellen."""
    resp = await client.post("/api/users", headers=HEADERS, json={"username": username})
    return resp.json()["id"]


async def _create_task(client, room_id, title="Spülen", **kwargs):
    """Hilfsfunktion: Task erstellen."""
    data = {"title": title, "room_id": room_id, **kwargs}
    resp = await client.post("/api/tasks", headers=HEADERS, json=data)
    return resp.json()


async def _create_instance(client, task_id, db_session):
    """Hilfsfunktion: Task-Instanz direkt in DB erstellen."""
    from app.models.task import TaskInstance
    instance = TaskInstance(task_id=task_id, due_date=date.today(), status="pending")
    db_session.add(instance)
    await db_session.flush()
    await db_session.refresh(instance)
    return instance.id


@pytest.mark.asyncio
async def test_list_tasks_empty(client):
    """Leere Task-Liste."""
    resp = await client.get("/api/tasks", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_task(client):
    """Task erstellen."""
    room_id = await _create_room(client)
    resp = await client.post(
        "/api/tasks",
        headers=HEADERS,
        json={"title": "Spülmaschine ausräumen", "room_id": room_id, "base_points": 10},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Spülmaschine ausräumen"
    assert data["base_points"] == 10


@pytest.mark.asyncio
async def test_update_task(client):
    """Task aktualisieren."""
    room_id = await _create_room(client)
    task = await _create_task(client, room_id)
    resp = await client.patch(
        f"/api/tasks/{task['id']}",
        headers=HEADERS,
        json={"title": "Neuer Titel", "base_points": 20},
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Neuer Titel"
    assert resp.json()["base_points"] == 20


@pytest.mark.asyncio
async def test_delete_task(client):
    """Task löschen."""
    room_id = await _create_room(client)
    task = await _create_task(client, room_id)
    resp = await client.delete(f"/api/tasks/{task['id']}", headers=HEADERS)
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_instances_today(client, db_session):
    """Heutige Instanzen abrufen."""
    room_id = await _create_room(client)
    task = await _create_task(client, room_id)
    await _create_instance(client, task["id"], db_session)

    resp = await client.get("/api/instances/today", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["status"] == "pending"


@pytest.mark.asyncio
async def test_complete_instance(client, db_session):
    """Task-Instanz abschließen mit Bonus-Breakdown."""
    room_id = await _create_room(client)
    user_id = await _create_user(client)
    task = await _create_task(client, room_id, base_points=10)
    instance_id = await _create_instance(client, task["id"], db_session)

    resp = await client.post(
        f"/api/instances/{instance_id}/complete",
        headers=HEADERS,
        json={"user_id": user_id},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "completion" in data
    assert "bonus_breakdown" in data
    assert "streak" in data
    assert "unlocked_achievements" in data
    assert data["bonus_breakdown"]["base_points"] == 10
    assert data["completion"]["points_earned"] > 0


@pytest.mark.asyncio
async def test_complete_instance_already_completed(client, db_session):
    """Bereits erledigte Instanz gibt 400 zurück."""
    room_id = await _create_room(client)
    user_id = await _create_user(client)
    task = await _create_task(client, room_id)
    instance_id = await _create_instance(client, task["id"], db_session)

    await client.post(
        f"/api/instances/{instance_id}/complete",
        headers=HEADERS,
        json={"user_id": user_id},
    )
    resp = await client.post(
        f"/api/instances/{instance_id}/complete",
        headers=HEADERS,
        json={"user_id": user_id},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_skip_instance(client, db_session):
    """Task-Instanz überspringen."""
    room_id = await _create_room(client)
    task = await _create_task(client, room_id)
    instance_id = await _create_instance(client, task["id"], db_session)

    resp = await client.post(f"/api/instances/{instance_id}/skip", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Task übersprungen"


@pytest.mark.asyncio
async def test_assign_instance(client, db_session):
    """Task-Instanz einem Benutzer zuweisen."""
    room_id = await _create_room(client)
    user_id = await _create_user(client)
    task = await _create_task(client, room_id)
    instance_id = await _create_instance(client, task["id"], db_session)

    resp = await client.post(
        f"/api/instances/{instance_id}/assign",
        headers=HEADERS,
        json={"user_id": user_id},
    )
    assert resp.status_code == 200
    assert resp.json()["assigned_user_id"] == user_id
