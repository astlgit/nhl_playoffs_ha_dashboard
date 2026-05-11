from __future__ import annotations

from typing import Any
import asyncio
from datetime import datetime

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN,
    LOGGER,
    SERIES_LETTERS,
)
from .api.live_api import fetch_live_game
from .utils.mapping_bracket import SERIES_MAP

# INTERVALS
LIVE_INTERVAL = 5          # LIVE + CRIT
PRE_INTERVAL = 30          # PRE (and FUT < 30 min)
FUT_LT3H_INTERVAL = 300    # FUT < 3 hours
FUT_GT3H_INTERVAL = 3600   # FUT > 3 hours
OFF_INTERVAL = 3600        # OFF / FINAL
FINAL_COOLDOWN_SECONDS = 120
DEFAULT_INTERVAL = 360


class LiveCoordinator:
    """Independent per-series live polling with correct legacy-format parsing."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        # Load persisted state, but DO NOT trust game_pk/json/state
        persisted = entry.options.get("live_state", {})

        self.state = {}
        for letter in SERIES_LETTERS:
            prev = persisted.get(letter, {})
            self.state[letter] = {
                "game_pk": None,                     # always reset
                "json": None,                        # always reset
                "state": None,                       # always reset
                "interval": prev.get("interval", FUT_GT3H_INTERVAL),
                "cooldown": prev.get("cooldown", 0),
            }

        self.tasks: dict[str, asyncio.Task] = {}
        self._listeners: list[callable] = []

    # -------------------------------------------------------------------------
    # Listener registration
    # -------------------------------------------------------------------------
    def add_listener(self, callback):
        self._listeners.append(callback)

    def _notify_listeners(self):
        for callback in list(self._listeners):
            try:
                callback()
            except Exception as err:
                LOGGER.error("LiveCoordinator listener failed: %s", err)


    @callback
    def attach_series_coordinator(self, series_coordinator):
        series_coordinator.async_add_listener(
            lambda: self.update_from_series(series_coordinator.data)
        )

    @callback
    def update_from_series(self, series_data: dict[str, Any]) -> None:
        """Receive game_pk from the Series API and store it for live polling."""
        for letter, data in series_data.items():
            today = data.get("today_game")
            next_game = data.get("next_game")

            # TODAY'S GAME TAKES PRIORITY
            if today:
                self.state[letter]["game_pk"] = today["game_pk"]
                self.state[letter]["json"] = None

                LOGGER.warning(
                    "SERIES→LIVE HANDOFF %s: TODAY game_pk=%s",
                    letter,
                    today["game_pk"],
                )
                continue

            # NEXT GAME (future)
            if next_game:
                self.state[letter]["game_pk"] = next_game["game_pk"]
                self.state[letter]["json"] = None

                LOGGER.warning(
                    "SERIES→LIVE HANDOFF %s: NEXT game_pk=%s",
                    letter,
                    next_game["game_pk"],
                )
                continue

            # NO GAME
            self.state[letter]["game_pk"] = None
            self.state[letter]["json"] = None

            LOGGER.warning(
                "SERIES→LIVE HANDOFF %s: NO GAME (game_pk=None)",
                letter,
            )

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    def get_series(self, letter: str) -> dict[str, Any]:
        return self.state.get(letter, {})

    async def async_start(self) -> None:
        for letter in SERIES_LETTERS:
            if letter not in self.tasks:
                self.tasks[letter] = asyncio.create_task(self._poll_series(letter))

    async def _poll_series(self, letter: str) -> None:
        session = aiohttp_client.async_get_clientsession(self.hass)

        while True:
            try:
                await self._update_series(letter, session)
                #LOGGER.warning("UPDATE_SERIES %s game_pk=%s", letter, self.state[letter]["game_pk"])
            except Exception as err:
                LOGGER.error("LiveCoordinator error for %s: %s", letter, err)

            await asyncio.sleep(self.state[letter]["interval"])

    # -------------------------------------------------------------------------
    # Main update logic
    # -------------------------------------------------------------------------
    async def _update_series(self, letter: str, session) -> None:
        series_state = self.state[letter]
        game_pk = series_state["game_pk"]

        if not game_pk:
            series_state["json"] = None
            series_state["state"] = None
            series_state["interval"] = FUT_GT3H_INTERVAL

            LOGGER.warning(
                "LIVE POLL %s: NO game_pk → idle interval=%s",
                letter,
                series_state["interval"],
            )

            self._persist()
            self._notify_listeners()
            return

        parsed = await fetch_live_game(session, game_pk)
        if not parsed:
            series_state["interval"] = FUT_GT3H_INTERVAL

            LOGGER.warning(
                "LIVE POLL %s: fetch failed for game_pk=%s → interval=%s",
                letter,
                game_pk,
                series_state["interval"],
            )

            self._persist()
            self._notify_listeners()
            return

        game_state = parsed.get("game_state", "").upper()

        series_state["json"] = parsed
        series_state["state"] = game_state

        # Compute interval
        series_state["interval"] = self._compute_interval(parsed)

        LOGGER.warning(
            "LIVE POLL %s: game_pk=%s state=%s interval=%s",
            letter,
            game_pk,
            game_state,
            series_state["interval"],
        )

        self._persist()
        self._notify_listeners()



    # -------------------------------------------------------------------------
    # Interval logic (legacy-format aware)
    # -------------------------------------------------------------------------
    def _compute_interval(self, live_json: dict[str, Any]) -> int:
        # Prefer parsed normalized state
        state = (
            live_json.get("game_state")  # your normalized field
            or live_json.get("gameState")  # raw NHL field
            or ""
        ).upper()

        start_str = live_json.get("startTimeUTC")

        # LIVE / CRIT
        if state in ("LIVE", "CRIT"):
            return LIVE_INTERVAL  # 5 seconds

        # PRE
        if state in ("PRE", "OVER"):
            return PRE_INTERVAL  # 30 seconds

        # FUT (time-based)
        if state == "FUT":
            try:
                start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                now = datetime.utcnow()
                diff = (start_dt - now).total_seconds()

                # Prevent negative values
                diff = max(diff, 0)

                if diff > 3 * 3600:
                    return FUT_GT3H_INTERVAL  # 3600
                if diff > 60 * 60:
                    return FUT_LT3H_INTERVAL  # 300
                return PRE_INTERVAL  # < 60 minutes → 30 seconds

            except Exception:
                return DEFAULT_INTERVAL


        # FINAL → 120 seconds
        if state == "FINAL":
            return FINAL_COOLDOWN_SECONDS

        # OFF → 3600 seconds
        if state == "OFF":
            return OFF_INTERVAL

        # Default
        return DEFAULT_INTERVAL

    # -------------------------------------------------------------------------
    # Persistence
    # -------------------------------------------------------------------------
    def _persist(self) -> None:
        new_options = dict(self.entry.options)
        new_options["live_state"] = self.state
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
