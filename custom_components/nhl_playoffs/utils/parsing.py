from __future__ import annotations

from typing import Any, Dict, Optional

from ..const import LOGGER


def safe_get(obj: Dict[str, Any], *keys, default=None):
    """Safely walk nested dict keys."""
    for key in keys:
        if not isinstance(obj, dict):
            return default
        obj = obj.get(key)
    return obj if obj is not None else default


def parse_live_game(game: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract all relevant live-game attributes for the unified live sensors.
    Works with NHL StatsAPI schedule endpoint.
    """

    # Basic metadata
    game_pk = game.get("gamePk")
    game_state = safe_get(game, "status", "detailedState", default="")

    # Teams
    home = safe_get(game, "teams", "home", "team", "abbreviation", default="")
    away = safe_get(game, "teams", "away", "team", "abbreviation", default="")

    # Scores
    home_score = safe_get(game, "teams", "home", "score", default=0)
    away_score = safe_get(game, "teams", "away", "score", default=0)

    # Linescore
    linescore = game.get("linescore", {})

    current_period = linescore.get("currentPeriod", 0)
    current_period_ordinal = linescore.get("currentPeriodOrdinal", "")
    period_time_remaining = linescore.get("currentPeriodTimeRemaining", "")

    # Intermission
    intermission = safe_get(linescore, "intermissionInfo", "inIntermission", default=False)
    intermission_time_remaining = safe_get(
        linescore, "intermissionInfo", "intermissionTimeRemaining", default=0
    )

    # Series info (for mapping)
    series_code = safe_get(game, "seriesSummary", "seriesCode", default=None)
    series_status = safe_get(game, "seriesSummary", "seriesStatus", default=None)

    # Final game winner
    winner = None
    if game_state == "Final":
        if home_score > away_score:
            winner = home
        elif away_score > home_score:
            winner = away

    return {
        "game_pk": game_pk,
        "game_state": game_state,
        "home_team": home,
        "away_team": away,
        "home_score": home_score,
        "away_score": away_score,
        "current_period": current_period,
        "current_period_ordinal": current_period_ordinal,
        "period_time_remaining": period_time_remaining,
        "intermission": intermission,
        "intermission_time_remaining": intermission_time_remaining,
        "series_code": series_code,
        "series_status": series_status,
        "winner": winner,
    }
