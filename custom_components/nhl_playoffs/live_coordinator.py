from __future__ import annotations

from typing import Any
import asyncio
from datetime import datetime

from homeassistant.core import HomeAssistant, callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN,
    LOGGER,
    SERIES_LETTERS,
)
from .api.live_api import fetch_live_game


FINAL_COOLDOWN_SECONDS = 120
LIVE_INTERVAL = 10
PRE_1H_INTERVAL = 60
PRE_1_3H_INTERVAL = 600
PRE_3H_INTERVAL = 1800
FUT_INTERVAL = 3600
OFF_INTERVAL = 3600


class LiveCoordinator:
    """Independent per-series live polling with persistence."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        self.state = entry.options.get("live_state", {})

        for letter in SERIES_LETTERS:
            self.state.setdefault(letter, {
                "game_pk": None,
                "state": None,
                "json": None,
                "interval": FUT_INTERVAL,
                "cooldown": 0,
            })

        self.tasks: dict[str, asyncio.Task] = {}

    # -------------------------------------------------------------------------
    # NEW: Receive updates from SeriesCoordinator
    # -------------------------------------------------------------------------
    def update_from_series(self, series_data: dict[str, Any]) -> None:
        for letter, data in series_data.items():
            today_pk = data.get("today_game_pk")
            next_game = data.get("next_game")

            if today_pk:
                self.state[letter]["game_pk"] = today_pk
                self.state[letter]["cooldown"] = 0
                continue

            if next_game:
                self.state[letter]["game_pk"] = next_game.get("game_pk")
                self.state[letter]["cooldown"] = 0
                continue

            self.state[letter]["game_pk"] = None
            self.state[letter]["json"] = None
            self.state[letter]["state"] = None

        self._persist()

    # -------------------------------------------------------------------------
    # Auto-refresh when SeriesCoordinator updates
    # -------------------------------------------------------------------------
    @callback
    def attach_series_coordinator(self, series_coordinator):
        series_coordinator.async_add_listener(
            lambda: self.update_from_series(series_coordinator.data)
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
            except Exception as err:
                LOGGER.error("LiveCoordinator error for %s: %s", letter, err)

            interval = self.state[letter]["interval"]
            await asyncio.sleep(interval)

    async def _update_series(self, letter: str, session) -> None:
        series_state = self.state[letter]
        game_pk = series_state["game_pk"]

        if not game_pk:
            series_state["json"] = None
            series_state["state"] = None
            series_state["interval"] = FUT_INTERVAL
            self._persist()
            return

        live_json = await fetch_live_game(session, game_pk)

        if not live_json:
            series_state["interval"] = FUT_INTERVAL
            self._persist()
            return

        # CRITICAL FIX: inject game_pk into the live JSON
        live_json["game_pk"] = game_pk

        game_state = (live_json.get("gameState") or "").upper()

        # Reset JSON if game_pk changed
        if series_state["json"] and series_state["json"].get("id") != game_pk:
            series_state["json"] = None
            series_state["state"] = None
            series_state["cooldown"] = 0

        # Store updated JSON
        series_state["json"] = live_json
        series_state["state"] = game_state
        series_state["interval"] = self._compute_interval(letter, live_json)

        # Final cooldown logic
        if game_state == "FINAL":
            if series_state["cooldown"] < FINAL_COOLDOWN_SECONDS:
                series_state["cooldown"] += series_state["interval"]
                series_state["interval"] = LIVE_INTERVAL
            else:
                series_state["interval"] = FUT_INTERVAL

        self._persist()

    def _compute_interval(self, letter: str, live_json: dict[str, Any]) -> int:
        game_state = (live_json.get("gameState") or "").upper()

        if game_state in ("LIVE", "CRIT"):
            return LIVE_INTERVAL

        if game_state == "PRE":
            start_str = live_json.get("startTimeUTC")
            if start_str:
                try:
                    start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                    now = datetime.utcnow()
                    diff = (start_dt - now).total_seconds()

                    if diff < 3600:
                        return PRE_1H_INTERVAL
                    if diff < 10800:
                        return PRE_1_3H_INTERVAL
                    return PRE_3H_INTERVAL
                except Exception:
                    return PRE_3H_INTERVAL

        if game_state == "FUT":
            return FUT_INTERVAL

        if game_state == "OFF":
            return OFF_INTERVAL

        return FUT_INTERVAL

    def _persist(self) -> None:
        new_options = dict(self.entry.options)
        new_options["live_state"] = self.state
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
