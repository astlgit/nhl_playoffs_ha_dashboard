from __future__ import annotations

import asyncio

from homeassistant.core import HomeAssistant

from .season import Season
from ..const import LOGGER


class NHLPlayoffsFetcher:
    """Fetch NHL playoffs data from the configured source."""

    def __init__(self, hass: HomeAssistant, season: Season) -> None:
        self.hass = hass
        self.season = season

    async def async_update(self) -> dict[str, object]:
        LOGGER.debug("Fetching NHL playoff data for season %s", self.season.display_season)
        await asyncio.sleep(0)
        return {
            "season": self.season.display_season,
            "series": {},
        }
