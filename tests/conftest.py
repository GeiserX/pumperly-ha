"""Common fixtures and HA mocks for Pumperly tests."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, AsyncMock, PropertyMock

import pytest


def _make_ha_mocks():
    """Create minimal mocks for homeassistant modules so imports work."""
    mods = {}

    # homeassistant
    ha = MagicMock()
    mods["homeassistant"] = ha

    # homeassistant.core
    core = MagicMock()
    mods["homeassistant.core"] = core

    # homeassistant.const
    const = ModuleType("homeassistant.const")
    const.CONF_LATITUDE = "latitude"
    const.CONF_LONGITUDE = "longitude"
    const.CONF_URL = "url"
    const.Platform = MagicMock()
    const.Platform.SENSOR = "sensor"
    const.EntityCategory = MagicMock()
    const.EntityCategory.DIAGNOSTIC = "diagnostic"
    mods["homeassistant.const"] = const

    # config_entries
    config_entries = MagicMock()

    class FakeConfigEntry:
        """Fake ConfigEntry that supports generic subscript."""

        def __class_getitem__(cls, item):
            return cls

    class FakeConfigFlow:
        """Fake ConfigFlow base class."""

        def __init_subclass__(cls, domain=None, **kwargs):
            super().__init_subclass__(**kwargs)
            if domain:
                cls.domain = domain

    config_entries.ConfigEntry = FakeConfigEntry
    config_entries.ConfigFlow = FakeConfigFlow
    config_entries.ConfigFlowResult = dict
    mods["homeassistant.config_entries"] = config_entries

    # helpers
    for mod_name in [
        "homeassistant.helpers",
        "homeassistant.helpers.aiohttp_client",
        "homeassistant.helpers.device_registry",
        "homeassistant.helpers.entity_platform",
        "homeassistant.helpers.selector",
    ]:
        mods[mod_name] = MagicMock()

    # update_coordinator - needs real base classes
    update_coordinator_mod = MagicMock()

    class FakeDataUpdateCoordinator:
        """Fake DataUpdateCoordinator for testing."""

        def __init_subclass__(cls, **kwargs):
            super().__init_subclass__(**kwargs)

        def __class_getitem__(cls, item):
            return cls

        def __init__(self, hass, logger, *, name, update_interval, config_entry=None):
            self.hass = hass
            self.logger = logger
            self.name = name
            self.update_interval = update_interval
            self.config_entry = config_entry
            self.data = None

        async def async_config_entry_first_refresh(self):
            pass

    class FakeCoordinatorEntity:
        """Fake CoordinatorEntity for testing."""

        def __class_getitem__(cls, item):
            return cls

        def __init__(self, coordinator):
            self.coordinator = coordinator

    update_coordinator_mod.DataUpdateCoordinator = FakeDataUpdateCoordinator
    update_coordinator_mod.CoordinatorEntity = FakeCoordinatorEntity
    update_coordinator_mod.UpdateFailed = type("UpdateFailed", (Exception,), {})
    mods["homeassistant.helpers.update_coordinator"] = update_coordinator_mod

    # sensor component
    sensor_mod = MagicMock()
    sensor_mod.SensorDeviceClass = MagicMock()
    sensor_mod.SensorDeviceClass.MONETARY = "monetary"
    sensor_mod.SensorStateClass = MagicMock()
    sensor_mod.SensorStateClass.MEASUREMENT = "measurement"
    sensor_mod.SensorStateClass.TOTAL = "total"
    sensor_mod.SensorEntity = type("SensorEntity", (), {})
    mods["homeassistant.components"] = MagicMock()
    mods["homeassistant.components.sensor"] = sensor_mod

    # data_entry_flow
    mods["homeassistant.data_entry_flow"] = MagicMock()

    return mods


# Install HA mocks before any custom_components import
_ha_mocks = _make_ha_mocks()
for name, mod in _ha_mocks.items():
    sys.modules[name] = mod


MOCK_STATION_B7 = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [-1.01, 38.01]},
    "properties": {
        "id": "station-1",
        "name": "Test Station",
        "brand": "TestBrand",
        "address": "123 Fuel St",
        "city": "TestCity",
        "price": 1.459,
        "currency": "EUR",
        "distance_km": 1.5,
        "reportedAt": "2026-01-01T12:00:00Z",
    },
}

MOCK_STATION_B7_CHEAP = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [-1.02, 38.02]},
    "properties": {
        "id": "station-2",
        "name": "Cheap Station",
        "brand": "CheapBrand",
        "address": "456 Cheap Rd",
        "city": "CheapCity",
        "price": 1.299,
        "currency": "EUR",
        "distance_km": 3.0,
        "reportedAt": "2026-01-01T12:00:00Z",
    },
}

MOCK_STATION_NO_PRICE = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [-1.03, 38.03]},
    "properties": {
        "id": "station-3",
        "name": "No Price Station",
        "brand": "NoBrand",
        "distance_km": 2.0,
    },
}

MOCK_STATION_NO_DISTANCE = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": [-1.04, 38.04]},
    "properties": {
        "id": "station-4",
        "name": "No Distance Station",
        "price": 1.5,
        "currency": "EUR",
    },
}

MOCK_STATION_EMPTY_GEOMETRY = {
    "type": "Feature",
    "geometry": {"type": "Point", "coordinates": []},
    "properties": {
        "id": "station-5",
        "name": "Empty Geom Station",
        "price": 1.6,
        "distance_km": 4.0,
    },
}

MOCK_STATS = {
    "totals": {"stations": 1234, "prices": 56789},
}


def make_mock_coordinator(data=None, fuel_types=None, entry_id="test-entry-id"):
    """Create a mock coordinator with configurable data."""
    from custom_components.pumperly.coordinator import PumperlyCoordinator

    mock_hass = MagicMock()
    mock_client = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = entry_id
    mock_entry.data = {
        "url": "https://pumperly.example.com",
        "latitude": 38.0,
        "longitude": -1.0,
        "fuel_types": fuel_types or ["B7", "E5"],
        "radius_km": 10,
    }

    coordinator = PumperlyCoordinator(mock_hass, mock_client, mock_entry)
    coordinator.data = data
    return coordinator
