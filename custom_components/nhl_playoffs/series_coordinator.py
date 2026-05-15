from __future__ import annotations

from typing import Any, Optional
import asyncio
from datetime import datetime, timezone

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import aiohttp_client
from homeassistant.util.dt import get_time_zone

from .const import (
    DOMAIN,
    LOGGER,
    UPDATE_INTERVAL,
    CONF_DEBUG,
    CONF_SEASON_MODE,
    CONF_MANUAL_SEASON,
    SEASON_MODE_CURRENT,
    SEASON_MODE_MANUAL,
)
from .utils.season import get_current_season
from .api.fetcher import (
    fetch_bracket,
    fetch_carousel,
    fetch_series_details,
)
from .utils.mapping_bracket import SERIES_MAP


class SeriesCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for NHL Playoffs data using series endpoint as authoritative source."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry

        data = entry.data
        options = entry.options

        self.season_mode = options.get(
            CONF_SEASON_MODE,
            data.get(CONF_SEASON_MODE, SEASON_MODE_CURRENT),
        )
        self.manual_season = options.get(
            CONF_MANUAL_SEASON,
            data.get(CONF_MANUAL_SEASON, ""),
        )

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_series",
            update_interval=UPDATE_INTERVAL,
        )

    @property
    def debug(self) -> bool:
        return bool(self.entry.options.get(CONF_DEBUG, False))

    # -------------------------------------------------------------------------
    # NEXT GAME (from series endpoint)
    # -------------------------------------------------------------------------

    def compute_next_game(self, series_obj: dict[str, Any]) -> dict[str, Any] | None:
        games = series_obj.get("games", [])
        if not games:
            return None

        parsed = []
        for g in games:
            start = g.get("startTimeUTC")
            if not start:
                continue
            try:
                dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            except Exception:
                continue
            parsed.append((dt, g))

        if not parsed:
            return None

        parsed.sort(key=lambda x: x[0])
        now = datetime.now(timezone.utc)   # FIXED

        for dt, g in parsed:
            if dt > now:
                return {
                    "game_pk": g.get("id"),
                    "start_time": g.get("startTimeUTC"),
                    "home": g.get("homeTeam", {}).get("abbrev"),
                    "away": g.get("awayTeam", {}).get("abbrev"),
                    "game_number": g.get("gameNumber"),
                }

        return None

    # -------------------------------------------------------------------------
    # TODAY'S GAME (from series endpoint)
    # -------------------------------------------------------------------------
    def compute_today_game(self, series_obj: dict[str, Any]) -> dict[str, Any] | None:
        games = series_obj.get("games", [])
        if not games:
            return None

        local_tz = get_time_zone(self.hass.config.time_zone)
        today = datetime.now(local_tz).date()

        parsed = []
        for g in games:
            start = g.get("startTimeUTC")
            if not start:
                continue
            try:
                dt_utc = datetime.fromisoformat(start.replace("Z", "+00:00"))
                dt_local = dt_utc.astimezone(local_tz)
            except Exception:
                continue
            parsed.append((dt_local, g))

        if not parsed:
            return None

        # 1. LIVE game takes priority
        for dt, g in parsed:
            if g.get("gameState") in ("LIVE", "CRIT", "IN_PROGRESS"):
                return {
                    "game_pk": g.get("id"),
                    "start_time": g.get("startTimeUTC"),
                    "home": g.get("homeTeam", {}).get("abbrev"),
                    "away": g.get("awayTeam", {}).get("abbrev"),
                    "game_number": g.get("gameNumber"),
                    "game_state": g.get("gameState"),
                }

        # 2. Game scheduled for today
        for dt, g in parsed:
            if dt.date() == today:
                return {
                    "game_pk": g.get("id"),
                    "start_time": g.get("startTimeUTC"),
                    "home": g.get("homeTeam", {}).get("abbrev"),
                    "away": g.get("awayTeam", {}).get("abbrev"),
                    "game_number": g.get("gameNumber"),
                    "game_state": g.get("gameState"),
                }

        return None


    # -------------------------------------------------------------------------
    # MAIN UPDATE
    # -------------------------------------------------------------------------
    async def _async_update_data(self) -> dict[str, Any]:
        try:
            auto_season, auto_bracket_year = get_current_season()

            if self.season_mode == SEASON_MODE_MANUAL and self.manual_season:
                season = self.manual_season
                bracket_year = int(self.manual_season[:4])
            else:
                season = auto_season
                bracket_year = auto_bracket_year

            session = aiohttp_client.async_get_clientsession(self.hass)

            # Fetch bracket + carousel
            bracket, carousel = await asyncio.gather(
                fetch_bracket(session, bracket_year),
                fetch_carousel(session, season),
            )

            # Determine active series
            active_series_letters = self._detect_active_series(bracket)

            # Fetch series details
            self.series_details = {}
            tasks = [
                asyncio.create_task(fetch_series_details(session, season, letter))
                for letter in active_series_letters
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for letter, result in zip(active_series_letters, results):
                if isinstance(result, Exception):
                    self.series_details[letter] = {}
                else:
                    self.series_details[letter] = result

            # Build next game + today game from series endpoint
            self.next_games = {
                letter: self.compute_next_game(series_obj)
                for letter, series_obj in self.series_details.items()
            }

            self.today_games = {
                letter: self.compute_today_game(series_obj)
                for letter, series_obj in self.series_details.items()
            }

            return self._merge_data(bracket, carousel)

        except Exception as err:
            raise UpdateFailed(f"Error updating NHL Playoffs data: {err}") from err

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------
    def _detect_active_series(self, bracket: dict[str, Any]) -> list[str]:
        letters: list[str] = []

        for item in bracket.get("series", []):
            letter = item.get("seriesLetter")
            if not letter:
                continue
            if item.get("topSeedTeam") and item.get("bottomSeedTeam"):
                letters.append(letter.upper())

        all_letters = [m["series_letter"] for m in SERIES_MAP.values()]
        return sorted(set(letters + all_letters))

    def _merge_data(self, bracket: dict[str, Any], carousel: dict[str, Any]) -> dict[str, Any]:
        data: dict[str, Any] = {}

        # ---------------------------------------------------------
        # BRACKET DATA
        # ---------------------------------------------------------
        for item in bracket.get("series", []):
            letter = item.get("seriesLetter", "").upper()
            if not letter:
                continue
            data.setdefault(letter, {})
            data[letter]["bracket"] = item

        # ---------------------------------------------------------
        # CAROUSEL DATA
        # ---------------------------------------------------------
        for item in carousel.get("series", []):
            letter = item.get("seriesLetter", "").upper()
            if not letter:
                continue
            data.setdefault(letter, {})
            data[letter]["carousel"] = item

        # ---------------------------------------------------------
        # SERIES DETAILS
        # ---------------------------------------------------------
        for letter, details in self.series_details.items():
            data.setdefault(letter, {})
            data[letter]["series_details"] = details

        # ---------------------------------------------------------
        # NEXT GAME
        # ---------------------------------------------------------
        for letter, next_game in self.next_games.items():
            data.setdefault(letter, {})
            data[letter]["next_game"] = next_game or None
            data[letter]["next_game_pk"] = next_game.get("game_pk") if next_game else None
            data[letter]["next_game_time"] = next_game.get("start_time") if next_game else None
            data[letter]["next_game_number"] = next_game.get("game_number") if next_game else None

        # ---------------------------------------------------------
        # TODAY GAME
        # ---------------------------------------------------------
        for letter, today in self.today_games.items():
            data.setdefault(letter, {})
            data[letter]["today_game"] = today or None
            data[letter]["today_game_pk"] = today.get("game_pk") if today else None

        # ---------------------------------------------------------
        # ENSURE ALL SERIES LETTERS EXIST
        # ---------------------------------------------------------
        for meta in SERIES_MAP.values():
            letter = meta["series_letter"]
            data.setdefault(letter, {})

            # Ensure all keys exist even if None
            data[letter].setdefault("bracket", {})
            data[letter].setdefault("carousel", {})
            data[letter].setdefault("series_details", {})

            data[letter].setdefault("next_game", None)
            data[letter].setdefault("next_game_pk", None)
            data[letter].setdefault("next_game_time", None)
            data[letter].setdefault("next_game_number", None)

            data[letter].setdefault("today_game", None)
            data[letter].setdefault("today_game_pk", None)

        return data
