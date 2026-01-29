"""Config Flow für die ChoreQuest-Integration."""

from __future__ import annotations

import logging
import secrets
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er

from .api import ChoreQuestApiClient, ChoreQuestApiError, ChoreQuestAuthError
from .const import CONF_API_KEY, CONF_BACKEND_URL, CONF_WEBHOOK_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ChoreQuestConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config Flow für ChoreQuest."""

    VERSION = 1

    def __init__(self) -> None:
        self._backend_url: str = ""
        self._api_key: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Schritt 1: Backend-URL und API-Key eingeben."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._backend_url = user_input[CONF_BACKEND_URL].rstrip("/")
            self._api_key = user_input[CONF_API_KEY]

            # Verbindungstest
            try:
                async with aiohttp.ClientSession() as session:
                    client = ChoreQuestApiClient(
                        self._backend_url, self._api_key, session
                    )
                    await client.health_check()
                    # Auth testen mit Dashboard-Aufruf
                    await client.get_dashboard()
            except ChoreQuestAuthError:
                errors["base"] = "invalid_auth"
            except ChoreQuestApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unerwarteter Fehler im Config Flow")
                errors["base"] = "unknown"

            if not errors:
                return await self.async_step_sync()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_BACKEND_URL, default="http://localhost:8000"): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
        )

    async def async_step_sync(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Schritt 2: Automatischer Sync von Areas und Personen."""
        errors: dict[str, str] = {}

        try:
            async with aiohttp.ClientSession() as session:
                client = ChoreQuestApiClient(
                    self._backend_url, self._api_key, session
                )

                # HA-Areas synchronisieren
                area_reg = ar.async_get(self.hass)
                areas = [
                    {"area_id": area.id, "name": area.name}
                    for area in area_reg.async_list_areas()
                ]
                if areas:
                    result = await client.sync_rooms(areas)
                    _LOGGER.info(
                        "Raum-Sync: %d erstellt, %d aktualisiert",
                        len(result.get("created", [])),
                        len(result.get("updated", [])),
                    )

                # HA-Personen synchronisieren
                persons = self._get_persons()
                if persons:
                    result = await client.sync_users(persons)
                    _LOGGER.info(
                        "User-Sync: %d erstellt, %d aktualisiert",
                        len(result.get("created", [])),
                        len(result.get("updated", [])),
                    )

        except ChoreQuestApiError as err:
            _LOGGER.error("Sync fehlgeschlagen: %s", err)
            errors["base"] = "sync_failed"

        if errors:
            return self.async_abort(reason="sync_failed")

        # Eindeutigen Eintrag erstellen
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title="ChoreQuest",
            data={
                CONF_BACKEND_URL: self._backend_url,
                CONF_API_KEY: self._api_key,
                CONF_WEBHOOK_ID: secrets.token_hex(32),
            },
        )

    def _get_persons(self) -> list[dict[str, str]]:
        """Liest Person-Entities aus der Entity Registry."""
        entity_reg = er.async_get(self.hass)
        persons = []
        for entity in entity_reg.entities.values():
            if entity.domain == "person":
                name = entity.name or entity.original_name or entity.entity_id
                persons.append({
                    "person_id": entity.entity_id,
                    "name": name,
                })
        return persons
