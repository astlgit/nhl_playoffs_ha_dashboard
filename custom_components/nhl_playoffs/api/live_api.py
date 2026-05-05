from __future__ import annotations

from typing import Any, Dict
import aiohttp
import async_timeout

from ..const import LOGGER, API_LIVE_GAME
from ..utils.parsing_live import parse_live_game


async def fetch_live_game(session: aiohttp.ClientSession, game_pk: int) -> Dict[str, Any]:
    """Fetch live play-by-play data for a specific gamePk (legacy format only)."""
    if not game_pk:
        return {}

    url = API_LIVE_GAME.format(gamePk=game_pk)

    try:
        async with async_timeout.timeout(10):
            resp = await session.get(url)
            resp.raise_for_status()
            data = await resp.json()

            # Parse the live JSON using the unified parser
            parsed = parse_live_game(data)

            # The NHL API does NOT include game_pk in the JSON,
            # so we must reattach it here.
            parsed["game_pk"] = game_pk

            return parsed

    except Exception as err:
        LOGGER.error("Failed to fetch live game %s: %s", game_pk, err)
        return {}


""""def normalize_live_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    #Normalize the REAL legacy NHL live API format (FUT, PRE, LIVE, OFF, FINAL).

    if not raw:
        return {}

    # -------------------------------------------------------------------------
    # GAME STATE
    # -------------------------------------------------------------------------
    game_state = (raw.get("gameState") or "").upper()

    # -------------------------------------------------------------------------
    # TEAMS
    # -------------------------------------------------------------------------
    away = raw.get("awayTeam", {})
    home = raw.get("homeTeam", {})

    away_team = away.get("abbrev")
    home_team = home.get("abbrev")

    away_score = away.get("score")
    home_score = home.get("score")

    away_logo = away.get("logo")
    home_logo = home.get("logo")

    away_shots = away.get("sog")
    home_shots = home.get("sog")

    # -------------------------------------------------------------------------
    # CLOCK + PERIOD
    # -------------------------------------------------------------------------
    clock = raw.get("clock", {})
    time_remaining = clock.get("timeRemaining")
    is_intermission = clock.get("inIntermission", False)

    # Legacy games use displayPeriod for LIVE/OFF/FUT
    period = raw.get("displayPeriod") or raw.get("periodDescriptor", {}).get("number")

    # -------------------------------------------------------------------------
    # OUTPUT (normalized)
    # -------------------------------------------------------------------------
    return {
        "game_state": game_state,
        "current_period": period,
        "current_period_ordinal": None,  # parse_live_game computes this
        "time_remaining": time_remaining,
        "is_intermission": is_intermission,
        "away_score": away_score,
        "home_score": home_score,
        "away_team": away_team,
        "home_team": home_team,
        "away_logo": away_logo,
        "home_logo": home_logo,
        "away_shots": away_shots,
        "home_shots": home_shots,
        "raw": raw,
    }"""
