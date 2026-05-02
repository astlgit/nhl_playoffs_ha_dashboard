from __future__ import annotations
from typing import Any, Dict


def _compute_period_ordinal(period: int | None) -> str:
    """Convert period number into ordinal (1st, 2nd, OT, 2OT, etc.)."""
    if period is None or period == 0:
        return ""

    if period == 1:
        return "1st"
    if period == 2:
        return "2nd"
    if period == 3:
        return "3rd"

    # Overtime logic
    ot_number = period - 3
    if ot_number == 1:
        return "OT"
    return f"{ot_number}OT"


def parse_live_game(live: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse the normalized live game object returned by live_api.fetch_live_game().
    Attribute names remain identical to the old system for dashboard compatibility.
    """

    if not live:
        return {
            "game_pk": None,
            "game_state": "",
            "home_team": "",
            "away_team": "",
            "home_score": 0,
            "away_score": 0,
            "current_period": 0,
            "current_period_ordinal": "",
            "period_time_remaining": "",
            "is_intermission": False,
            "home_logo": None,
            "away_logo": None,
            "home_shots": None,
            "away_shots": None,
            "winner": None,
            "series_code": None,
            "series_status": None,
        }

    # Basic fields
    game_state = live.get("game_state", "")

    # Treat CRIT as LIVE
    if game_state == "CRIT":
        game_state = "LIVE"

    current_period = live.get("current_period")
    current_period_ordinal = (
        live.get("current_period_ordinal")
        or _compute_period_ordinal(current_period)
    )

    time_remaining = live.get("time_remaining")
    is_intermission = live.get("is_intermission", False)

    # Teams
    home_team = live.get("home_team", "")
    away_team = live.get("away_team", "")

    # Scores
    home_score = live.get("home_score", 0)
    away_score = live.get("away_score", 0)

    # Logos
    home_logo = live.get("home_logo")
    away_logo = live.get("away_logo")

    # Shots
    home_shots = live.get("home_shots")
    away_shots = live.get("away_shots")

    # Winner (only when final)
    winner = None
    if game_state in ("FINAL", "OFF"):
        if home_score > away_score:
            winner = home_team
        elif away_score > home_score:
            winner = away_team

    # Series metadata (optional)
    series_code = live.get("series_code")
    series_status = live.get("series_status")

    return {
        "game_pk": live.get("game_pk"),
        "game_state": game_state,

        "home_team": home_team,
        "away_team": away_team,

        "home_score": home_score,
        "away_score": away_score,

        "current_period": current_period,
        "current_period_ordinal": current_period_ordinal,

        "period_time_remaining": time_remaining or "",
        "is_intermission": is_intermission,

        "home_logo": home_logo,
        "away_logo": away_logo,

        "home_shots": home_shots,
        "away_shots": away_shots,

        "series_code": series_code,
        "series_status": series_status,

        "winner": winner,
    }
