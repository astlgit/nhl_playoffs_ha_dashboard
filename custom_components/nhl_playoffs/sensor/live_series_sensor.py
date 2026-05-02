from __future__ import annotations

from datetime import timedelta
from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity

from ..const import DOMAIN, LOGGER, SERIES_COORDINATOR, LIVE_COORDINATOR
from ..utils.parsing_live import parse_live_game


SCAN_INTERVAL_NORMAL = timedelta(seconds=60)
SCAN_INTERVAL_LIVE = timedelta(seconds=10)
SCAN_INTERVAL_FINAL = timedelta(seconds=300)
SCAN_INTERVAL_SERIES_OVER = timedelta(hours=1)


class LiveSeriesSensor(SensorEntity):
    """Unified live sensor for a single playoff series."""

    _attr_should_poll = True

    def __init__(self, hass, entry, series_key: str, meta: dict[str, Any]) -> None:
        self.hass = hass
        self.entry = entry

        self.series_key = series_key
        self.series_letter = meta["series_letter"]

        self._attr_name = f"Live {series_key.upper()}"
        self._attr_unique_id = f"{DOMAIN}_live_{series_key}"
        self.entity_id = f"sensor.live_{series_key}"

        data = hass.data[DOMAIN][entry.entry_id]
        self.series_coordinator = data[SERIES_COORDINATOR]
        self.live_coordinator = data[LIVE_COORDINATOR]

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
        """Update using LiveCoordinator + SeriesCoordinator with clean parsing."""
        try:
            live_state = self.live_coordinator.get_series(self.series_letter)
            raw_json = live_state.get("json")

            # Always include game_pk
            self._attr_extra_state_attributes = {
                "game_pk": live_state.get("game_pk")
            }

            # ---------------------------------------------------------
            # LIVE GAME
            # ---------------------------------------------------------
            if raw_json:
                parsed = parse_live_game(raw_json)
                self._attr_extra_state_attributes.update(parsed)

                game_state = parsed["game_state"]

                if game_state == "LIVE":  # CRIT already normalized in parser
                    self._state = "live"
                    self._scan_interval = SCAN_INTERVAL_LIVE

                elif game_state == "FINAL":
                    self._state = "final"
                    self._scan_interval = SCAN_INTERVAL_FINAL

                else:
                    self._state = "normal"
                    self._scan_interval = SCAN_INTERVAL_NORMAL

                return

            # ---------------------------------------------------------
            # TODAY'S GAME (not live yet)
            # ---------------------------------------------------------
            series_data = self.series_coordinator.data.get(self.series_letter, {})
            today = series_data.get("today_game")
            next_game = series_data.get("next_game")

            if today:
                self._state = today.get("game_state", "normal")
                self._attr_extra_state_attributes.update(today)
                self._scan_interval = SCAN_INTERVAL_NORMAL
                return

            # ---------------------------------------------------------
            # FUTURE GAME
            # ---------------------------------------------------------
            if next_game:
                self._state = "FUT"
                self._attr_extra_state_attributes.update(next_game)
                self._scan_interval = SCAN_INTERVAL_NORMAL
                return

            # ---------------------------------------------------------
            # NO GAME
            # ---------------------------------------------------------
            self._state = "normal"
            self._scan_interval = SCAN_INTERVAL_SERIES_OVER

        except Exception as err:
            LOGGER.error("Live sensor update failed for %s: %s", self.series_key, err)
            self._scan_interval = SCAN_INTERVAL_NORMAL
