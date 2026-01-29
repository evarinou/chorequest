"""Sensor-Entities für ChoreQuest."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorStateClass
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
    """Sensor-Entities einrichten."""
    coordinator: ChoreQuestCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities: list[SensorEntity] = []

    # Globale Sensoren
    entities.append(ChoreQuestTasksTodaySensor(coordinator, entry))
    entities.append(ChoreQuestWeeklyLeaderSensor(coordinator, entry))

    # Pro-User-Sensoren
    for user in coordinator.data.get("users", []):
        entities.append(ChoreQuestUserPointsSensor(coordinator, entry, user))
        entities.append(ChoreQuestUserWeeklyPointsSensor(coordinator, entry, user))
        entities.append(ChoreQuestUserStreakSensor(coordinator, entry, user))

    async_add_entities(entities)


class ChoreQuestSensorBase(CoordinatorEntity[ChoreQuestCoordinator], SensorEntity):
    """Basis-Klasse für ChoreQuest-Sensoren."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ChoreQuestCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "ChoreQuest",
            "manufacturer": "ChoreQuest",
            "model": "Haushalts-Manager",
            "sw_version": "0.1.0",
        }


class ChoreQuestTasksTodaySensor(ChoreQuestSensorBase):
    """Sensor: Anzahl heutiger offener Aufgaben."""

    _attr_name = "Aufgaben heute"
    _attr_icon = "mdi:clipboard-list"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "Aufgaben"

    def __init__(self, coordinator: ChoreQuestCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_tasks_today"

    @property
    def native_value(self) -> int:
        return self.coordinator.data.get("tasks_today", 0)


class ChoreQuestWeeklyLeaderSensor(ChoreQuestSensorBase):
    """Sensor: Wochenführer (Benutzer mit den meisten Wochenpunkten)."""

    _attr_name = "Wochenführer"
    _attr_icon = "mdi:trophy"

    def __init__(self, coordinator: ChoreQuestCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_weekly_leader"

    @property
    def native_value(self) -> str | None:
        users = self.coordinator.data.get("users", [])
        if not users:
            return None
        leader = max(users, key=lambda u: u.get("weekly_points", 0))
        return leader.get("display_name") or leader.get("username")

    @property
    def extra_state_attributes(self) -> dict:
        users = self.coordinator.data.get("users", [])
        if not users:
            return {}
        leader = max(users, key=lambda u: u.get("weekly_points", 0))
        return {"weekly_points": leader.get("weekly_points", 0)}


class ChoreQuestUserPointsSensor(ChoreQuestSensorBase):
    """Sensor: Gesamtpunkte eines Benutzers."""

    _attr_icon = "mdi:star"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_unit_of_measurement = "Punkte"

    def __init__(
        self,
        coordinator: ChoreQuestCoordinator,
        entry: ConfigEntry,
        user: dict,
    ) -> None:
        super().__init__(coordinator, entry)
        self._user_id = user["id"]
        name = user.get("display_name") or user.get("username")
        self._attr_name = f"{name} Punkte gesamt"
        self._attr_unique_id = f"{entry.entry_id}_user_{self._user_id}_total_points"

    @property
    def native_value(self) -> int:
        for user in self.coordinator.data.get("users", []):
            if user["id"] == self._user_id:
                return user.get("total_points", 0)
        return 0


class ChoreQuestUserWeeklyPointsSensor(ChoreQuestSensorBase):
    """Sensor: Wochenpunkte eines Benutzers."""

    _attr_icon = "mdi:calendar-star"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "Punkte"

    def __init__(
        self,
        coordinator: ChoreQuestCoordinator,
        entry: ConfigEntry,
        user: dict,
    ) -> None:
        super().__init__(coordinator, entry)
        self._user_id = user["id"]
        name = user.get("display_name") or user.get("username")
        self._attr_name = f"{name} Punkte Woche"
        self._attr_unique_id = f"{entry.entry_id}_user_{self._user_id}_weekly_points"

    @property
    def native_value(self) -> int:
        for user in self.coordinator.data.get("users", []):
            if user["id"] == self._user_id:
                return user.get("weekly_points", 0)
        return 0


class ChoreQuestUserStreakSensor(ChoreQuestSensorBase):
    """Sensor: Aktuelle Streak eines Benutzers."""

    _attr_icon = "mdi:fire"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "Tage"

    def __init__(
        self,
        coordinator: ChoreQuestCoordinator,
        entry: ConfigEntry,
        user: dict,
    ) -> None:
        super().__init__(coordinator, entry)
        self._user_id = user["id"]
        name = user.get("display_name") or user.get("username")
        self._attr_name = f"{name} Streak"
        self._attr_unique_id = f"{entry.entry_id}_user_{self._user_id}_streak"

    @property
    def native_value(self) -> int:
        for user in self.coordinator.data.get("users", []):
            if user["id"] == self._user_id:
                return user.get("current_streak", 0)
        return 0
