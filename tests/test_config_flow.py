"""Tests for the Pumperly config flow - exercises the actual source code."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.pumperly.api import PumperlyConnectionError, PumperlyError
from custom_components.pumperly.config_flow import PumperlyConfigFlow
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
    expected = {
        "E5", "E5_PREMIUM", "E10", "E5_98", "E98_E10", "B7", "B7_PREMIUM",
        "B_AGRICULTURAL", "HVO", "B10", "LPG", "CNG", "LNG", "H2", "EV", "ADBLUE",
    }
    assert set(FUEL_TYPES.keys()) == expected


def test_config_flow_init() -> None:
    """Test config flow initializes with defaults."""
    flow = PumperlyConfigFlow()
    assert flow._url == DEFAULT_URL
    assert flow._latitude == 0.0
    assert flow._longitude == 0.0
    assert flow._fuel_types == list(DEFAULT_FUEL_TYPES)


def test_config_flow_version() -> None:
    """Test config flow version is 1."""
    assert PumperlyConfigFlow.VERSION == 1


@pytest.mark.asyncio
async def test_step_user_shows_form() -> None:
    """Test step_user shows form when no input provided."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    result = await flow.async_step_user(user_input=None)

    flow.async_show_form.assert_called_once()
    call_kwargs = flow.async_show_form.call_args
    assert call_kwargs.kwargs["step_id"] == "user"


@pytest.mark.asyncio
async def test_step_user_connection_error() -> None:
    """Test step_user shows error on connection failure."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    mock_client = MagicMock()
    mock_client.async_get_config = AsyncMock(side_effect=PumperlyError("fail"))

    with patch(
        "custom_components.pumperly.config_flow.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.pumperly.config_flow.PumperlyApiClient",
        return_value=mock_client,
    ):
        result = await flow.async_step_user(user_input={"url": "https://bad.example.com"})

    flow.async_show_form.assert_called_once()
    call_kwargs = flow.async_show_form.call_args
    assert call_kwargs.kwargs["errors"] == {"base": "cannot_connect"}


@pytest.mark.asyncio
async def test_step_user_unknown_error() -> None:
    """Test step_user shows unknown error on unexpected exception."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    mock_client = MagicMock()
    mock_client.async_get_config = AsyncMock(side_effect=RuntimeError("unexpected"))

    with patch(
        "custom_components.pumperly.config_flow.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.pumperly.config_flow.PumperlyApiClient",
        return_value=mock_client,
    ):
        result = await flow.async_step_user(user_input={"url": "https://bad.example.com"})

    call_kwargs = flow.async_show_form.call_args
    assert call_kwargs.kwargs["errors"] == {"base": "unknown"}


@pytest.mark.asyncio
async def test_step_user_success_proceeds_to_location() -> None:
    """Test step_user proceeds to location step on success."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_step_location = AsyncMock(return_value={"type": "form", "step_id": "location"})

    mock_client = MagicMock()
    mock_client.async_get_config = AsyncMock(return_value={"version": "1.0"})

    with patch(
        "custom_components.pumperly.config_flow.async_get_clientsession",
        return_value=MagicMock(),
    ), patch(
        "custom_components.pumperly.config_flow.PumperlyApiClient",
        return_value=mock_client,
    ):
        result = await flow.async_step_user(user_input={"url": "https://pumperly.com/"})

    assert flow._url == "https://pumperly.com"
    flow.async_step_location.assert_awaited_once()


@pytest.mark.asyncio
async def test_step_location_shows_form() -> None:
    """Test step_location shows form when no input provided."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.hass.config.latitude = 38.0
    flow.hass.config.longitude = -1.0
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    result = await flow.async_step_location(user_input=None)

    flow.async_show_form.assert_called_once()
    call_kwargs = flow.async_show_form.call_args
    assert call_kwargs.kwargs["step_id"] == "location"


