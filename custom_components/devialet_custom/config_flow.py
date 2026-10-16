"""Config flow for Devialet Custom."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DevialetCustomApi, DevialetError
from .const import CONF_SIMPLE_MODE, DOMAIN

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_SIMPLE_MODE, default=False): bool,
    }
)
OPTIONS_SCHEMA = vol.Schema({vol.Optional(CONF_SIMPLE_MODE, default=False): bool})


class DevialetCustomConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Devialet Custom."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return DevialetCustomOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for the speaker's host and verify it responds."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            api = DevialetCustomApi(async_get_clientsession(self.hass), host)
            try:
                info = await api.get_device_info()
                settings = await api.get_settings()
            except DevialetError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(info["serial"])
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                title = settings.get("friendlyname") or info.get("model", "Devialet")
                return self.async_create_entry(
                    title=title,
                    data={CONF_HOST: host},
                    options={CONF_SIMPLE_MODE: user_input[CONF_SIMPLE_MODE]},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                STEP_USER_SCHEMA, user_input
            ),
            errors=errors,
        )


class DevialetCustomOptionsFlow(OptionsFlow):
    """Switch between full and simple mode."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Show the options form."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, self.config_entry.options
            ),
        )
