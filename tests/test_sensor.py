"""Tests for Pumperly sensor module - exercises the actual source code."""

from __future__ import annotations

import pytest

from custom_components.pumperly.sensor import (
    _fuel_label,
    _get_stations,
    _station_props,
    _station_coords,
    _station_extra_attrs,
    _get_currency,
    PumperlyCheapestSensor,
    PumperlyNearestSensor,
    PumperlyAverageSensor,
    PumperlyTotalStationsSensor,
    PumperlyTotalPricesSensor,
    async_setup_entry,
)
from custom_components.pumperly.const import FUEL_ICONS, FUEL_TYPES

from .conftest import (
    MOCK_STATION_B7,
    MOCK_STATION_B7_CHEAP,
    MOCK_STATION_NO_PRICE,
    MOCK_STATION_NO_DISTANCE,
    MOCK_STATION_EMPTY_GEOMETRY,
    make_mock_coordinator,
)


# --- Helper function tests ---


def test_fuel_label_known() -> None:
    """Test known fuel type returns label."""
    assert _fuel_label("B7") == "Diesel B7"
    assert _fuel_label("E5") == "Gasoline E5 (95)"


def test_fuel_label_unknown() -> None:
    """Test unknown fuel type returns the key itself."""
    assert _fuel_label("UNKNOWN_FUEL") == "UNKNOWN_FUEL"


def test_fuel_icons_all_defined() -> None:
    """Test all fuel types have icons."""
    for key in FUEL_TYPES:
        assert key in FUEL_ICONS


def test_get_stations_with_data() -> None:
    """Test _get_stations returns station list from coordinator data."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7]}, "stats": {}}
    )
    result = _get_stations(coordinator, "B7")
    assert len(result) == 1
    assert result[0] is MOCK_STATION_B7


def test_get_stations_none_data() -> None:
    """Test _get_stations returns empty list when coordinator data is None."""
    coordinator = make_mock_coordinator(data=None)
    result = _get_stations(coordinator, "B7")
    assert result == []


def test_get_stations_missing_fuel_type() -> None:
    """Test _get_stations returns empty list for missing fuel type."""
    coordinator = make_mock_coordinator(
        data={"stations": {"E5": [MOCK_STATION_B7]}, "stats": {}}
    )
    result = _get_stations(coordinator, "B7")
    assert result == []


def test_station_props() -> None:
    """Test extracting properties from a station."""
    props = _station_props(MOCK_STATION_B7)
    assert props["name"] == "Test Station"
    assert props["price"] == 1.459


def test_station_props_empty() -> None:
    """Test extracting properties from empty dict."""
    props = _station_props({})
    assert props == {}


def test_station_coords() -> None:
    """Test extracting coordinates from a station."""
    lat, lon = _station_coords(MOCK_STATION_B7)
    assert lat == pytest.approx(38.01)
    assert lon == pytest.approx(-1.01)


def test_station_coords_missing() -> None:
    """Test missing coordinates return None."""
    lat, lon = _station_coords({})
    assert lat is None
    assert lon is None


def test_station_coords_empty_coordinates() -> None:
    """Test empty coordinates list returns None."""
    lat, lon = _station_coords(MOCK_STATION_EMPTY_GEOMETRY)
    assert lat is None
    assert lon is None


def test_station_extra_attrs() -> None:
    """Test building extra state attributes from a station."""
    attrs = _station_extra_attrs(MOCK_STATION_B7)
    assert attrs["station_name"] == "Test Station"
    assert attrs["brand"] == "TestBrand"
    assert attrs["address"] == "123 Fuel St"
    assert attrs["city"] == "TestCity"
    assert attrs["distance_km"] == 1.5
    assert attrs["reported_at"] == "2026-01-01T12:00:00Z"
    assert attrs["latitude"] == pytest.approx(38.01)
    assert attrs["longitude"] == pytest.approx(-1.01)
    assert attrs["station_id"] == "station-1"


def test_station_extra_attrs_empty() -> None:
    """Test extra attrs from station with no properties."""
    attrs = _station_extra_attrs({})
    assert attrs["station_name"] is None
    assert attrs["latitude"] is None


def test_get_currency() -> None:
    """Test currency extraction."""
    assert _get_currency([MOCK_STATION_B7]) == "EUR"


def test_get_currency_empty() -> None:
    """Test currency with no stations returns None."""
    assert _get_currency([]) is None


def test_get_currency_no_currency_field() -> None:
    """Test currency when no station has currency."""
    assert _get_currency([MOCK_STATION_NO_PRICE]) is None


# --- Cheapest Sensor ---


def test_cheapest_sensor_native_value() -> None:
    """Test cheapest sensor returns min price."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]}, "stats": {}}
    )
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    assert sensor.native_value == 1.299


