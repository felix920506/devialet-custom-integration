"""Select entities for Devialet Custom configuration options."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import SIMPLE_MODE_KEYS, SOURCES
from .coordinator import DevialetConfigEntry, DevialetCoordinator
from .entity import DevialetEntity


@dataclass(frozen=True, kw_only=True)
class DevialetSelectDescription(SelectEntityDescription):
    """Maps HA option names to the values the speaker uses."""

    values: dict[str, str | int]


SELECTS = (
    DevialetSelectDescription(
        key="ledmode",
        translation_key="led_mode",
        entity_category=EntityCategory.CONFIG,
        values={"off": 0, "on": 1, "slow_blink": 2, "fast_blink": 3},
    ),
    DevialetSelectDescription(
        key="mix",
        translation_key="channel_mix",
        entity_category=EntityCategory.CONFIG,
        values={"left": "L", "right": "R", "mono": "M"},
    ),
    DevialetSelectDescription(
        key="startupsource",
        translation_key="startup_source",
        entity_category=EntityCategory.CONFIG,
        values={source: source for source in SOURCES},
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DevialetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up select entities."""
    coordinator = entry.runtime_data
    async_add_entities(
        DevialetSelect(coordinator, description)
        for description in SELECTS
        if not coordinator.simple_mode or description.key in SIMPLE_MODE_KEYS
    )


class DevialetSelect(DevialetEntity, SelectEntity):
    """A Devialet setting with a fixed set of values."""

    entity_description: DevialetSelectDescription

    def __init__(
        self, coordinator: DevialetCoordinator, description: DevialetSelectDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        self._attr_options = list(description.values)

    @property
    def current_option(self) -> str | None:
        value = self.coordinator.data.get(self.entity_description.key)
        for option, option_value in self.entity_description.values.items():
            if option_value == value:
                return option
        return None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set(
            self.entity_description.key, self.entity_description.values[option]
        )
