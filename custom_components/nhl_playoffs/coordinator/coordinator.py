from __future__ import annotations

from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .fetcher import NHLPlayoffsFetcher
from .season import Season
from ..const import DOMAIN, LOGGER


class NHLPlayoffsCoordinator(DataUpdateCoordinator):
    """Coordinator for NHL Playoffs data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self.season = Season(entry.data)
        self.fetcher = NHLPlayoffsFetcher(hass, self.season)

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=15),
            update_method=self._async_update_data,
        )

    async def _async_update_data(self) -> dict[str, object]:
        try:
            return await self.fetcher.async_update()
        except Exception as err:
            raise UpdateFailed(err) from err