def test_cheapest_sensor_native_value_empty() -> None:
    """Test cheapest sensor returns None with no stations."""
    coordinator = make_mock_coordinator(data={"stations": {"B7": []}, "stats": {}})
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    assert sensor.native_value is None


def test_cheapest_sensor_native_value_no_prices() -> None:
    """Test cheapest sensor returns None when stations have no prices."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_NO_PRICE]}, "stats": {}}
    )
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    assert sensor.native_value is None


def test_cheapest_sensor_unit() -> None:
    """Test cheapest sensor returns currency unit."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7]}, "stats": {}}
    )
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    assert sensor.native_unit_of_measurement == "EUR"


def test_cheapest_sensor_extra_attrs() -> None:
    """Test cheapest sensor returns cheapest station attributes."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]}, "stats": {}}
    )
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["station_name"] == "Cheap Station"


def test_cheapest_sensor_extra_attrs_empty() -> None:
    """Test cheapest sensor returns None attrs with no stations."""
    coordinator = make_mock_coordinator(data={"stations": {"B7": []}, "stats": {}})
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    assert sensor.extra_state_attributes is None


def test_cheapest_sensor_extra_attrs_no_prices() -> None:
    """Test cheapest sensor returns None attrs when no station has price."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_NO_PRICE]}, "stats": {}}
    )
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    assert sensor.extra_state_attributes is None


def test_cheapest_sensor_unique_id() -> None:
    """Test cheapest sensor unique_id format."""
    coordinator = make_mock_coordinator()
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    assert sensor._attr_unique_id == "test-entry-id_cheapest_B7"


def test_cheapest_sensor_icon() -> None:
    """Test cheapest sensor uses fuel-specific icon."""
    coordinator = make_mock_coordinator()
    sensor = PumperlyCheapestSensor(coordinator, "B7")
    assert sensor._attr_icon == "mdi:gas-station"


def test_cheapest_sensor_icon_unknown_fuel() -> None:
    """Test cheapest sensor falls back to default icon for unknown fuel."""
    coordinator = make_mock_coordinator()
    sensor = PumperlyCheapestSensor(coordinator, "UNKNOWN")
    assert sensor._attr_icon == "mdi:gas-station"


# --- Nearest Sensor ---


def test_nearest_sensor_native_value() -> None:
    """Test nearest sensor returns nearest station's price."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]}, "stats": {}}
    )
    sensor = PumperlyNearestSensor(coordinator, "B7")
    # MOCK_STATION_B7 has distance_km=1.5, MOCK_STATION_B7_CHEAP has 3.0
    assert sensor.native_value == 1.459


def test_nearest_sensor_native_value_empty() -> None:
    """Test nearest sensor returns None with no stations."""
    coordinator = make_mock_coordinator(data={"stations": {"B7": []}, "stats": {}})
    sensor = PumperlyNearestSensor(coordinator, "B7")
    assert sensor.native_value is None


def test_nearest_sensor_native_value_no_distance() -> None:
    """Test nearest sensor returns None when no station has distance_km."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_NO_DISTANCE]}, "stats": {}}
    )
    sensor = PumperlyNearestSensor(coordinator, "B7")
    assert sensor.native_value is None


