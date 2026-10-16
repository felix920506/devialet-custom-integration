"""Media player for Devialet Custom: volume, mute and input source."""

from __future__ import annotations

from homeassistant.components.media_player import (
    MediaPlayerDeviceClass,
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import SOURCES
from .coordinator import DevialetConfigEntry, DevialetCoordinator
from .entity import DevialetEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DevialetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the media player."""
    async_add_entities([DevialetMediaPlayer(entry.runtime_data)])


class DevialetMediaPlayer(DevialetEntity, MediaPlayerEntity):
    """The speaker as a media player."""

    _attr_name = None
    _attr_device_class = MediaPlayerDeviceClass.SPEAKER
    _attr_source_list = SOURCES
    _attr_supported_features = (
        MediaPlayerEntityFeature.VOLUME_SET
        | MediaPlayerEntityFeature.VOLUME_STEP
        | MediaPlayerEntityFeature.VOLUME_MUTE
        | MediaPlayerEntityFeature.SELECT_SOURCE
    )

    def __init__(self, coordinator: DevialetCoordinator) -> None:
        super().__init__(coordinator, "media_player")

    @property
    def state(self) -> MediaPlayerState:
        if self.coordinator.data.get("powerstate") == "Running":
            return MediaPlayerState.ON
        return MediaPlayerState.STANDBY

    @property
    def volume_level(self) -> float | None:
        volume = self.coordinator.data.get("volume")
        return None if volume is None else volume / 100

    @property
    def is_volume_muted(self) -> bool | None:
        mute = self.coordinator.data.get("mutemode")
        return None if mute is None else bool(mute)

    @property
    def source(self) -> str | None:
        return self.coordinator.data.get("source")

    async def async_set_volume_level(self, volume: float) -> None:
        await self.coordinator.async_set("volume", round(volume * 100))

    async def async_mute_volume(self, mute: bool) -> None:
        await self.coordinator.async_set("mutemode", int(mute))

    async def async_select_source(self, source: str) -> None:
        await self.coordinator.async_set("source", source)