@pytest.mark.asyncio
async def test_step_location_success_proceeds_to_fuel_types() -> None:
    """Test step_location proceeds to fuel_types on valid input."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_step_fuel_types = AsyncMock(return_value={"type": "form"})

    result = await flow.async_step_location(
        user_input={"location": {"latitude": 38.5, "longitude": -1.5}}
    )

    assert flow._latitude == 38.5
    assert flow._longitude == -1.5
    flow.async_step_fuel_types.assert_awaited_once()


@pytest.mark.asyncio
async def test_step_fuel_types_shows_form() -> None:
    """Test step_fuel_types shows form when no input provided."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    result = await flow.async_step_fuel_types(user_input=None)

    flow.async_show_form.assert_called_once()
    call_kwargs = flow.async_show_form.call_args
    assert call_kwargs.kwargs["step_id"] == "fuel_types"


@pytest.mark.asyncio
async def test_step_fuel_types_no_selection_error() -> None:
    """Test step_fuel_types shows error when no fuels selected."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    result = await flow.async_step_fuel_types(user_input={CONF_FUEL_TYPES: []})

    call_kwargs = flow.async_show_form.call_args
    assert call_kwargs.kwargs["errors"] == {CONF_FUEL_TYPES: "no_fuel_types"}


@pytest.mark.asyncio
async def test_step_fuel_types_success_proceeds_to_radius() -> None:
    """Test step_fuel_types proceeds to radius on valid input."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_step_radius = AsyncMock(return_value={"type": "form"})

    result = await flow.async_step_fuel_types(
        user_input={CONF_FUEL_TYPES: ["B7", "E5"]}
    )

    assert flow._fuel_types == ["B7", "E5"]
    flow.async_step_radius.assert_awaited_once()


@pytest.mark.asyncio
async def test_step_radius_shows_form() -> None:
    """Test step_radius shows form when no input provided."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow.async_show_form = MagicMock(return_value={"type": "form"})

    result = await flow.async_step_radius(user_input=None)

    flow.async_show_form.assert_called_once()
    call_kwargs = flow.async_show_form.call_args
    assert call_kwargs.kwargs["step_id"] == "radius"


@pytest.mark.asyncio
async def test_step_radius_creates_entry() -> None:
    """Test step_radius creates config entry with all data."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow._url = "https://pumperly.com"
    flow._latitude = 38.0
    flow._longitude = -1.0
    flow._fuel_types = ["B7", "E5"]
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

    result = await flow.async_step_radius(user_input={CONF_RADIUS_KM: 15})

    flow.async_set_unique_id.assert_awaited_once()
    flow._abort_if_unique_id_configured.assert_called_once()
    flow.async_create_entry.assert_called_once()

    call_kwargs = flow.async_create_entry.call_args
    data = call_kwargs.kwargs["data"]
    assert data["url"] == "https://pumperly.com"
    assert data["latitude"] == 38.0
    assert data["longitude"] == -1.0
    assert data[CONF_FUEL_TYPES] == ["B7", "E5"]
    assert data[CONF_RADIUS_KM] == 15


@pytest.mark.asyncio
async def test_step_radius_title_truncation() -> None:
    """Test step_radius truncates title when many fuel types selected."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow._url = "https://pumperly.com"
    flow._latitude = 38.0
    flow._longitude = -1.0
    flow._fuel_types = ["B7", "E5", "LPG", "CNG", "H2"]
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

    await flow.async_step_radius(user_input={CONF_RADIUS_KM: 10})

    call_kwargs = flow.async_create_entry.call_args
    title = call_kwargs.kwargs["title"]
    assert "+2" in title  # 5 fuels, show first 3 + "+2"


@pytest.mark.asyncio
async def test_step_radius_title_no_truncation() -> None:
    """Test step_radius doesn't truncate when 3 or fewer fuel types."""
    flow = PumperlyConfigFlow()
    flow.hass = MagicMock()
    flow._url = "https://pumperly.com"
    flow._latitude = 38.0
    flow._longitude = -1.0
    flow._fuel_types = ["B7"]
    flow.async_set_unique_id = AsyncMock()
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_create_entry = MagicMock(return_value={"type": "create_entry"})

    await flow.async_step_radius(user_input={CONF_RADIUS_KM: 10})

    call_kwargs = flow.async_create_entry.call_args
    title = call_kwargs.kwargs["title"]
    assert "+" not in title
    assert "Diesel B7" in title
