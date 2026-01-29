"""DataUpdateCoordinator für ChoreQuest."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ChoreQuestApiClient, ChoreQuestApiError
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ChoreQuestCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Koordinator, der Dashboard-Daten vom Backend pollt."""

    def __init__(self, hass: HomeAssistant, client: ChoreQuestApiClient) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Holt aktuelle Dashboard-Daten vom Backend."""
        try:
            return await self.client.get_dashboard()
        except ChoreQuestApiError as err:
            raise UpdateFailed(f"Fehler beim Abrufen der Dashboard-Daten: {err}") from err
