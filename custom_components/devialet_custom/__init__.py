"""The Devialet Custom integration."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DevialetCustomApi, DevialetError
from .coordinator import DevialetConfigEntry, DevialetCoordinator

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.NUMBER, Platform.SELECT, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> bool:
    """Set up a Devialet Custom speaker from a config entry."""
    api = DevialetCustomApi(async_get_clientsession(hass), entry.data[CONF_HOST])
    try:
        device_info = await api.get_device_info()
    except DevialetError as err:
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = DevialetCoordinator(hass, entry, api, device_info)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
