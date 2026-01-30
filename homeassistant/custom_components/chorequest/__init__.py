"""ChoreQuest — Gamifizierter Haushalts-Todo-Manager für Home Assistant."""

from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import area_registry as ar
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.components import webhook
from homeassistant.helpers.event import async_track_time_interval

from .api import ChoreQuestApiClient, ChoreQuestApiError
from .const import CONF_API_KEY, CONF_BACKEND_URL, CONF_WEBHOOK_ID, DOMAIN, SYNC_INTERVAL_HOURS
from .coordinator import ChoreQuestCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.TODO]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration aus Config Entry einrichten."""
    session = async_get_clientsession(hass)
    client = ChoreQuestApiClient(
        entry.data[CONF_BACKEND_URL],
        entry.data[CONF_API_KEY],
        session,
    )

    coordinator = ChoreQuestCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "client": client,
        "coordinator": coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Webhook registrieren (für Echtzeit-Updates vom Backend)
    webhook_id = entry.data.get(CONF_WEBHOOK_ID)
    if webhook_id:
        webhook.async_register(
            hass,
            DOMAIN,
            "ChoreQuest",
            webhook_id,
            _handle_webhook,
        )
        hass.data[DOMAIN][entry.entry_id]["webhook_id"] = webhook_id
        _LOGGER.info("Webhook registriert: %s", webhook_id)

    # Services registrieren
    _register_services(hass, entry)

    # Periodischer Re-Sync alle 24h
    async def _periodic_sync(_now) -> None:
        await _run_sync(hass, client)

    unsub = async_track_time_interval(
        hass, _periodic_sync, timedelta(hours=SYNC_INTERVAL_HOURS)
    )
    hass.data[DOMAIN][entry.entry_id]["unsub_sync"] = unsub

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Integration entladen."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        unsub = data.get("unsub_sync")
        if unsub:
            unsub()
        # Webhook deregistrieren
        webhook_id = data.get("webhook_id")
        if webhook_id:
            webhook.async_unregister(hass, webhook_id)
    return unload_ok


async def _handle_webhook(
    hass: HomeAssistant, webhook_id: str, request
) -> None:
    """Verarbeitet eingehende Webhooks vom ChoreQuest-Backend."""
    try:
        data = await request.json()
    except ValueError:
        _LOGGER.warning("Webhook: Ungültiges JSON empfangen")
        return

    event_type = data.get("event_type", "unknown")
    _LOGGER.debug("Webhook empfangen: %s", event_type)

    # HA-Event feuern für Automationen
    hass.bus.async_fire(f"chorequest_{event_type}", data)

    # Coordinator refreshen für alle Entries
    for entry_data in hass.data.get(DOMAIN, {}).values():
        if isinstance(entry_data, dict) and "coordinator" in entry_data:
            coordinator = entry_data["coordinator"]
            await coordinator.async_request_refresh()


def _register_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Registriert HA-Services für ChoreQuest."""

    async def handle_complete_task(call: ServiceCall) -> None:
        """Service: Aufgabe als erledigt markieren."""
        instance_id = call.data["instance_id"]
        user_id = call.data["user_id"]
        notes = call.data.get("notes")
        client: ChoreQuestApiClient = hass.data[DOMAIN][entry.entry_id]["client"]
        try:
            await client.complete_task(instance_id, user_id, notes)
            coordinator: ChoreQuestCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
            await coordinator.async_request_refresh()
        except ChoreQuestApiError as err:
            _LOGGER.error("Fehler beim Abschließen der Aufgabe: %s", err)

    async def handle_refresh_tasks(call: ServiceCall) -> None:
        """Service: Dashboard-Daten neu laden."""
        coordinator: ChoreQuestCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        await coordinator.async_request_refresh()

    async def handle_sync_rooms(call: ServiceCall) -> None:
        """Service: Räume und Benutzer synchronisieren."""
        client: ChoreQuestApiClient = hass.data[DOMAIN][entry.entry_id]["client"]
        await _run_sync(hass, client)
        coordinator: ChoreQuestCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
        await coordinator.async_request_refresh()

    if not hass.services.has_service(DOMAIN, "complete_task"):
        hass.services.async_register(
            DOMAIN,
            "complete_task",
            handle_complete_task,
            schema=vol.Schema(
                {
                    vol.Required("instance_id"): int,
                    vol.Required("user_id"): int,
                    vol.Optional("notes"): str,
                }
            ),
        )

    if not hass.services.has_service(DOMAIN, "refresh_tasks"):
        hass.services.async_register(DOMAIN, "refresh_tasks", handle_refresh_tasks)

    if not hass.services.has_service(DOMAIN, "sync_rooms"):
        hass.services.async_register(DOMAIN, "sync_rooms", handle_sync_rooms)


async def _run_sync(hass: HomeAssistant, client: ChoreQuestApiClient) -> None:
    """Synchronisiert Areas und Personen mit dem Backend."""
    try:
        # Areas synchronisieren
        area_reg = ar.async_get(hass)
        areas = [
            {"area_id": area.id, "name": area.name}
            for area in area_reg.async_list_areas()
        ]
        if areas:
            result = await client.sync_rooms(areas)
            _LOGGER.info(
                "Re-Sync Räume: %d erstellt, %d aktualisiert",
                len(result.get("created", [])),
                len(result.get("updated", [])),
            )

        # Personen synchronisieren
        entity_reg = er.async_get(hass)
        persons = []
        for entity in entity_reg.entities.values():
            if entity.domain == "person":
                name = entity.name or entity.original_name or entity.entity_id
                persons.append({"person_id": entity.entity_id, "name": name})
        if persons:
            result = await client.sync_users(persons)
            _LOGGER.info(
                "Re-Sync Benutzer: %d erstellt, %d aktualisiert",
                len(result.get("created", [])),
                len(result.get("updated", [])),
            )
    except ChoreQuestApiError as err:
        _LOGGER.error("Sync fehlgeschlagen: %s", err)
