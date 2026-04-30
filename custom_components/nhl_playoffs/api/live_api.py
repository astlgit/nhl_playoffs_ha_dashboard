from __future__ import annotations

from typing import Any, List, Dict
import datetime

import aiohttp
import async_timeout

from ..const import LOGGER


NHL_SCHEDULE_URL = "https://statsapi.web.nhl.com/api/v1/schedule"


async def fetch_today_games(session: aiohttp.ClientSession) -> List[Dict[str, Any]]:
    """Fetch all NHL games scheduled for today (regular season + playoffs)."""
    today = datetime.date.today().strftime("%Y-%m-%d")

    params = {
        "date": today,
        "expand": "schedule.linescore,schedule.game.seriesSummary"
    }

    LOGGER.debug("Fetching today's NHL games for %s", today)

    try:
        async with async_timeout.timeout(10):
            async with session.get(NHL_SCHEDULE_URL, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
    except Exception as err:
        LOGGER.error("Failed to fetch today's NHL games: %s", err)
        return []

    dates = data.get("dates", [])
    if not dates:
        return []

    return dates[0].get("games", [])


def filter_playoff_games(games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return only playoff games from today's schedule."""
    playoff_games: List[Dict[str, Any]] = []

    for game in games:
        if game.get("gameType") == "P":
            playoff_games.append(game)

    return playoff_games
