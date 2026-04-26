from __future__ import annotations

import logging
from datetime import timedelta

DOMAIN = "nhl_playoffs"
LOGGER = logging.getLogger(f"custom_components.{DOMAIN}")

CONF_SEASON_MODE = "season_mode"
CONF_MANUAL_SEASON = "manual_season"
CONF_DEBUG = "debug"

SEASON_MODE_CURRENT = "current"
SEASON_MODE_MANUAL = "manual"
DEFAULT_SEASON_MODE = SEASON_MODE_CURRENT
DEFAULT_MANUAL_SEASON = "20232024"  # Good full-data test season

UPDATE_INTERVAL = timedelta(hours=1)

# NHL API endpoints
API_BRACKET = "https://api-web.nhle.com/v1/playoff-bracket/{year}"
API_CAROUSEL = "https://api-web.nhle.com/v1/playoff-series/carousel/{season}"
API_SCHEDULE = "https://api-web.nhle.com/v1/playoff-series/{season}/{series_letter}"
