from __future__ import annotations

import logging
from datetime import timedelta

# ---------------------------------------------------------------------------
# Domain + Logging
# ---------------------------------------------------------------------------
DOMAIN = "nhl_playoffs"
LOGGER = logging.getLogger(f"custom_components.{DOMAIN}")

# ---------------------------------------------------------------------------
# Config Options
# ---------------------------------------------------------------------------
CONF_SEASON_MODE = "season_mode"
CONF_MANUAL_SEASON = "manual_season"
CONF_DEBUG = "debug"

SEASON_MODE_CURRENT = "current"
SEASON_MODE_MANUAL = "manual"

DEFAULT_SEASON_MODE = SEASON_MODE_CURRENT
DEFAULT_MANUAL_SEASON = "20232024"  # Good full-data test season

# ---------------------------------------------------------------------------
# SeriesCoordinator update interval (slow data)
# ---------------------------------------------------------------------------
UPDATE_INTERVAL = timedelta(minutes=5)

# ---------------------------------------------------------------------------
# Coordinator Keys
# ---------------------------------------------------------------------------
SERIES_COORDINATOR = "series"
LIVE_COORDINATOR = "live"

# ---------------------------------------------------------------------------
# Series Letters (A–O)
# ---------------------------------------------------------------------------
SERIES_LETTERS = [
    "A", "B", "C", "D",
    "E", "F", "G", "H",
    "I", "J", "K", "L",
    "M", "N", "O",
]

# ---------------------------------------------------------------------------
# NHL API Endpoints
# ---------------------------------------------------------------------------
API_BRACKET = "https://api-web.nhle.com/v1/playoff-bracket/{year}"
API_CAROUSEL = "https://api-web.nhle.com/v1/playoff-series/carousel/{season}"
API_SCHEDULE = "https://api-web.nhle.com/v1/playoff-series/{season}/{series_letter}"

# League-wide authoritative schedule for today's games
API_SCHEDULE_NOW = "https://api-web.nhle.com/v1/schedule/now"

# Modern live play-by-play endpoint
API_LIVE_GAME = "https://api-web.nhle.com/v1/gamecenter/{gamePk}/play-by-play"
