from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity

from ..const import DOMAIN, LOGGER, SERIES_COORDINATOR, LIVE_COORDINATOR
from ..utils.parsing_live import parse_live_game


class LiveSeriesSensor(SensorEntity):
    """Live game sensor driven entirely by LiveCoordinator timing."""

    _attr_should_poll = False

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

        self._state = "normal"
        self._attr_extra_state_attributes = {}

    async def async_added_to_hass(self):
        """Register for coordinator updates."""
        #LOGGER.warning("LiveSeriesSensor registered listener for %s", self.series_key)

        # LiveCoordinator updates
        self.live_coordinator.add_listener(
            lambda: self.hass.async_create_task(self._handle_coordinator_update())
        )

        # SeriesCoordinator updates (today/next game)
        self.series_coordinator.async_add_listener(
            lambda: self.hass.async_create_task(self._handle_coordinator_update())
        )

        # Initial state
        await self._handle_coordinator_update()

    async def _handle_coordinator_update(self):
        """Refresh state from coordinators."""
        #LOGGER.warning("LiveSeriesSensor UPDATE fired for %s", self.series_key)
        #LOGGER.warning("🔴 SENSOR UPDATE: series_key=%s series_letter=%s", self.series_key, self.series_letter)
        #LOGGER.warning("🔍 SENSOR %s USING LETTER=%s", self.series_key, self.series_letter)

        try:
            live_state = self.live_coordinator.get_series(self.series_letter)

            # If coordinator hasn't populated JSON yet
            if not live_state or live_state.get("json") is None:
                self._attr_extra_state_attributes = {
                    "game_pk": live_state.get("game_pk")
                }
                return

            raw_json = live_state["json"]

            self._attr_extra_state_attributes = {
                "game_pk": live_state.get("game_pk")
            }

            # ---------------------------------------------------------
            # LIVE GAME
            # ---------------------------------------------------------
            if raw_json:
                parsed = raw_json  # already parsed by coordinator
                self._attr_extra_state_attributes.update(parsed)

                game_state = parsed.get("game_state", "")

                if game_state in ("LIVE", "CRIT", "PRE", "OVER", "FINAL"):
                    self._state = "live"
                elif game_state == "OFF":
                    self._state = "final"
                else:
                    self._state = "normal"

                self.async_write_ha_state()
                return

            # ---------------------------------------------------------
            # TODAY'S GAME
            # ---------------------------------------------------------
            series_data = self.series_coordinator.data.get(self.series_letter, {})
            today = series_data.get("today_game")
            next_game = series_data.get("next_game")

            if today:
                self._state = today.get("game_state", "normal")
                self._attr_extra_state_attributes.update(today)
                self.async_write_ha_state()
                return

            # ---------------------------------------------------------
            # FUTURE GAME
            # ---------------------------------------------------------
            if next_game:
                self._state = "FUT"
                self._attr_extra_state_attributes.update(next_game)
                self.async_write_ha_state()
                return

            # ---------------------------------------------------------
            # NO GAME
            # ---------------------------------------------------------
            self._state = "normal"
            self.async_write_ha_state()

        except Exception as err:
            LOGGER.error("LiveSeriesSensor update failed for %s: %s", self.series_key, err)

    @property
    def native_value(self) -> str:
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attr_extra_state_attributes
