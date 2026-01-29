"""API-Client für die Kommunikation mit dem ChoreQuest-Backend."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class ChoreQuestApiError(Exception):
    """Allgemeiner API-Fehler."""


class ChoreQuestAuthError(ChoreQuestApiError):
    """Authentifizierungsfehler."""


class ChoreQuestApiClient:
    """Client für das ChoreQuest-Backend."""

    def __init__(self, base_url: str, api_key: str, session: aiohttp.ClientSession) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._session = session

    @property
    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._api_key}"}

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """Führt einen API-Request durch."""
        url = f"{self._base_url}{path}"
        try:
            async with self._session.request(
                method, url, headers=self._headers, **kwargs
            ) as resp:
                if resp.status == 401:
                    raise ChoreQuestAuthError("Ungültiger API-Key")
                if resp.status >= 400:
                    text = await resp.text()
                    raise ChoreQuestApiError(
                        f"API-Fehler {resp.status}: {text}"
                    )
                if resp.status == 204:
                    return None
                return await resp.json()
        except aiohttp.ClientError as err:
            raise ChoreQuestApiError(f"Verbindungsfehler: {err}") from err

    async def health_check(self) -> dict[str, Any]:
        """Prüft die Verbindung zum Backend (kein Auth nötig)."""
        url = f"{self._base_url}/api/health"
        try:
            async with self._session.get(url) as resp:
                if resp.status != 200:
                    raise ChoreQuestApiError(f"Health-Check fehlgeschlagen: {resp.status}")
                return await resp.json()
        except aiohttp.ClientError as err:
            raise ChoreQuestApiError(f"Verbindungsfehler: {err}") from err

    async def get_dashboard(self) -> dict[str, Any]:
        """Holt die Dashboard-Daten."""
        return await self._request("GET", "/api/dashboard")

    async def get_users(self) -> list[dict[str, Any]]:
        """Holt alle Benutzer."""
        return await self._request("GET", "/api/users")

    async def sync_rooms(self, areas: list[dict[str, str]]) -> dict[str, Any]:
        """Synchronisiert HA-Areas als Räume."""
        return await self._request("POST", "/api/rooms/sync", json={"areas": areas})

    async def sync_users(self, persons: list[dict[str, str]]) -> dict[str, Any]:
        """Synchronisiert HA-Personen als Benutzer."""
        return await self._request("POST", "/api/users/sync", json={"persons": persons})

    async def complete_task(self, instance_id: int, user_id: int, notes: str | None = None) -> dict[str, Any]:
        """Markiert eine Task-Instanz als erledigt."""
        payload: dict[str, Any] = {"user_id": user_id}
        if notes:
            payload["notes"] = notes
        return await self._request("POST", f"/api/instances/{instance_id}/complete", json=payload)

    async def get_instances_today(self) -> list[dict[str, Any]]:
        """Holt die heutigen Task-Instanzen."""
        return await self._request("GET", "/api/instances/today")
