"""Number entities for Devialet Custom configuration options."""

from __future__ import annotations

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfElectricPotential
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DevialetConfigEntry, DevialetCoordinator
from .entity import DevialetEntity

# Ranges match the validation rules in the speaker's own configuration page.
NUMBERS = (
    NumberEntityDescription(
        key="startupvolume",
        translation_key="startup_volume",
        entity_category=EntityCategory.CONFIG,
        native_min_value=0,
        native_max_value=100,
        native_step=1,
        native_unit_of_measurement=PERCENTAGE,
    ),
    NumberEntityDescription(
        key="splmax",
        translation_key="max_spl",
        entity_category=EntityCategory.CONFIG,
        native_min_value=50,
        native_max_value=96,
        native_step=1,
        native_unit_of_measurement="dB",
        mode=NumberMode.BOX,
    ),
    NumberEntityDescription(
        key="analogsensitivity",
        translation_key="analog_sensitivity",
        entity_category=EntityCategory.CONFIG,
        native_min_value=1,
        native_max_value=10,
        native_step=0.5,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        mode=NumberMode.BOX,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DevialetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up number entities."""
    async_add_entities(
        DevialetNumber(entry.runtime_data, description) for description in NUMBERS
    )


class DevialetNumber(DevialetEntity, NumberEntity):
    """A numeric Devialet setting."""

    def __init__(
        self, coordinator: DevialetCoordinator, description: NumberEntityDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self.entity_description.key)

    async def async_set_native_value(self, value: float) -> None:
        # Integer settings must be sent as JSON integers, not floats.
        if self.entity_description.native_step == 1:
            value = int(value)
        await self.coordinator.async_set(self.entity_description.key, value)
