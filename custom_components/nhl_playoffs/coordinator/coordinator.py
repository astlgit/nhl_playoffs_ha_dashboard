from __future__ import annotations

from typing import Any
import asyncio

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import aiohttp_client

from ..const import (
    DOMAIN,
    LOGGER,
    UPDATE_INTERVAL,
    CONF_DEBUG,
    CONF_SEASON_MODE,
    CONF_MANUAL_SEASON,
    SEASON_MODE_CURRENT,
    SEASON_MODE_MANUAL,
)

from .season import get_current_season
from .fetcher import fetch_bracket, fetch_carousel, fetch_schedule_for_series
from ..utils.mapping import SERIES_MAP


class NHLPlayoffsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for NHL Playoffs data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        data = entry.data
        options = entry.options

        self.season_mode = options.get(CONF_SEASON_MODE, data.get(CONF_SEASON_MODE, SEASON_MODE_CURRENT))
        self.manual_season = options.get(CONF_MANUAL_SEASON, data.get(CONF_MANUAL_SEASON, ""))

        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            update_interval=UPDATE_INTERVAL,
        )

    @property
    def debug(self) -> bool:
        return bool(self.entry.options.get(CONF_DEBUG, False))

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch and merge NHL playoff data."""
        try:
            auto_season, auto_bracket_year = get_current_season()

            if self.season_mode == SEASON_MODE_MANUAL and self.manual_season:
                season = self.manual_season
                bracket_year = int(self.manual_season[:4])
            else:
                season = auto_season
                bracket_year = auto_bracket_year

            if self.debug:
                LOGGER.debug("Using season=%s bracket_year=%s", season, bracket_year)

            session = aiohttp_client.async_get_clientsession(self.hass)

            # Fetch bracket + carousel
            bracket = await fetch_bracket(session, bracket_year)
            carousel = await fetch_carousel(session, season)

            # Detect active series
            active_series_letters = self._detect_active_series(bracket)

            if self.debug:
                LOGGER.debug("Active series letters: %s", active_series_letters)

            # Fetch schedules
            schedules: dict[str, Any] = {}

            tasks = [
                asyncio.create_task(fetch_schedule_for_series(session, season, letter))
                for letter in active_series_letters
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for letter, result in zip(active_series_letters, results):
                if isinstance(result, Exception):
                    LOGGER.debug("Schedule fetch failed for %s: %s", letter, result)
                    schedules[letter] = {}
                else:
                    schedules[letter] = result

            # Merge all data
            merged = self._merge_data(bracket, carousel, schedules)

            if self.debug:
                LOGGER.debug("Merged playoff data keys: %s", list(merged.keys()))

            return merged

        except Exception as err:
            raise UpdateFailed(f"Error updating NHL Playoffs data: {err}") from err

    def _detect_active_series(self, bracket: dict[str, Any]) -> list[str]:
        letters: list[str] = []

        for item in bracket.get("series", []):
            letter = item.get("seriesLetter")
            if not letter:
                continue

            if item.get("topSeedTeam") and item.get("bottomSeedTeam"):
                letters.append(letter.upper())

        # Always include all series A–O for complete bracket display
        all_letters = [m["series_letter"] for m in SERIES_MAP.values()]
        letters = sorted(set(letters + all_letters))

        return letters

    def _merge_data(
        self,
        bracket: dict[str, Any],
        carousel: dict[str, Any],
        schedules: dict[str, Any],
    ) -> dict[str, Any]:

        data: dict[str, Any] = {}

        # Bracket
        for item in bracket.get("series", []):
            letter = item.get("seriesLetter", "").upper()
            if not letter:
                continue
            data.setdefault(letter, {})
            data[letter]["bracket"] = item

        # Carousel
        for item in carousel.get("series", []):
            letter = item.get("seriesLetter", "").upper()
            if not letter:
                continue
            data.setdefault(letter, {})
            data[letter]["carousel"] = item

        # Schedules
        for letter, sched in schedules.items():
            data.setdefault(letter, {})
            data[letter]["schedule"] = sched

        # Ensure all A–O exist
        for meta in SERIES_MAP.values():
            letter = meta["series_letter"]
            data.setdefault(letter, {})

        return data
