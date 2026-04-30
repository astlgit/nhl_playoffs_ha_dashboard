from __future__ import annotations

from datetime import datetime


def get_current_season() -> tuple[str, int]:
    """Return (season_str, bracket_year)."""
    now = datetime.now()
    year = now.year
    month = now.month

    if month >= 7:
        season_start = year
        season_end = year + 1
    else:
        season_start = year - 1
        season_end = year

    season = f"{season_start}{season_end}"
    bracket_year = season_end
    return season, bracket_year
