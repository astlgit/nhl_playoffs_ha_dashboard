from __future__ import annotations

from typing import Optional, Dict, Any

# Your existing static mapping (unchanged)
SERIES_MAP = {
    "r1_east_1": {
        "name": "Playoffs R1 East 1",
        "series_letter": "A",
        "round": 1,
        "conference": "East",
    },
    "r1_east_2": {
        "name": "Playoffs R1 East 2",
        "series_letter": "B",
        "round": 1,
        "conference": "East",
    },
    "r1_east_3": {
        "name": "Playoffs R1 East 3",
        "series_letter": "C",
        "round": 1,
        "conference": "East",
    },
    "r1_east_4": {
        "name": "Playoffs R1 East 4",
        "series_letter": "D",
        "round": 1,
        "conference": "East",
    },
    "r1_west_1": {
        "name": "Playoffs R1 West 1",
        "series_letter": "E",
        "round": 1,
        "conference": "West",
    },
    "r1_west_2": {
        "name": "Playoffs R1 West 2",
        "series_letter": "F",
        "round": 1,
        "conference": "West",
    },
    "r1_west_3": {
        "name": "Playoffs R1 West 3",
        "series_letter": "G",
        "round": 1,
        "conference": "West",
    },
    "r1_west_4": {
        "name": "Playoffs R1 West 4",
        "series_letter": "H",
        "round": 1,
        "conference": "West",
    },
    "r2_east_1": {
        "name": "Playoffs R2 East 1",
        "series_letter": "I",
        "round": 2,
        "conference": "East",
    },
    "r2_east_2": {
        "name": "Playoffs R2 East 2",
        "series_letter": "J",
        "round": 2,
        "conference": "East",
    },
    "r2_west_1": {
        "name": "Playoffs R2 West 1",
        "series_letter": "K",
        "round": 2,
        "conference": "West",
    },
    "r2_west_2": {
        "name": "Playoffs R2 West 2",
        "series_letter": "L",
        "round": 2,
        "conference": "West",
    },
    "east_final": {
        "name": "Playoffs East Final",
        "series_letter": "M",
        "round": 3,
        "conference": "East",
    },
    "west_final": {
        "name": "Playoffs West Final",
        "series_letter": "N",
        "round": 3,
        "conference": "West",
    },
    "final": {
        "name": "Stanley Cup Final",
        "series_letter": "O",
        "round": 4,
        "conference": "League",
    },
}


# ---------------------------------------------------------
# NEW: Reverse lookup helpers for LIVE GAME mapping
# ---------------------------------------------------------

# Build reverse lookup: "A" → "r1_east_1"
LETTER_TO_SERIES_KEY = {
    meta["series_letter"]: key for key, meta in SERIES_MAP.items()
}


def get_series_key_from_letter(letter: str) -> Optional[str]:
    """Return our internal series key (e.g., r1_east_1) from a series letter (A–O)."""
    if not letter:
        return None
    return LETTER_TO_SERIES_KEY.get(letter.upper())


def get_series_key_from_live_game(game: Dict[str, Any]) -> Optional[str]:
    """
    Extract the series letter from a live game object and map it to our internal key.
    StatsAPI path:
        game["seriesSummary"]["seriesCode"]  → "A", "B", ..., "O"
    """
    summary = game.get("seriesSummary", {})
    letter = summary.get("seriesCode")

    if not letter:
        return None

    return get_series_key_from_letter(letter)
