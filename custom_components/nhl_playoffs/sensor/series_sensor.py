from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN, SERIES_COORDINATOR
from ..series_coordinator import SeriesCoordinator
from ..utils.mapping_bracket import SERIES_MAP


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    series_coordinator: SeriesCoordinator = hass.data[DOMAIN][entry.entry_id][SERIES_COORDINATOR]

    entities: list[SeriesSensor] = []

    for key, meta in SERIES_MAP.items():
        entities.append(
            SeriesSensor(
                coordinator=series_coordinator,
                series_key=key,
                meta=meta,
            )
        )

    async_add_entities(entities)


class SeriesSensor(CoordinatorEntity, SensorEntity):
    """Playoff series sensor using the new SeriesCoordinator."""

    _attr_icon = "mdi:hockey-sticks"

    def __init__(self, coordinator: SeriesCoordinator, series_key: str, meta: dict[str, Any]) -> None:
        super().__init__(coordinator)

        self._series_key = series_key
        self._meta = meta

        # REQUIRED: match your working naming pattern
        self._attr_unique_id = f"{DOMAIN}_series_{series_key}"
        self.entity_id = f"sensor.series_{series_key}"
        self._attr_name = meta["name"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        letter = self._meta["series_letter"]
        series_data = data.get(letter, {})

        bracket = series_data.get("bracket", {})
        details = series_data.get("series_details", {})
        next_game = series_data.get("next_game")
        today_game_pk = series_data.get("today_game_pk")

        attrs: dict[str, Any] = {}

        # ---------------------------------------------------------
        # TEAM + SERIES DATA
        # ---------------------------------------------------------
        team1 = bracket.get("topSeedTeam") or {}
        team2 = bracket.get("bottomSeedTeam") or {}

        attrs["team1_abbrev"] = team1.get("abbrev") or "TBD"
        attrs["team2_abbrev"] = team2.get("abbrev") or "TBD"

        attrs["team1_name"] = (team1.get("name") or {}).get("default") or "TBD"
        attrs["team2_name"] = (team2.get("name") or {}).get("default") or "TBD"

        attrs["team1_seed"] = bracket.get("topSeedRankAbbrev") or "—"
        attrs["team2_seed"] = bracket.get("bottomSeedRankAbbrev") or "—"

        attrs["team1_wins"] = bracket.get("topSeedWins") or 0
        attrs["team2_wins"] = bracket.get("bottomSeedWins") or 0

        attrs["team1_logo"] = team1.get("logo") or "/local/nhl/tbd.png"
        attrs["team2_logo"] = team2.get("logo") or "/local/nhl/tbd.png"

        attrs["series_letter"] = letter
        attrs["round"] = self._meta["round"]
        attrs["conference"] = self._meta["conference"]

        # ---------------------------------------------------------
        # SERIES STATUS
        # ---------------------------------------------------------
        a1 = attrs["team1_abbrev"]
        a2 = attrs["team2_abbrev"]
        w1 = attrs["team1_wins"]
        w2 = attrs["team2_wins"]

        if a1 == "TBD" or a2 == "TBD" or (w1 == 0 and w2 == 0):
            attrs["series_status"] = "TBD"
        elif w1 < 4 and w2 < 4:
            if w1 > w2:
                attrs["series_status"] = f"{a1} lead {w1}-{w2}"
            elif w2 > w1:
                attrs["series_status"] = f"{a2} lead {w2}-{w1}"
            else:
                attrs["series_status"] = f"Tied {w1}-{w2}"
        else:
            if w1 > w2:
                attrs["series_status"] = f"{a1} wins {w1}-{w2}"
            else:
                attrs["series_status"] = f"{a2} wins {w2}-{w1}"

        # ---------------------------------------------------------
        # GAMES LIST (from series_details)
        # ---------------------------------------------------------
        games = details.get("games", []) or []

        games_list: list[dict[str, Any]] = []
        games_dict: dict[str, Any] = {}

        for g in games:
            game_id = g.get("id")
            if not game_id:
                continue

            item = {
                "game_id": game_id,
                "game_state": g.get("gameState"),
                "start_time": g.get("startTimeUTC"),
                "home": (g.get("homeTeam") or {}).get("abbrev"),
                "away": (g.get("awayTeam") or {}).get("abbrev"),
                "home_score": (g.get("homeTeam") or {}).get("score"),
                "away_score": (g.get("awayTeam") or {}).get("score"),
                "broadcast": g.get("broadcast"),
            }

            games_list.append(item)
            games_dict[str(game_id)] = item

        attrs["games_list"] = games_list
        attrs["games_dict"] = games_dict

        # ---------------------------------------------------------
        # NEXT GAME
        # ---------------------------------------------------------
        if next_game:
            attrs["next_game_pk"] = next_game.get("game_pk")
            attrs["next_game_time"] = next_game.get("start_time")
            attrs["next_game_home"] = next_game.get("home")
            attrs["next_game_away"] = next_game.get("away")
            attrs["next_game_number"] = next_game.get("game_number")
        else:
            attrs["next_game_pk"] = None
            attrs["next_game_time"] = None
            attrs["next_game_home"] = None
            attrs["next_game_away"] = None
            attrs["next_game_number"] = None

        # ---------------------------------------------------------
        # TODAY GAME PK (critical for LiveCoordinator)
        # ---------------------------------------------------------
        attrs["today_game_pk"] = today_game_pk

        return attrs

    @property
    def native_value(self) -> str | None:
        return self.extra_state_attributes.get("series_status")
