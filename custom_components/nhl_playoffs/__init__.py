from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    SERIES_COORDINATOR,
    LIVE_COORDINATOR,
    LOGGER,
)
from .series_coordinator import SeriesCoordinator
from .live_coordinator import LiveCoordinator

PLATFORMS: list[str] = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    series_coordinator = SeriesCoordinator(hass, entry)
    await series_coordinator.async_config_entry_first_refresh()

    live_coordinator = LiveCoordinator(hass, entry)

    # Initial sync FIRST — ensures game_pk is populated correctly
    #LOGGER.warning("🟠 INIT: SERIES DATA BEFORE FIRST SYNC: %s", series_coordinator.data)

    live_coordinator.update_from_series(series_coordinator.data)

    # Attach listener AFTER initial sync — prevents overwriting with None
    live_coordinator.attach_series_coordinator(series_coordinator)

    # Start polling AFTER HA is fully started
    async def _start_later(_):
        await live_coordinator.async_start()

    hass.bus.async_listen_once("homeassistant_started", _start_later)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        SERIES_COORDINATOR: series_coordinator,
        LIVE_COORDINATOR: live_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