def test_nearest_sensor_native_value_no_price_on_nearest() -> None:
    """Test nearest sensor returns None when nearest station has no price."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_NO_PRICE]}, "stats": {}}
    )
    sensor = PumperlyNearestSensor(coordinator, "B7")
    # Station has distance_km but no price
    assert sensor.native_value is None


def test_nearest_sensor_unit() -> None:
    """Test nearest sensor returns currency unit."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7]}, "stats": {}}
    )
    sensor = PumperlyNearestSensor(coordinator, "B7")
    assert sensor.native_unit_of_measurement == "EUR"


def test_nearest_sensor_extra_attrs() -> None:
    """Test nearest sensor returns nearest station attributes."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]}, "stats": {}}
    )
    sensor = PumperlyNearestSensor(coordinator, "B7")
    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["station_name"] == "Test Station"


def test_nearest_sensor_extra_attrs_empty() -> None:
    """Test nearest sensor returns None attrs with no stations."""
    coordinator = make_mock_coordinator(data={"stations": {"B7": []}, "stats": {}})
    sensor = PumperlyNearestSensor(coordinator, "B7")
    assert sensor.extra_state_attributes is None


def test_nearest_sensor_extra_attrs_no_distance() -> None:
    """Test nearest sensor returns None attrs when no station has distance."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_NO_DISTANCE]}, "stats": {}}
    )
    sensor = PumperlyNearestSensor(coordinator, "B7")
    assert sensor.extra_state_attributes is None


def test_nearest_sensor_unique_id() -> None:
    """Test nearest sensor unique_id format."""
    coordinator = make_mock_coordinator()
    sensor = PumperlyNearestSensor(coordinator, "E5")
    assert sensor._attr_unique_id == "test-entry-id_nearest_E5"


# --- Average Sensor ---


def test_average_sensor_native_value() -> None:
    """Test average sensor returns mean price."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]}, "stats": {}}
    )
    sensor = PumperlyAverageSensor(coordinator, "B7")
    expected = round((1.459 + 1.299) / 2, 3)
    assert sensor.native_value == expected


def test_average_sensor_native_value_single() -> None:
    """Test average sensor with a single station."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7]}, "stats": {}}
    )
    sensor = PumperlyAverageSensor(coordinator, "B7")
    assert sensor.native_value == 1.459


def test_average_sensor_native_value_empty() -> None:
    """Test average sensor returns None with no stations."""
    coordinator = make_mock_coordinator(data={"stations": {"B7": []}, "stats": {}})
    sensor = PumperlyAverageSensor(coordinator, "B7")
    assert sensor.native_value is None


def test_average_sensor_native_value_no_prices() -> None:
    """Test average sensor returns None when stations have no prices."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_NO_PRICE]}, "stats": {}}
    )
    sensor = PumperlyAverageSensor(coordinator, "B7")
    assert sensor.native_value is None


def test_average_sensor_unit() -> None:
    """Test average sensor returns currency unit."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7]}, "stats": {}}
    )
    sensor = PumperlyAverageSensor(coordinator, "B7")
    assert sensor.native_unit_of_measurement == "EUR"


