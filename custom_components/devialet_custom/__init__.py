"""The Devialet Custom integration."""

from __future__ import annotations

from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import DevialetCustomApi, DevialetError
from .const import SIMPLE_MODE_KEYS
from .coordinator import DevialetConfigEntry, DevialetCoordinator, volume_store

PLATFORMS = [Platform.MEDIA_PLAYER, Platform.NUMBER, Platform.SELECT, Platform.SENSOR]
SIMPLE_MODE_PLATFORMS = [Platform.MEDIA_PLAYER, Platform.SELECT]


async def async_setup_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> bool:
    """Set up a Devialet Custom speaker from a config entry."""
    api = DevialetCustomApi(async_get_clientsession(hass), entry.data[CONF_HOST])
    try:
        device_info = await api.get_device_info()
    except DevialetError as err:
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = DevialetCoordinator(hass, entry, api, device_info)
    await coordinator.async_load_saved_volume()
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    if coordinator.simple_mode:
        _remove_full_mode_entities(hass, entry, device_info["serial"])

    await hass.config_entries.async_forward_entry_setups(entry, _platforms(entry))
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _platforms(entry))


async def async_remove_entry(hass: HomeAssistant, entry: DevialetConfigEntry) -> None:
    """Delete the saved volume when the speaker is removed."""
    await volume_store(hass, entry.entry_id).async_remove()


def _platforms(entry: DevialetConfigEntry) -> list[Platform]:
    # Use the mode the entry was set up with, not the (possibly changed) options.
    return SIMPLE_MODE_PLATFORMS if entry.runtime_data.simple_mode else PLATFORMS


def _remove_full_mode_entities(
    hass: HomeAssistant, entry: DevialetConfigEntry, serial: str
) -> None:
    """Drop entities that simple mode doesn't provide so they don't linger."""
    keep = {f"{serial}_{key}" for key in SIMPLE_MODE_KEYS}
    registry = er.async_get(hass)
    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if entity.unique_id not in keep:
            registry.async_remove(entity.entity_id)


async def _async_options_updated(
    hass: HomeAssistant, entry: DevialetConfigEntry
) -> None:
    await hass.config_entries.async_reload(entry.entry_id)
