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
    """Normalize NHL live-game JSON into a stable, HA-friendly structure."""

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
            "is_running": False,
            "is_intermission": False,
            "home_logo": None,
            "away_logo": None,
            "home_shots": None,
            "away_shots": None,
            "winner": None,
            "series_code": None,
            "series_status": None,
            "startTimeUTC": None,

            # Strength defaults
            "strength_home": 5,
            "strength_away": 5,

            # New simplified flags
            "home_pp": False,
            "away_pp": False,
            "home_en": False,
            "away_en": False,
            "is_4_on_4": False,
            "is_5_on_3": False,
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
    is_running = clock.get("running", False)
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
    # START TIME
    # -------------------------------------------------------------------------
    start_time = raw.get("startTimeUTC")

    # -------------------------------------------------------------------------
    # NEW POWER PLAY / EMPTY NET / STRENGTH LOGIC
    # -------------------------------------------------------------------------
    situation = raw.get("situation")

    if situation:
        home_sit = situation.get("homeTeam", {})
        away_sit = situation.get("awayTeam", {})

        # Strengths
        home_strength = home_sit.get("strength", 5)
        away_strength = away_sit.get("strength", 5)

        # Empty net flags
        home_en = "EN" in (home_sit.get("situationDescriptions") or [])
        away_en = "EN" in (away_sit.get("situationDescriptions") or [])

        # Power play flags (from sitDesc, not strength mismatch)
        home_pp = "PP" in (home_sit.get("situationDescriptions") or [])
        away_pp = "PP" in (away_sit.get("situationDescriptions") or [])

        # 4-on-4
        is_4_on_4 = home_strength == 4 and away_strength == 4

        # 5-on-3
        is_5_on_3 = (
            (home_strength == 5 and away_strength == 3) or
            (home_strength == 3 and away_strength == 5)
        )

    else:
        # No situation block → assume even strength
        home_strength = 5
        away_strength = 5
        home_en = False
        away_en = False
        home_pp = False
        away_pp = False
        is_4_on_4 = False
        is_5_on_3 = False

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
        "is_running": is_running,
        "is_intermission": is_intermission,
        "home_logo": home_logo,
        "away_logo": away_logo,
        "home_shots": home_shots,
        "away_shots": away_shots,
        "winner": winner,
        "series_code": raw.get("series_code"),
        "series_status": raw.get("series_status"),
        "startTimeUTC": start_time,

        # Strength + PP + EN flags
        "strength_home": home_strength,
        "strength_away": away_strength,
        "home_pp": home_pp,
        "away_pp": away_pp,
        "home_en": home_en,
        "away_en": away_en,
        "is_4_on_4": is_4_on_4,
        "is_5_on_3": is_5_on_3,
    }
