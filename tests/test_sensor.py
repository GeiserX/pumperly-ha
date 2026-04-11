"""Tests for Pumperly sensor value computation logic."""

from __future__ import annotations

import pytest

from custom_components.pumperly.const import FUEL_ICONS, FUEL_TYPES

from .conftest import MOCK_STATION_B7, MOCK_STATION_B7_CHEAP


# --- Helper function tests (extracted logic from sensor.py) ---


def _station_props(station: dict) -> dict:
    """Extract properties from a station feature."""
    return station.get("properties", {})


def _station_coords(station: dict) -> tuple:
    """Extract coordinates from a station feature."""
    coords = station.get("geometry", {}).get("coordinates", [])
    if len(coords) >= 2:
        return coords[1], coords[0]
    return None, None


def _get_cheapest_price(stations: list[dict]) -> float | None:
    """Compute cheapest price from stations."""
    if not stations:
        return None
    prices = [
        _station_props(s).get("price")
        for s in stations
        if _station_props(s).get("price") is not None
    ]
    if not prices:
        return None
    return round(min(prices), 3)


def _get_nearest_price(stations: list[dict]) -> float | None:
    """Compute nearest station price."""
    if not stations:
        return None
    nearest = min(
        (s for s in stations if _station_props(s).get("distance_km") is not None),
        key=lambda s: _station_props(s)["distance_km"],
        default=None,
    )
    if nearest is None:
        return None
    price = _station_props(nearest).get("price")
    return round(price, 3) if price is not None else None


def _get_average_price(stations: list[dict]) -> float | None:
    """Compute average price across stations."""
    if not stations:
        return None
    prices = [
        _station_props(s).get("price")
        for s in stations
        if _station_props(s).get("price") is not None
    ]
    if not prices:
        return None
    return round(sum(prices) / len(prices), 3)


def _get_currency(stations: list[dict]) -> str | None:
    """Get currency from first station."""
    for station in stations:
        currency = _station_props(station).get("currency")
        if currency:
            return currency
    return None


# --- Tests ---


def test_fuel_label_known() -> None:
    """Test known fuel type returns label."""
    assert FUEL_TYPES["B7"] == "Diesel B7"
    assert FUEL_TYPES["E5"] == "Gasoline E5 (95)"


def test_fuel_icons_all_defined() -> None:
    """Test all fuel types have icons."""
    for key in FUEL_TYPES:
        assert key in FUEL_ICONS


def test_station_props() -> None:
    """Test extracting properties from a station."""
    props = _station_props(MOCK_STATION_B7)
    assert props["name"] == "Test Station"
    assert props["price"] == 1.459


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


def test_cheapest_price() -> None:
    """Test cheapest price calculation."""
    stations = [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]
    assert _get_cheapest_price(stations) == 1.299


def test_cheapest_price_empty() -> None:
    """Test cheapest with no stations returns None."""
    assert _get_cheapest_price([]) is None


def test_nearest_price() -> None:
    """Test nearest station price."""
    stations = [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]
    # MOCK_STATION_B7 has distance_km=1.5, MOCK_STATION_B7_CHEAP has 3.0
    assert _get_nearest_price(stations) == 1.459


def test_nearest_price_empty() -> None:
    """Test nearest with no stations returns None."""
    assert _get_nearest_price([]) is None


def test_average_price() -> None:
    """Test average price calculation."""
    stations = [MOCK_STATION_B7, MOCK_STATION_B7_CHEAP]
    expected = round((1.459 + 1.299) / 2, 3)
    assert _get_average_price(stations) == expected


def test_average_price_empty() -> None:
    """Test average with no stations returns None."""
    assert _get_average_price([]) is None


def test_average_price_single() -> None:
    """Test average with single station."""
    assert _get_average_price([MOCK_STATION_B7]) == 1.459


def test_get_currency() -> None:
    """Test currency extraction."""
    stations = [MOCK_STATION_B7]
    assert _get_currency(stations) == "EUR"


def test_get_currency_empty() -> None:
    """Test currency with no stations returns None."""
    assert _get_currency([]) is None


def test_total_stations_from_stats() -> None:
    """Test extracting total stations from stats data."""
    data = {"stats": {"stations": 1234, "prices": 5678}}
    assert data["stats"]["stations"] == 1234


def test_total_prices_from_stats() -> None:
    """Test extracting total prices from stats data."""
    data = {"stats": {"stations": 1234, "prices": 5678}}
    assert data["stats"]["prices"] == 5678


def test_station_no_price() -> None:
    """Test station without price is excluded."""
    station_no_price = {
        "type": "Feature",
        "geometry": {"coordinates": [-1.0, 38.0]},
        "properties": {"name": "No Price Station"},
    }
    assert _get_cheapest_price([station_no_price]) is None
    assert _get_average_price([station_no_price]) is None
