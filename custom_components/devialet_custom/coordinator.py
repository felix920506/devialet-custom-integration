"""Data update coordinator for Devialet Custom."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import DevialetCustomApi, DevialetError
from .const import CONF_SIMPLE_MODE, DEFAULT_ON_VOLUME, DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

STORAGE_VERSION = 1

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
        self.simple_mode: bool = entry.options.get(CONF_SIMPLE_MODE, False)
        self.store = volume_store(hass, entry.entry_id)
        # Volume to restore when leaving the fake standby (volume 0).
        self.saved_volume: int | None = None

    async def async_load_saved_volume(self) -> None:
        """Load the volume saved by the last standby."""
        if stored := await self.store.async_load():
            self.saved_volume = stored.get("volume")

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

    async def async_standby(self) -> None:
        """Fake standby: remember the current volume, then set it to 0%."""
        volume = self.data.get("volume") or 0
        if volume > 0:
            self.saved_volume = volume
            await self.store.async_save({"volume": volume})
        await self.async_set("volume", 0)

    async def async_wake(self) -> None:
        """Leave fake standby by restoring the saved volume."""
        if self.data.get("volume"):
            return
        volume = (
            self.saved_volume or self.data.get("startupvolume") or DEFAULT_ON_VOLUME
        )
        await self.async_set("volume", volume)


def volume_store(hass: HomeAssistant, entry_id: str) -> Store[dict[str, Any]]:
    """Return the store holding a speaker's saved volume."""
    return Store(hass, STORAGE_VERSION, f"{DOMAIN}.{entry_id}")