def test_average_sensor_extra_attrs() -> None:
    """Test average sensor returns station count."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]}, "stats": {}}
    )
    sensor = PumperlyAverageSensor(coordinator, "B7")
    attrs = sensor.extra_state_attributes
    assert attrs is not None
    assert attrs["station_count"] == 2


def test_average_sensor_extra_attrs_empty() -> None:
    """Test average sensor returns None attrs when no prices."""
    coordinator = make_mock_coordinator(
        data={"stations": {"B7": [MOCK_STATION_NO_PRICE]}, "stats": {}}
    )
    sensor = PumperlyAverageSensor(coordinator, "B7")
    assert sensor.extra_state_attributes is None


def test_average_sensor_unique_id() -> None:
    """Test average sensor unique_id format."""
    coordinator = make_mock_coordinator()
    sensor = PumperlyAverageSensor(coordinator, "B7")
    assert sensor._attr_unique_id == "test-entry-id_average_B7"


# --- Total Stations Sensor ---


def test_total_stations_value() -> None:
    """Test total stations sensor returns station count from stats."""
    coordinator = make_mock_coordinator(
        data={"stations": {}, "stats": {"stations": 1234, "prices": 5678}}
    )
    sensor = PumperlyTotalStationsSensor(coordinator)
    assert sensor.native_value == 1234


def test_total_stations_value_none_data() -> None:
    """Test total stations sensor returns None when data is None."""
    coordinator = make_mock_coordinator(data=None)
    sensor = PumperlyTotalStationsSensor(coordinator)
    assert sensor.native_value is None


def test_total_stations_value_missing_key() -> None:
    """Test total stations sensor returns None when key missing."""
    coordinator = make_mock_coordinator(data={"stations": {}, "stats": {}})
    sensor = PumperlyTotalStationsSensor(coordinator)
    assert sensor.native_value is None


def test_total_stations_unique_id() -> None:
    """Test total stations sensor unique_id format."""
    coordinator = make_mock_coordinator()
    sensor = PumperlyTotalStationsSensor(coordinator)
    assert sensor._attr_unique_id == "test-entry-id_total_stations"


# --- Total Prices Sensor ---


def test_total_prices_value() -> None:
    """Test total prices sensor returns price count from stats."""
    coordinator = make_mock_coordinator(
        data={"stations": {}, "stats": {"stations": 1234, "prices": 5678}}
    )
    sensor = PumperlyTotalPricesSensor(coordinator)
    assert sensor.native_value == 5678


def test_total_prices_value_none_data() -> None:
    """Test total prices sensor returns None when data is None."""
    coordinator = make_mock_coordinator(data=None)
    sensor = PumperlyTotalPricesSensor(coordinator)
    assert sensor.native_value is None


def test_total_prices_unique_id() -> None:
    """Test total prices sensor unique_id format."""
    coordinator = make_mock_coordinator()
    sensor = PumperlyTotalPricesSensor(coordinator)
    assert sensor._attr_unique_id == "test-entry-id_total_prices"


# --- async_setup_entry ---


@pytest.mark.asyncio
async def test_async_setup_entry() -> None:
    """Test sensor platform setup creates correct entities."""
    from unittest.mock import MagicMock, call

    coordinator = make_mock_coordinator(
        data={
            "stations": {"B7": [MOCK_STATION_B7], "E5": []},
            "stats": {"stations": 100, "prices": 500},
        }
    )

    mock_entry = coordinator.config_entry
    mock_hass = MagicMock()
    mock_add_entities = MagicMock()

    await async_setup_entry(mock_hass, mock_entry, mock_add_entities)

    mock_add_entities.assert_called_once()
    entities = mock_add_entities.call_args[0][0]
    # 2 fuel types x 3 sensors each + 2 diagnostic = 8
    assert len(entities) == 8

    # Check types
    cheapest = [e for e in entities if isinstance(e, PumperlyCheapestSensor)]
    nearest = [e for e in entities if isinstance(e, PumperlyNearestSensor)]
    average = [e for e in entities if isinstance(e, PumperlyAverageSensor)]
    total_stations = [e for e in entities if isinstance(e, PumperlyTotalStationsSensor)]
    total_prices = [e for e in entities if isinstance(e, PumperlyTotalPricesSensor)]

    assert len(cheapest) == 2
    assert len(nearest) == 2
    assert len(average) == 2
    assert len(total_stations) == 1
    assert len(total_prices) == 1
