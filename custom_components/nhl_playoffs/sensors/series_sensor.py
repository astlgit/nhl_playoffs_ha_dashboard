from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from ..const import DOMAIN
from ..coordinator.coordinator import NHLPlayoffsCoordinator
from ..utils.mapping import SERIES_MAP


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: NHLPlayoffsCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[NHLPlayoffSeriesSensor] = []

    for key, meta in SERIES_MAP.items():
        entities.append(
            NHLPlayoffSeriesSensor(
                coordinator=coordinator,
                series_key=key,
                meta=meta,
            )
        )

    async_add_entities(entities)


class NHLPlayoffSeriesSensor(CoordinatorEntity, SensorEntity):
    _attr_icon = "mdi:hockey-sticks"

    def __init__(self, coordinator: NHLPlayoffsCoordinator, series_key: str, meta: dict[str, Any]) -> None:
        super().__init__(coordinator)
        self._series_key = series_key
        self._meta = meta
        self._attr_unique_id = f"{DOMAIN}_{series_key}"
        self._attr_entity_id = f"playoffs_{series_key}"
        self._attr_name = meta["name"]

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        letter = self._meta["series_letter"]
        series_data = data.get(letter, {})

        bracket = series_data.get("bracket", {})
        schedule = series_data.get("schedule", {})

        attrs: dict[str, Any] = {}

        # ---------------------------------------------------------
        # TEAM + SERIES DATA (with safe fallbacks)
        # ---------------------------------------------------------
        team1 = bracket.get("topSeedTeam") or {}
        team2 = bracket.get("bottomSeedTeam") or {}

        t1_abbrev = team1.get("abbrev") or "TBD"
        t2_abbrev = team2.get("abbrev") or "TBD"

        t1_name = (team1.get("name") or {}).get("default") or "TBD"
        t2_name = (team2.get("name") or {}).get("default") or "TBD"

        t1_seed = bracket.get("topSeedRankAbbrev") or "—"
        t2_seed = bracket.get("bottomSeedRankAbbrev") or "—"

        t1_wins = bracket.get("topSeedWins") or 0
        t2_wins = bracket.get("bottomSeedWins") or 0

        t1_logo = team1.get("logo") or "/local/nhl/tbd.png"
        t2_logo = team2.get("logo") or "/local/nhl/tbd.png"

        attrs["team1_abbrev"] = t1_abbrev
        attrs["team2_abbrev"] = t2_abbrev
        attrs["team1_name"] = t1_name
        attrs["team2_name"] = t2_name
        attrs["team1_seed"] = t1_seed
        attrs["team2_seed"] = t2_seed
        attrs["team1_wins"] = t1_wins
        attrs["team2_wins"] = t2_wins
        attrs["team1_logo"] = t1_logo
        attrs["team2_logo"] = t2_logo

        attrs["series_letter"] = letter
        attrs["round"] = self._meta["round"]
        attrs["conference"] = self._meta["conference"]

        # ---------------------------------------------------------
        # SERIES STATUS (TBD-safe, final logic)
        # ---------------------------------------------------------
        a1 = t1_abbrev
        a2 = t2_abbrev
        w1 = t1_wins
        w2 = t2_wins

        # Both teams unknown
        if a1 == "TBD" and a2 == "TBD":
            attrs["series_status"] = "TBD"

        # One team unknown
        elif a1 == "TBD" or a2 == "TBD":
            attrs["series_status"] = "TBD"

        # Before series starts
        elif w1 == 0 and w2 == 0:
            attrs["series_status"] = "TBD"

        # Series active
        elif w1 < 4 and w2 < 4:
            if w1 > w2:
                attrs["series_status"] = f"{a1} lead {w1}-{w2}"
            elif w2 > w1:
                attrs["series_status"] = f"{a2} lead {w2}-{w1}"
            else:
                attrs["series_status"] = f"Tied {w1}-{w2}"

        # Series finished
        else:
            if w1 > w2:
                attrs["series_status"] = f"{a1} wins {w1}-{w2}"
            else:
                attrs["series_status"] = f"{a2} wins {w2}-{w1}"

        # ---------------------------------------------------------
        # SCHEDULE PARSING
        # ---------------------------------------------------------
        games = (
            schedule.get("games")
            or schedule.get("gameSchedule")
            or []
        )

        games_list: list[dict[str, Any]] = []
        games_dict: dict[str, Any] = {}

        for g in games:
            game_id = g.get("id") or g.get("gameId")
            if not game_id:
                continue

            item = {
                "game_id": game_id,
                "game_state": g.get("gameState") or g.get("gameStateCode"),
                "start_time": g.get("startTimeUTC") or g.get("startTime"),
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
        # NEXT GAME / LAST GAME
        # ---------------------------------------------------------
        next_game = None
        last_game = None

        for g in games_list:
            state = (g.get("game_state") or "").upper()

            if state in ("FUT", "PRE") and next_game is None:
                next_game = g

            if state in ("OFF", "FINAL", "END", "COMPLETED"):
                last_game = g

        attrs["next_game"] = next_game
        attrs["last_game"] = last_game

        return attrs

    @property
    def native_value(self) -> str | None:
        return self.extra_state_attributes.get("series_status")
