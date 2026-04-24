from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_SEASON_MODE,
    CONF_MANUAL_SEASON,
    SEASON_MODE_CURRENT,
    SEASON_MODE_MANUAL,
    DEFAULT_SEASON_MODE,
    DEFAULT_MANUAL_SEASON,
)


def _season_schema(defaults: dict[str, Any]) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(
                CONF_SEASON_MODE,
                default=defaults.get(CONF_SEASON_MODE, DEFAULT_SEASON_MODE),
            ): vol.In(
                {
                    SEASON_MODE_CURRENT: "Current season (auto-detect)",
                    SEASON_MODE_MANUAL: "Manual season (override)",
                }
            ),
            vol.Optional(
                CONF_MANUAL_SEASON,
                default=defaults.get(CONF_MANUAL_SEASON, DEFAULT_MANUAL_SEASON),
            ): str,
        }
    )


class NHLPlayoffsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NHL Playoffs."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            # Basic validation: if manual mode, require a season string
            if (
                user_input[CONF_SEASON_MODE] == SEASON_MODE_MANUAL
                and not user_input.get(CONF_MANUAL_SEASON)
            ):
                return self.async_show_form(
                    step_id="user",
                    data_schema=_season_schema(user_input),
                    errors={"base": "manual_season_required"},
                )

            return self.async_create_entry(
                title="NHL Playoffs",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=_season_schema({}),
        )


class NHLPlayoffsOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for NHL Playoffs."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        defaults: dict[str, Any] = {
            **self.config_entry.data,
            **self.config_entry.options,
        }

        return self.async_show_form(
            step_id="init",
            data_schema=_season_schema(defaults),
        )


async def async_get_options_flow(
    config_entry: config_entries.ConfigEntry,
) -> NHLPlayoffsOptionsFlowHandler:
    return NHLPlayoffsOptionsFlowHandler(config_entry)
