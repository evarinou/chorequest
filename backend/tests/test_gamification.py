"""Tests für Gamification-Endpoints (Leaderboard, Achievements)."""

import pytest
from tests.conftest import HEADERS


@pytest.mark.asyncio
async def test_leaderboard_empty(client):
    """Leeres Leaderboard."""
    resp = await client.get("/api/leaderboard", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_leaderboard_with_users(client):
    """Leaderboard sortiert nach total_points."""
    await client.post("/api/users", headers=HEADERS, json={"username": "user1"})
    await client.post("/api/users", headers=HEADERS, json={"username": "user2"})
    resp = await client.get("/api/leaderboard", headers=HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_weekly_leaderboard(client):
    """Wöchentliches Leaderboard."""
    await client.post("/api/users", headers=HEADERS, json={"username": "weekly1"})
    resp = await client.get("/api/leaderboard/weekly", headers=HEADERS)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_achievements_list_empty(client):
    """Leere Achievement-Liste (keine Seed-Daten im Test)."""
    resp = await client.get("/api/achievements", headers=HEADERS)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_user_achievements_empty(client):
    """Keine freigeschalteten Achievements."""
    create_resp = await client.post(
        "/api/users", headers=HEADERS, json={"username": "achuser"}
    )
    user_id = create_resp.json()["id"]
    resp = await client.get(f"/api/achievements/{user_id}", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_achievement_progress(client):
    """Achievement-Fortschritt abrufen."""
    create_resp = await client.post(
        "/api/users", headers=HEADERS, json={"username": "proguser"}
    )
    user_id = create_resp.json()["id"]
    resp = await client.get(f"/api/achievements/{user_id}/progress", headers=HEADERS)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
