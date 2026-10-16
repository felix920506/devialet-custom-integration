"""Diagnostic sensors for Devialet Custom."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import re
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import DevialetConfigEntry, DevialetCoordinator
from .entity import DevialetEntity


def _temperature(component: str) -> Callable[[dict[str, Any]], float | None]:
    """Extract one value from e.g. 'ASIC temperature : 30.59 °C, DAMP ...'."""
    pattern = re.compile(rf"{component} temperature\s*:\s*(-?[\d.]+)")

    def parse(data: dict[str, Any]) -> float | None:
        match = pattern.search(data.get("temperature") or "")
        return float(match.group(1)) if match else None

    return parse


@dataclass(frozen=True, kw_only=True)
class DevialetSensorDescription(SensorEntityDescription):
    """Describes how to read a sensor value from the settings payload."""

    value_fn: Callable[[dict[str, Any]], Any]


def _temperature_sensor(component: str) -> DevialetSensorDescription:
    return DevialetSensorDescription(
        key=f"{component.lower()}_temperature",
        translation_key=f"{component.lower()}_temperature",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=_temperature(component),
    )


SENSORS = (
    DevialetSensorDescription(
        key="currentsourcestate",
        translation_key="source_state",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("currentsourcestate"),
    ),
    DevialetSensorDescription(
        key="currentstreamtype",
        translation_key="stream_type",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("currentstreamtype"),
    ),
    DevialetSensorDescription(
        key="internalstate",
        translation_key="internal_state",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda data: data.get("internalstate"),
    ),
    _temperature_sensor("ASIC"),
    _temperature_sensor("DAMP"),
    _temperature_sensor("SOC"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DevialetConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    async_add_entities(
        DevialetSensor(entry.runtime_data, description) for description in SENSORS
    )


class DevialetSensor(DevialetEntity, SensorEntity):
    """A read-only value reported by the speaker."""

    entity_description: DevialetSensorDescription

    def __init__(
        self, coordinator: DevialetCoordinator, description: DevialetSensorDescription
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data)
