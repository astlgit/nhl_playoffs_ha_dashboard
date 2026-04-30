from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .series_sensor import async_setup_entry as setup_series_sensors
from .live_series_sensor import async_setup_entry as setup_live_sensors


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up all NHL Playoffs sensors."""
    # Existing bracket + carousel + schedule sensors
    await setup_series_sensors(hass, entry, async_add_entities)

    # New unified live sensors
    await setup_live_sensors(hass, entry, async_add_entities)
