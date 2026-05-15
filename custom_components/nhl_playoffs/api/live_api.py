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

