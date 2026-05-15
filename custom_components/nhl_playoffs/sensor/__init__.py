from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from ..const import DOMAIN, SERIES_COORDINATOR, LIVE_COORDINATOR
from ..utils.mapping_bracket import SERIES_MAP
from .series_sensor import SeriesSensor
from .live_series_sensor import LiveSeriesSensor


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    data = hass.data[DOMAIN][entry.entry_id]
    series_coordinator = data[SERIES_COORDINATOR]
    live_coordinator = data[LIVE_COORDINATOR]

    entities = []

    # Create sensors for each series
    for series_key, meta in SERIES_MAP.items():
        # Static series info (today/next game)
        entities.append(SeriesSensor(series_coordinator, series_key, meta))

        # Live game sensor (event-driven)
        entities.append(LiveSeriesSensor(hass, entry, series_key, meta))

    async_add_entities(entities)
