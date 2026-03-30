"""Base entity for Pumperly."""

from __future__ import annotations

from homeassistant.const import CONF_URL
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import PumperlyCoordinator


class PumperlyEntity(CoordinatorEntity[PumperlyCoordinator]):
    """Base class for Pumperly entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PumperlyCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Pumperly",
            manufacturer="Pumperly",
            model="Fuel Price Tracker",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=entry.data[CONF_URL],
        )
