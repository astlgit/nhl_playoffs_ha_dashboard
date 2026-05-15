from __future__ import annotations

from typing import Any, Dict

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import entity_registry as er

from ..const import DOMAIN, LOGGER, SERIES_COORDINATOR, LIVE_COORDINATOR
from ..utils.mapping_bracket import SERIES_MAP


# ---------------------------------------------------------
# MIGRATION CLEANUP — remove ALL old live sensors
# ---------------------------------------------------------
async def _cleanup_old_live_entities(hass: HomeAssistant):
    registry = er.async_get(hass)

    OLD_ENTITY_PREFIXES = [
        "sensor.live_",
        "sensor.series_",
        "sensor.playoffs_",
        "sensor.nhl_live_",
        "sensor.nhl_series_",
        "sensor.live_final",
        "sensor.series_final",
        "sensor.nhl_live_final",
        "sensor.nhl_series_final",
    ]

    OLD_UNIQUE_PREFIXES = [
        "live_",
        "series_",
        "nhl_live_",
        "nhl_series_",
        f"{DOMAIN}_live_",
        f"{DOMAIN}_series_",
        f"{DOMAIN}_",
    ]

    for entity_id, entity in list(registry.entities.items()):
        if entity.platform != DOMAIN:
            continue

        if any(entity_id.startswith(prefix) for prefix in OLD_ENTITY_PREFIXES):
            registry.async_remove(entity_id)
            continue

        if any(entity.unique_id.startswith(prefix) for prefix in OLD_UNIQUE_PREFIXES):
            registry.async_remove(entity_id)
            continue


# ---------------------------------------------------------
# SETUP ENTRY
# ---------------------------------------------------------
async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    await _cleanup_old_live_entities(hass)

    data = hass.data[DOMAIN][entry.entry_id]
    series_coordinator = data[SERIES_COORDINATOR]
    live_coordinator = data[LIVE_COORDINATOR]

    entities: list[LiveSeriesSensor] = []

    for key, meta in SERIES_MAP.items():
        entities.append(
            LiveSeriesSensor(
                hass=hass,
                entry=entry,
                series_key=key,   # <-- now matches r1_west_1, r3_east_cf, r4_final, etc.
                meta=meta,
            )
        )

    async_add_entities(entities)


# ---------------------------------------------------------
# LIVE SENSOR CLASS
# ---------------------------------------------------------
class LiveSeriesSensor(SensorEntity):
    _attr_should_poll = False

    def __init__(self, hass, entry, series_key: str, meta: dict[str, Any]) -> None:
        self.hass = hass
        self.entry = entry

        self.series_key = series_key
        self.series_letter = meta["series_letter"]

        # FINAL NAMING — nhl_live_{series_key}
        # Example: nhl_live_r1_west_1
        self._attr_unique_id = f"nhl_live_{series_key}"
        self._attr_name = f"NHL Live {series_key.upper()}"

        data = hass.data[DOMAIN][entry.entry_id]
        self.series_coordinator = data[SERIES_COORDINATOR]
        self.live_coordinator = data[LIVE_COORDINATOR]

        self._state = "normal"
        self._attr_extra_state_attributes: Dict[str, Any] = {}

    async def async_added_to_hass(self):
        self.live_coordinator.add_listener(
            lambda: self.hass.async_create_task(self._handle_coordinator_update())
        )

        self.series_coordinator.async_add_listener(
            lambda: self.hass.async_create_task(self._handle_coordinator_update())
        )

        await self._handle_coordinator_update()

    async def _handle_coordinator_update(self):
        try:
            live_state = self.live_coordinator.get_series(self.series_letter)

            base_attrs: Dict[str, Any] = {}
            if live_state:
                base_attrs["game_pk"] = live_state.get("game_pk")

            self._attr_extra_state_attributes = base_attrs

            if not live_state or live_state.get("json") is None:
                await self._update_from_series_fallback()
                self.async_write_ha_state()
                return

            raw_json = live_state["json"]

            if raw_json:
                parsed = raw_json
                self._attr_extra_state_attributes.update(parsed)

                game_state = parsed.get("game_state", "")

                if game_state in ("LIVE", "CRIT", "PRE", "OVER", "FINAL"):
                    self._state = "live"
                elif game_state == "OFF":
                    self._state = "final"
                else:
                    self._state = "normal"

                self.async_write_ha_state()
                return

            await self._update_from_series_fallback()
            self.async_write_ha_state()

        except Exception as err:
            LOGGER.error("LiveSeriesSensor update failed for %s: %s", self.series_key, err)

    async def _update_from_series_fallback(self):
        series_data = self.series_coordinator.data.get(self.series_letter, {}) or {}
        today = series_data.get("today_game")
        next_game = series_data.get("next_game")

        if today:
            self._state = today.get("game_state", "normal")
            self._attr_extra_state_attributes.update(today)
            return

        if next_game:
            self._state = "FUT"
            self._attr_extra_state_attributes.update(next_game)
            return

        self._state = "normal"

    @property
    def native_value(self) -> str:
        return self._state

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attr_extra_state_attributes
