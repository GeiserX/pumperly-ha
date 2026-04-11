"""Common fixtures and HA mocks for Pumperly tests."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock, AsyncMock

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
    mods["homeassistant.config_entries"] = config_entries

    # helpers
    for mod_name in [
        "homeassistant.helpers",
        "homeassistant.helpers.aiohttp_client",
        "homeassistant.helpers.device_registry",
        "homeassistant.helpers.entity_platform",
        "homeassistant.helpers.selector",
        "homeassistant.helpers.update_coordinator",
    ]:
        mods[mod_name] = MagicMock()

    # sensor component
    sensor_mod = MagicMock()
    sensor_mod.SensorDeviceClass = MagicMock()
    sensor_mod.SensorDeviceClass.MONETARY = "monetary"
    sensor_mod.SensorStateClass = MagicMock()
    sensor_mod.SensorStateClass.MEASUREMENT = "measurement"
    sensor_mod.SensorStateClass.TOTAL = "total"
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

MOCK_STATS = {
    "totals": {"stations": 1234, "prices": 56789},
}
