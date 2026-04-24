from __future__ import annotations

import logging

DOMAIN = "nhl_playoffs"
LOGGER = logging.getLogger(f"custom_components.{DOMAIN}")

CONF_SEASON_MODE = "season_mode"
CONF_MANUAL_SEASON = "manual_season"

SEASON_MODE_CURRENT = "current"
SEASON_MODE_MANUAL = "manual"
DEFAULT_SEASON_MODE = SEASON_MODE_CURRENT
DEFAULT_MANUAL_SEASON = "20232024"  # Good full-data test season
