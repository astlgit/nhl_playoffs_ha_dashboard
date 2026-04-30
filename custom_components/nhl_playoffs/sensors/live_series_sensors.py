from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import aiohttp_client

from ..const import DOMAIN, LOGGER
from ..api.live_api import fetch_today_games, filter_playoff_games
from ..utils.mapping import SERIES_MAP, get_series_key_from_live_game
from ..utils.parsing import parse_live_game


# Polling speeds
SCAN_INTERVAL_NORMAL = timedelta(seconds=60)
SCAN_INTERVAL_LIVE = timedelta(seconds=10)
SCAN_INTERVAL_FINAL = timedelta(seconds=300)
SCAN_INTERVAL_SERIES_OVER = timedelta(hours=1)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up 15 unified live sensors."""
    session = aiohttp_client.async_get_clientsession(hass)

    sensors = []
    for series_key, meta in SERIES_MAP.items():
        sensors.append(
            LiveSeriesSensor(
                hass=hass,
                session=session,
                entry=entry,
                series_key=series_key,
                meta=meta,
            )
        )

    async_add_entities(sensors)


class LiveSeriesSensor(SensorEntity):
    """Unified live sensor for a single playoff series."""

    _attr_should_poll = True

    def __init__(
        self,
        hass: HomeAssistant,
        session,
        entry: ConfigEntry,
        series_key: str,
        meta: Dict[str, Any],
    ) -> None:
        self.hass = hass
        self.session = session
        self.entry = entry

        self.series_key = series_key
        self.series_letter = meta["series_letter"]
        self._attr_name = f"NHL Live {meta['name']}"
        self._attr_unique_id = f"{DOMAIN}_live_{series_key}"

        self._attr_extra_state_attributes = {}
        self._state = "normal"

        self._scan_interval = SCAN_INTERVAL_NORMAL

    @property
    def native_value(self) -> str:
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attr_extra_state_attributes

    @property
    def should_poll(self) -> bool:
        return True

    @property
    def scan_interval(self) -> timedelta:
        return self._scan_interval

    async def async_update(self) -> None:
        """Poll the live API and update sensor state."""
        try:
            games = await fetch_today_games(self.session)
            playoff_games = filter_playoff_games(games)

            # Find the game for this series
            game = self._find_game_for_series(playoff_games)

            if not game:
                # No game today for this series
                self._state = "normal"
                self._attr_extra_state_attributes = {}
                self._scan_interval = SCAN_INTERVAL_NORMAL
                return

            parsed = parse_live_game(game)
            self._attr_extra_state_attributes = parsed

            game_state = parsed["game_state"]

            # Determine sensor state
            if game_state in ("Live", "In Progress"):
                self._state = "live"
                self._scan_interval = SCAN_INTERVAL_LIVE

            elif game_state == "Final":
                self._state = "final"
                self._scan_interval = SCAN_INTERVAL_FINAL

            else:
                # Preview, warmup, scheduled
                self._state = "normal"
                self._scan_interval = SCAN_INTERVAL_NORMAL

        except Exception as err:
            LOGGER.error("Live sensor update failed for %s: %s", self.series_key, err)
            self._scan_interval = SCAN_INTERVAL_NORMAL

    def _find_game_for_series(self, games: list[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Return the game object for this sensor's series."""
        for game in games:
            key = get_series_key_from_live_game(game)
            if key == self.series_key:
                return game
        return None
