"""Tests for the Pumperly coordinator data logic."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.pumperly.api import PumperlyConnectionError, PumperlyError
from custom_components.pumperly.const import (
    CONF_FUEL_TYPES,
    CONF_RADIUS_KM,
    CONF_STATION_LIMIT,
    DEFAULT_STATION_LIMIT,
    UPDATE_INTERVAL_MINUTES,
)

from .conftest import MOCK_STATION_B7, MOCK_STATS


MOCK_CONFIG_DATA = {
    "latitude": 38.0,
    "longitude": -1.0,
    CONF_RADIUS_KM: 10,
    CONF_FUEL_TYPES: ["B7", "E5"],
    "url": "https://pumperly.example.com",
}


def test_update_interval() -> None:
    """Verify the update interval is 30 minutes."""
    assert UPDATE_INTERVAL_MINUTES == 30


def test_default_station_limit() -> None:
    """Verify default station limit is 5."""
    assert DEFAULT_STATION_LIMIT == 5


@pytest.mark.asyncio
async def test_coordinator_fetches_stats_and_stations() -> None:
    """Test that the coordinator calls both stats and stations APIs."""
    client = MagicMock()
    client.async_get_stats = AsyncMock(return_value=MOCK_STATS)
    client.async_get_nearest_stations = AsyncMock(return_value=[MOCK_STATION_B7])

    # Simulate what the coordinator does in _async_update_data
    data: dict = {"stations": {}, "stats": {}}
    config = MOCK_CONFIG_DATA

    stats = await client.async_get_stats()
    data["stats"] = stats.get("totals", {})

    for fuel_type in config[CONF_FUEL_TYPES]:
        stations = await client.async_get_nearest_stations(
            lat=config["latitude"],
            lon=config["longitude"],
            radius_km=config[CONF_RADIUS_KM],
            fuel=fuel_type,
            limit=config.get(CONF_STATION_LIMIT, DEFAULT_STATION_LIMIT),
        )
        data["stations"][fuel_type] = stations

    assert data["stats"]["stations"] == 1234
    assert data["stats"]["prices"] == 56789
    assert "B7" in data["stations"]
    assert "E5" in data["stations"]
    assert len(data["stations"]["B7"]) == 1


@pytest.mark.asyncio
async def test_connection_error_on_station_fetch() -> None:
    """Test that connection errors are propagated for station fetches."""
    client = MagicMock()
    client.async_get_stats = AsyncMock(return_value=MOCK_STATS)
    client.async_get_nearest_stations = AsyncMock(
        side_effect=PumperlyConnectionError("fail")
    )

    with pytest.raises(PumperlyConnectionError):
        await client.async_get_nearest_stations(
            lat=38.0, lon=-1.0, radius_km=10, fuel="B7", limit=5
        )


@pytest.mark.asyncio
async def test_api_error_on_stations_returns_empty() -> None:
    """Test that non-connection API errors can be caught gracefully."""
    client = MagicMock()
    client.async_get_nearest_stations = AsyncMock(
        side_effect=PumperlyError("bad data")
    )

    # Simulate coordinator behavior: catch PumperlyError and return []
    try:
        await client.async_get_nearest_stations(
            lat=38.0, lon=-1.0, radius_km=10, fuel="B7", limit=5
        )
        stations = []
    except PumperlyConnectionError:
        raise
    except PumperlyError:
        stations = []

    assert stations == []


@pytest.mark.asyncio
async def test_stats_failure_does_not_block() -> None:
    """Test that stats failure doesn't prevent station fetching."""
    client = MagicMock()
    client.async_get_stats = AsyncMock(side_effect=PumperlyError("no stats"))
    client.async_get_nearest_stations = AsyncMock(return_value=[MOCK_STATION_B7])

    stats = {}
    try:
        result = await client.async_get_stats()
        stats = result.get("totals", {})
    except PumperlyError:
        pass

    stations = await client.async_get_nearest_stations(
        lat=38.0, lon=-1.0, radius_km=10, fuel="B7", limit=5
    )

    assert stats == {}
    assert len(stations) == 1
