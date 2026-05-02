from __future__ import annotations

from typing import Any, Optional
import asyncio
from datetime import datetime

import pytz
import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import aiohttp_client

from .const import (
    DOMAIN,
    LOGGER,
    UPDATE_INTERVAL,
    CONF_DEBUG,
    CONF_SEASON_MODE,
    CONF_MANUAL_SEASON,
    SEASON_MODE_CURRENT,
    SEASON_MODE_MANUAL,
    API_SCHEDULE_NOW,
)
from .utils.season import get_current_season
from .api.fetcher import (
    fetch_bracket,
    fetch_carousel,
    fetch_series_details,
)
from .utils.mapping_bracket import SERIES_MAP


class SeriesCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator for slow-changing NHL Playoffs data."""

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

    def to_local(self, dt_str: str) -> Optional[datetime]:
        if not dt_str:
            return None
        try:
            dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        except Exception:
            return None
        local_tz = pytz.timezone(self.hass.config.time_zone)
        return dt.astimezone(local_tz)

    def compute_next_game(self, series_obj: dict[str, Any]) -> dict[str, Any] | None:
        games = series_obj.get("games", [])
        if not games:
            return None

        needed = series_obj.get("neededToWin")
        top_wins = series_obj.get("topSeedTeam", {}).get("seriesWins", 0)
        bottom_wins = series_obj.get("bottomSeedTeam", {}).get("seriesWins", 0)

        if top_wins == needed or bottom_wins == needed:
            return None

        for g in games:
            if g.get("gameState") != "FUT":
                continue
            if g.get("ifNecessary") and (top_wins == needed or bottom_wins == needed):
                continue
            return {
                "game_pk": g.get("id"),
                "start_time": g.get("startTimeUTC"),
                "home": g.get("homeTeam", {}).get("abbrev"),
                "away": g.get("awayTeam", {}).get("abbrev"),
                "game_number": g.get("gameNumber"),
            }

        return None

    async def _fetch_schedule_now(self, session: aiohttp.ClientSession) -> dict[str, Any]:
        try:
            async with async_timeout.timeout(10):
                async with session.get(API_SCHEDULE_NOW) as resp:
                    resp.raise_for_status()
                    return await resp.json()
        except Exception as err:
            LOGGER.error("Failed to fetch schedule/now: %s", err)
            return {}

    def _build_today_games_from_schedule(
        self,
        schedule_now: dict[str, Any],
    ) -> dict[str, dict[str, Any]]:
        today_games: dict[str, dict[str, Any]] = {}

        local_tz = pytz.timezone(self.hass.config.time_zone)
        today = datetime.now(local_tz).date()

        for day in schedule_now.get("gameWeek", []):
            for g in day.get("games", []):
                series_status = g.get("seriesStatus") or {}
                letter = series_status.get("seriesLetter")
                if not letter:
                    continue

                letter = letter.upper()
                start_str = g.get("startTimeUTC")
                if not start_str:
                    continue

                try:
                    dt_utc = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                    dt_local = dt_utc.astimezone(local_tz)
                except Exception:
                    continue

                if dt_local.date() == today:
                    today_games[letter] = {
                        "game_pk": g.get("id"),
                        "start_time": start_str,
                        "home": g.get("homeTeam", {}).get("abbrev"),
                        "away": g.get("awayTeam", {}).get("abbrev"),
                        "game_number": series_status.get("gameNumberOfSeries"),
                        "game_state": g.get("gameState"),
                    }

        return today_games

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

            bracket, carousel, schedule_now = await asyncio.gather(
                fetch_bracket(session, bracket_year),
                fetch_carousel(session, season),
                self._fetch_schedule_now(session),
            )

            active_series_letters = self._detect_active_series(bracket)

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

            self.next_games = {
                letter: self.compute_next_game(series_obj)
                for letter, series_obj in self.series_details.items()
            }

            self.today_games = self._build_today_games_from_schedule(schedule_now)

            return self._merge_data(bracket, carousel)

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

        all_letters = [m["series_letter"] for m in SERIES_MAP.values()]
        return sorted(set(letters + all_letters))

    def _merge_data(self, bracket: dict[str, Any], carousel: dict[str, Any]) -> dict[str, Any]:
        data: dict[str, Any] = {}

        for item in bracket.get("series", []):
            letter = item.get("seriesLetter", "").upper()
            if not letter:
                continue
            data.setdefault(letter, {})
            data[letter]["bracket"] = item

        for item in carousel.get("series", []):
            letter = item.get("seriesLetter", "").upper()
            if not letter:
                continue
            data.setdefault(letter, {})
            data[letter]["carousel"] = item

        for letter, details in self.series_details.items():
            data.setdefault(letter, {})
            data[letter]["series_details"] = details

        for letter, next_game in self.next_games.items():
            data.setdefault(letter, {})
            data[letter]["next_game"] = next_game

        for letter, today in self.today_games.items():
            data.setdefault(letter, {})
            data[letter]["today_game"] = today
            data[letter]["today_game_pk"] = today.get("game_pk")

        for meta in SERIES_MAP.values():
            letter = meta["series_letter"]
            data.setdefault(letter, {})

        return data
