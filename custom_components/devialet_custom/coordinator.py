"""Data update coordinator for Devialet Custom."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DevialetCustomApi, DevialetError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

type DevialetConfigEntry = ConfigEntry[DevialetCoordinator]


class DevialetCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Poll /cisettings/getall and push setting changes."""

    config_entry: DevialetConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: DevialetConfigEntry,
        api: DevialetCustomApi,
        device_info: dict[str, Any],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.api = api
        self.device_info = device_info

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.api.get_settings()
        except DevialetError as err:
            raise UpdateFailed(str(err)) from err

    async def async_set(self, key: str, value: Any) -> None:
        """Write a setting, apply it locally, then refresh from the speaker."""
        try:
            await self.api.set_setting(key, value)
        except DevialetError as err:
            raise HomeAssistantError(f"Failed to set {key}: {err}") from err
        self.async_set_updated_data({**self.data, key: value})
        await self.async_request_refresh()
