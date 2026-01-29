"""Todo-Listen-Entities für ChoreQuest (eine pro Raum)."""

from __future__ import annotations

import logging

from homeassistant.components.todo import (
    TodoItem,
    TodoItemStatus,
    TodoListEntity,
    TodoListEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import ChoreQuestApiClient, ChoreQuestApiError
from .const import DOMAIN
from .coordinator import ChoreQuestCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Todo-Listen einrichten (eine pro Raum)."""
    coordinator: ChoreQuestCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    client: ChoreQuestApiClient = hass.data[DOMAIN][entry.entry_id]["client"]

    entities = []
    for room in coordinator.data.get("rooms", []):
        entities.append(ChoreQuestRoomTodoList(coordinator, client, entry, room))

    async_add_entities(entities)


class ChoreQuestRoomTodoList(
    CoordinatorEntity[ChoreQuestCoordinator], TodoListEntity
):
    """Todo-Liste für einen Raum."""

    _attr_has_entity_name = True
    _attr_supported_features = TodoListEntityFeature.UPDATE_TODO_ITEM

    def __init__(
        self,
        coordinator: ChoreQuestCoordinator,
        client: ChoreQuestApiClient,
        entry: ConfigEntry,
        room: dict,
    ) -> None:
        super().__init__(coordinator)
        self._client = client
        self._room_id = room["room_id"]
        self._attr_name = f"Aufgaben {room['room_name']}"
        self._attr_icon = room.get("icon", "mdi:room")
        self._attr_unique_id = f"{entry.entry_id}_todo_room_{self._room_id}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "ChoreQuest",
            "manufacturer": "ChoreQuest",
            "model": "Haushalts-Manager",
            "sw_version": "0.1.0",
        }

    @property
    def todo_items(self) -> list[TodoItem]:
        """Aktuelle Tasks des Raums als TodoItems."""
        items = []
        for room in self.coordinator.data.get("rooms", []):
            if room["room_id"] == self._room_id:
                for task in room.get("tasks", []):
                    items.append(
                        TodoItem(
                            uid=str(task["instance_id"]),
                            summary=task["title"],
                            status=TodoItemStatus.NEEDS_ACTION
                            if task["status"] == "pending"
                            else TodoItemStatus.COMPLETED,
                            description=f"{task['base_points']} Punkte",
                        )
                    )
                break
        return items

    async def async_update_todo_item(self, item: TodoItem) -> None:
        """Task abhaken — User wird aus dem HA-Kontext aufgelöst."""
        if item.status != TodoItemStatus.COMPLETED:
            return

        instance_id = int(item.uid)

        # User-Auflösung: Versuche den HA-User auf einen ChoreQuest-User zu mappen
        user_id = await self._resolve_user_id()
        if user_id is None:
            _LOGGER.warning(
                "Konnte keinen ChoreQuest-Benutzer zuordnen. "
                "Verwende ersten verfügbaren Benutzer."
            )
            users = self.coordinator.data.get("users", [])
            if users:
                user_id = users[0]["id"]
            else:
                _LOGGER.error("Keine Benutzer im System vorhanden")
                return

        try:
            await self._client.complete_task(instance_id, user_id)
            await self.coordinator.async_request_refresh()
        except ChoreQuestApiError as err:
            _LOGGER.error("Fehler beim Abschließen der Aufgabe %d: %s", instance_id, err)

    async def _resolve_user_id(self) -> int | None:
        """Versucht den aktuellen HA-User einem ChoreQuest-User zuzuordnen."""
        # Über ha_user_id in den Dashboard-Daten nachschlagen
        context = self.hass.data.get("context")
        if context and hasattr(context, "user_id") and context.user_id:
            ha_user_id = context.user_id
            for user in self.coordinator.data.get("users", []):
                if user.get("ha_user_id") == ha_user_id:
                    return user["id"]

        # Fallback: Erster User
        users = self.coordinator.data.get("users", [])
        return users[0]["id"] if users else None
