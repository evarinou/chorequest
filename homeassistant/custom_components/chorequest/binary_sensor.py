"""Binary-Sensor-Entities für ChoreQuest."""

from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ChoreQuestCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Binary-Sensor-Entities einrichten."""
    coordinator: ChoreQuestCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    async_add_entities([ChoreQuestOverdueSensor(coordinator, entry)])


class ChoreQuestOverdueSensor(
    CoordinatorEntity[ChoreQuestCoordinator], BinarySensorEntity
):
    """Binary Sensor: Überfällige Aufgaben vorhanden."""

    _attr_has_entity_name = True
    _attr_name = "Überfällige Aufgaben"
    _attr_icon = "mdi:alert-circle"
    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator: ChoreQuestCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_overdue"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "ChoreQuest",
            "manufacturer": "ChoreQuest",
            "model": "Haushalts-Manager",
            "sw_version": "0.1.0",
        }

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("tasks_overdue", 0) > 0

    @property
    def extra_state_attributes(self) -> dict:
        return {"tasks_overdue": self.coordinator.data.get("tasks_overdue", 0)}
