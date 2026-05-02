from __future__ import annotations

from typing import Any, Dict
import aiohttp
import async_timeout

from ..const import LOGGER, API_LIVE_GAME


async def fetch_live_game(session: aiohttp.ClientSession, game_pk: int) -> Dict[str, Any]:
    """
    Fetch live play-by-play data for a specific gamePk.
    This is the ONLY live endpoint we trust for playoffs.
    """
    if not game_pk:
        LOGGER.debug("fetch_live_game called with empty game_pk")
        return {}

    url = API_LIVE_GAME.format(gamePk=game_pk)
    LOGGER.debug("Fetching live data for gamePk=%s", game_pk)

    try:
        async with async_timeout.timeout(10):
            async with session.get(url) as resp:
                resp.raise_for_status()
                data = await resp.json()
    except Exception as err:
        LOGGER.error("Failed to fetch live game %s: %s", game_pk, err)
        return {}

    return normalize_live_data(data)


def normalize_live_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize the modern NHL live API structure into a clean, predictable dict.
    This ensures sensors never break when the API changes fields.
    """

    if not raw:
        return {}

    # Basic game state
    game_state = raw.get("gameState", "")
    period = raw.get("periodDescriptor", {}).get("number")
    period_ordinal = raw.get("periodDescriptor", {}).get("ordinalNum")
    time_remaining = raw.get("clock", {}).get("timeRemaining")
    is_intermission = raw.get("clock", {}).get("inIntermission", False)

    # Teams
    away = raw.get("awayTeam", {})
    home = raw.get("homeTeam", {})

    return {
        "game_state": game_state,
        "current_period": period,
        "current_period_ordinal": period_ordinal,
        "time_remaining": time_remaining,
        "is_intermission": is_intermission,

        # Scores
        "away_score": away.get("score"),
        "home_score": home.get("score"),

        # Team info
        "away_team": away.get("abbrev"),
        "home_team": home.get("abbrev"),
        "away_logo": away.get("logo"),
        "home_logo": home.get("logo"),

        # Shots
        "away_shots": away.get("sog"),
        "home_shots": home.get("sog"),

        # Raw payload (optional for debugging)
        "raw": raw,
    }
