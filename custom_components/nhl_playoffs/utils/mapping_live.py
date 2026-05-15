from __future__ import annotations
from typing import Optional, Dict, Any

from .mapping_bracket import SERIES_MAP  # reuse the same static map

# Reverse lookup: "A" → "r1_e1"
LETTER_TO_SERIES_KEY = {
    meta["series_letter"]: key for key, meta in SERIES_MAP.items()
}

def get_series_key_from_letter(letter: str) -> Optional[str]:
    if not letter:
        return None
    return LETTER_TO_SERIES_KEY.get(letter.upper())

def get_series_key_from_live_game(game: Dict[str, Any]) -> Optional[str]:
    """
    Modern API:
        game["seriesStatus"]["seriesLetter"]
    """
    status = game.get("seriesStatus", {})
    letter = status.get("seriesLetter")

    if not letter:
        return None

    return get_series_key_from_letter(letter)
