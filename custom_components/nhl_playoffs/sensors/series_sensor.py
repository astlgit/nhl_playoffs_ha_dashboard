from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN
from ..coordinator.coordinator import NHLPlayoffsCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: NHLPlayoffsCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[PlayoffsSeriesSensor] = []

    series_keys = [
        "playoffs_r1_west_1",
        "playoffs_r1_west_2",
        "playoffs_r1_west_3",
        "playoffs_r1_west_4",
        "playoffs_r2_west_1",
        "playoffs_r2_west_2",
        "playoffs_west_final",
        "playoffs_r2_east_1",
        "playoffs_r2_east_2",
        "playoffs_east_final",
    ]

    for series_key in series_keys:
        entities.append(PlayoffsSeriesSensor(coordinator, series_key))

    async_add_entities(entities, True)


class PlayoffsSeriesSensor(Entity):
    """A placeholder sensor entity for a playoff series."""

    def __init__(self, coordinator: NHLPlayoffsCoordinator, series_key: str) -> None:
        self.coordinator = coordinator
        self.series_key = series_key
        self._attr_name = series_key.replace("_", " ").title()
        self._attr_unique_id = series_key
        self._state = "unknown"
        self._attr_native_value = None
        self._attr_extra_state_attributes: dict[str, Any] = {
            "series_status": "Unknown",
            "team1_name": "",
            "team2_name": "",
            "team1_seed": "",
            "team2_seed": "",
            "team1_logo": "",
            "team2_logo": "",
        }

    @property
    def name(self) -> str:
        return self._attr_name

    @property
    def unique_id(self) -> str:
        return self._attr_unique_id

    @property
    def state(self) -> str:
        return self._state

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return self._attr_extra_state_attributes

    async def async_update(self) -> None:
        data = self.coordinator.data or {}
        series_data = data.get("series", {}).get(self.series_key, {})
        self._state = series_data.get("series_status", "unknown")
        self._attr_extra_state_attributes.update(series_data)
