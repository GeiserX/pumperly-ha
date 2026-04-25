"""Tests for the Pumperly coordinator - exercises the actual source code."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from custom_components.pumperly.api import PumperlyConnectionError, PumperlyError
from custom_components.pumperly.coordinator import PumperlyCoordinator
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

MOCK_CONFIG_DATA_WITH_LIMIT = {
    **MOCK_CONFIG_DATA,
    CONF_STATION_LIMIT: 3,
}


def _make_coordinator(config_data=None, client=None):
    """Create a PumperlyCoordinator with mocked dependencies."""
    mock_hass = MagicMock()
    if client is None:
        client = MagicMock()
    mock_entry = MagicMock()
    mock_entry.entry_id = "test-entry"
    mock_entry.data = config_data or MOCK_CONFIG_DATA
    return PumperlyCoordinator(mock_hass, client, mock_entry)


def test_update_interval() -> None:
    """Verify the update interval is 30 minutes."""
    assert UPDATE_INTERVAL_MINUTES == 30
    coordinator = _make_coordinator()
    assert coordinator.update_interval == timedelta(minutes=30)


def test_default_station_limit() -> None:
    """Verify default station limit is 5."""
    assert DEFAULT_STATION_LIMIT == 5


def test_coordinator_stores_client() -> None:
    """Test coordinator stores the API client reference."""
    client = MagicMock()
    coordinator = _make_coordinator(client=client)
    assert coordinator.client is client


@pytest.mark.asyncio
async def test_async_update_data_success() -> None:
    """Test _async_update_data fetches stats and stations for all fuel types."""
    client = MagicMock()
    client.async_get_stats = AsyncMock(return_value=MOCK_STATS)
    client.async_get_nearest_stations = AsyncMock(return_value=[MOCK_STATION_B7])

    coordinator = _make_coordinator(client=client)
    data = await coordinator._async_update_data()

    assert data["stats"]["stations"] == 1234
    assert data["stats"]["prices"] == 56789
    assert "B7" in data["stations"]
    assert "E5" in data["stations"]
    assert len(data["stations"]["B7"]) == 1
    assert client.async_get_nearest_stations.call_count == 2


@pytest.mark.asyncio
async def test_async_update_data_with_custom_limit() -> None:
    """Test _async_update_data uses custom station limit from config."""
    client = MagicMock()
    client.async_get_stats = AsyncMock(return_value=MOCK_STATS)
    client.async_get_nearest_stations = AsyncMock(return_value=[MOCK_STATION_B7])

    coordinator = _make_coordinator(config_data=MOCK_CONFIG_DATA_WITH_LIMIT, client=client)
    await coordinator._async_update_data()

    # Verify limit=3 was passed
    for call_args in client.async_get_nearest_stations.call_args_list:
        assert call_args.kwargs["limit"] == 3


@pytest.mark.asyncio
async def test_async_update_data_stats_failure_continues() -> None:
    """Test that stats failure doesn't prevent station fetching."""
    client = MagicMock()
    client.async_get_stats = AsyncMock(side_effect=PumperlyError("no stats"))
    client.async_get_nearest_stations = AsyncMock(return_value=[MOCK_STATION_B7])

    coordinator = _make_coordinator(client=client)
    data = await coordinator._async_update_data()

    # Stats should be empty dict (failure was caught)
    assert data["stats"] == {}
    # Stations should still be fetched
    assert len(data["stations"]["B7"]) == 1


@pytest.mark.asyncio
async def test_async_update_data_connection_error_raises_update_failed() -> None:
    """Test that connection errors on station fetch raise UpdateFailed."""
    from homeassistant.helpers.update_coordinator import UpdateFailed

    client = MagicMock()
    client.async_get_stats = AsyncMock(return_value=MOCK_STATS)
    client.async_get_nearest_stations = AsyncMock(
        side_effect=PumperlyConnectionError("fail")
    )

    coordinator = _make_coordinator(client=client)
    with pytest.raises(UpdateFailed):
        await coordinator._async_update_data()


@pytest.mark.asyncio
async def test_async_update_data_api_error_returns_empty_stations() -> None:
    """Test that non-connection API errors result in empty station list."""
    client = MagicMock()
    client.async_get_stats = AsyncMock(return_value=MOCK_STATS)
    client.async_get_nearest_stations = AsyncMock(
        side_effect=PumperlyError("bad data")
    )

    coordinator = _make_coordinator(client=client)
    data = await coordinator._async_update_data()

    # Stations should be empty for each fuel type
    assert data["stations"]["B7"] == []
    assert data["stations"]["E5"] == []


@pytest.mark.asyncio
async def test_async_update_data_default_station_limit() -> None:
    """Test _async_update_data uses DEFAULT_STATION_LIMIT when not in config."""
    client = MagicMock()
    client.async_get_stats = AsyncMock(return_value=MOCK_STATS)
    client.async_get_nearest_stations = AsyncMock(return_value=[])

    coordinator = _make_coordinator(client=client)
    await coordinator._async_update_data()

    for call_args in client.async_get_nearest_stations.call_args_list:
        assert call_args.kwargs["limit"] == DEFAULT_STATION_LIMIT
