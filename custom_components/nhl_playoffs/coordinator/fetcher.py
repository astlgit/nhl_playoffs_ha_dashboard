from __future__ import annotations

from typing import Any

import aiohttp
import async_timeout

from ..const import API_BRACKET, API_CAROUSEL, API_SCHEDULE, LOGGER


async def fetch_json(session: aiohttp.ClientSession, url: str) -> Any:
    LOGGER.debug("Fetching URL: %s", url)
    async with async_timeout.timeout(10):
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.json()


async def fetch_bracket(session: aiohttp.ClientSession, bracket_year: int) -> dict:
    url = API_BRACKET.format(year=bracket_year)
    return await fetch_json(session, url)


async def fetch_carousel(session: aiohttp.ClientSession, season: str) -> dict:
    url = API_CAROUSEL.format(season=season)
    return await fetch_json(session, url)


async def fetch_schedule_for_series(
    session: aiohttp.ClientSession, season: str, series_letter: str
) -> dict:
    url = API_SCHEDULE.format(season=season, series_letter=series_letter.lower())
    try:
        return await fetch_json(session, url)
    except Exception as err:
        LOGGER.debug("Schedule fetch failed for series %s: %s", series_letter, err)
        return {}
