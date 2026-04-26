from __future__ import annotations

import datetime
from typing import Any

from ..const import (
    CONF_MANUAL_SEASON,
    CONF_SEASON_MODE,
    DEFAULT_MANUAL_SEASON,
    DEFAULT_SEASON_MODE,
    SEASON_MODE_CURRENT,
    SEASON_MODE_MANUAL,
)


class Season:
    """Season selection and display helpers."""

    def __init__(self, data: dict[str, Any]) -> None:
        self.season_mode = data.get(CONF_SEASON_MODE, DEFAULT_SEASON_MODE)
        self.manual_season = data.get(CONF_MANUAL_SEASON, DEFAULT_MANUAL_SEASON)

    @property
    def display_season(self) -> str:
        if self.season_mode == SEASON_MODE_MANUAL and self.manual_season:
            return self.manual_season

        now = datetime.datetime.now()
        year = now.year
        if now.month < 9:
            return f"{year-1}{year}"
        return f"{year}{year+1}"
