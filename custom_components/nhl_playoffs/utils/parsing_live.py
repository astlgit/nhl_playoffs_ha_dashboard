from __future__ import annotations
from typing import Any, Dict
from ..const import LOGGER

def _compute_period_ordinal(period: int | None) -> str:
    if not period:
        return ""
    if period == 1:
        return "1st"
    if period == 2:
        return "2nd"
    if period == 3:
        return "3rd"
    ot = period - 3
    return "OT" if ot == 1 else f"{ot}OT"


def parse_live_game(raw: Dict[str, Any]) -> Dict[str, Any]:
    if not raw:
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
            "startTimeUTC": None,
        }

    # -------------------------------------------------------------------------
    # GAME STATE
    # -------------------------------------------------------------------------
    game_state = (raw.get("gameState") or "").upper()
    if game_state == "CRIT":
        game_state = "LIVE"

    # -------------------------------------------------------------------------
    # TEAMS
    # -------------------------------------------------------------------------
    home = raw.get("homeTeam", {})
    away = raw.get("awayTeam", {})

    home_team = home.get("abbrev") or ""
    away_team = away.get("abbrev") or ""

    home_score = home.get("score", 0)
    away_score = away.get("score", 0)

    home_logo = home.get("logo")
    away_logo = away.get("logo")

    home_shots = home.get("sog")
    away_shots = away.get("sog")

    # -------------------------------------------------------------------------
    # CLOCK + PERIOD
    # -------------------------------------------------------------------------
    clock = raw.get("clock", {})
    time_remaining = clock.get("timeRemaining", "")
    is_intermission = clock.get("inIntermission", False)

    period = raw.get("displayPeriod") or raw.get("periodDescriptor", {}).get("number")
    period_ordinal = _compute_period_ordinal(period)

    # -------------------------------------------------------------------------
    # WINNER (FINAL or OFF)
    # -------------------------------------------------------------------------
    winner = None
    if game_state in ("FINAL", "OFF"):
        if home_score > away_score:
            winner = home_team
        elif away_score > home_score:
            winner = away_team

    # -------------------------------------------------------------------------
    # START TIME (modern NHL API)
    # -------------------------------------------------------------------------
    start_time = raw.get("startTimeUTC")

    # -------------------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------------------
    return {
        "game_pk": raw.get("id"),
        "game_state": game_state,
        "home_team": home_team,
        "away_team": away_team,
        "home_score": home_score,
        "away_score": away_score,
        "current_period": period,
        "current_period_ordinal": period_ordinal,
        "period_time_remaining": time_remaining,
        "is_intermission": is_intermission,
        "home_logo": home_logo,
        "away_logo": away_logo,
        "home_shots": home_shots,
        "away_shots": away_shots,
        "winner": winner,
        "series_code": raw.get("series_code"),
        "series_status": raw.get("series_status"),
        "startTimeUTC": start_time,  # <-- CORRECT FIELD
    }


