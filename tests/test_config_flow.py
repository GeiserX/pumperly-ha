"""Tests for the Pumperly config flow logic."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.pumperly.api import PumperlyConnectionError, PumperlyError
from custom_components.pumperly.const import (
    CONF_FUEL_TYPES,
    CONF_RADIUS_KM,
    DEFAULT_FUEL_TYPES,
    DEFAULT_RADIUS_KM,
    DEFAULT_URL,
    DOMAIN,
    FUEL_TYPES,
    MAX_RADIUS_KM,
    MIN_RADIUS_KM,
)


def test_domain_constant() -> None:
    """Test the domain is correctly defined."""
    assert DOMAIN == "pumperly"


def test_default_url() -> None:
    """Test the default URL."""
    assert DEFAULT_URL == "https://pumperly.com"


def test_default_fuel_types() -> None:
    """Test default fuel types include B7 and E5."""
    assert "B7" in DEFAULT_FUEL_TYPES
    assert "E5" in DEFAULT_FUEL_TYPES


def test_radius_bounds() -> None:
    """Test radius boundaries."""
    assert MIN_RADIUS_KM == 1
    assert MAX_RADIUS_KM == 50
    assert MIN_RADIUS_KM <= DEFAULT_RADIUS_KM <= MAX_RADIUS_KM


def test_fuel_types_complete() -> None:
    """Test all expected fuel types are defined."""
    expected = {"E5", "E5_PREMIUM", "E10", "E5_98", "E98_E10", "B7", "B7_PREMIUM",
                "B_AGRICULTURAL", "HVO", "B10", "LPG", "CNG", "LNG", "H2", "EV", "ADBLUE"}
    assert set(FUEL_TYPES.keys()) == expected


@pytest.mark.asyncio
async def test_api_client_validates_connection() -> None:
    """Test that config flow would detect connection errors."""
    from custom_components.pumperly.api import PumperlyApiClient

    # Unreachable server
    import aiohttp
    async with aiohttp.ClientSession() as session:
        client = PumperlyApiClient(session, "http://127.0.0.1:1")
        with pytest.raises(PumperlyConnectionError):
            await client.async_get_config()


@pytest.mark.asyncio
async def test_api_client_validates_url_stripping() -> None:
    """Test that trailing slashes are stripped from URL."""
    from custom_components.pumperly.api import PumperlyApiClient

    import aiohttp
    async with aiohttp.ClientSession() as session:
        client = PumperlyApiClient(session, "https://pumperly.com/")
        assert client._base_url == "https://pumperly.com"
