"""Tests für Zusammenfassungs-Endpoints."""

import pytest
from tests.conftest import HEADERS


@pytest.mark.asyncio
async def test_list_summaries_empty(client):
    """Leere Zusammenfassungs-Liste."""
    resp = await client.get("/api/summaries", headers=HEADERS)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_latest_summary_not_found(client):
    """Keine Zusammenfassung vorhanden gibt 404 zurück."""
    resp = await client.get("/api/summaries/latest", headers=HEADERS)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_generate_summary_without_claude_key(client):
    """Zusammenfassung ohne Claude-Key nutzt Fallback-Text."""
    resp = await client.post("/api/summaries/generate", headers=HEADERS)
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert "tokens_used" in data
    assert data["tokens_used"] == 0
    assert "Wochen-Zusammenfassung" in data["summary"]["summary_text"]
    assert "Claude API-Key" in data["summary"]["summary_text"]
