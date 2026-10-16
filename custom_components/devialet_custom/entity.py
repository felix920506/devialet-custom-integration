"""Base entity for Devialet Custom."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import DevialetCoordinator


class DevialetEntity(CoordinatorEntity[DevialetCoordinator]):
    """Entity attached to a Devialet Custom speaker."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: DevialetCoordinator, key: str) -> None:
        super().__init__(coordinator)
        info = coordinator.device_info
        serial = info["serial"]
        self._attr_unique_id = f"{serial}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            manufacturer=MANUFACTURER,
            model=info.get("model"),
            name=coordinator.data.get("friendlyname") or info.get("model"),
            serial_number=serial,
            sw_version=info.get("release", {}).get("version"),
            configuration_url=f"http://{coordinator.api.host}/",
        )
