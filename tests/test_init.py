"""Tests for the Pumperly integration __init__ module."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from custom_components.pumperly import async_setup_entry, async_unload_entry, PLATFORMS


def test_platforms_contains_sensor() -> None:
    """Test that PLATFORMS includes the sensor platform."""
    from homeassistant.const import Platform
    assert Platform.SENSOR in PLATFORMS


@pytest.mark.asyncio
async def test_async_setup_entry_success() -> None:
    """Test async_setup_entry creates coordinator and forwards platforms."""
    mock_hass = MagicMock()
    mock_hass.config_entries.async_forward_entry_setups = AsyncMock()

    mock_entry = MagicMock()
    mock_entry.data = {"url": "https://pumperly.com"}
    mock_entry.runtime_data = None

    mock_session = MagicMock()
    mock_coordinator = MagicMock()
    mock_coordinator.async_config_entry_first_refresh = AsyncMock()

    with patch(
        "custom_components.pumperly.async_get_clientsession",
        return_value=mock_session,
    ), patch(
        "custom_components.pumperly.PumperlyApiClient",
        return_value=MagicMock(),
    ) as mock_client_cls, patch(
        "custom_components.pumperly.PumperlyCoordinator",
        return_value=mock_coordinator,
    ) as mock_coord_cls:
        result = await async_setup_entry(mock_hass, mock_entry)

    assert result is True
    mock_coord_cls.assert_called_once()
    mock_coordinator.async_config_entry_first_refresh.assert_awaited_once()
    mock_hass.config_entries.async_forward_entry_setups.assert_awaited_once_with(
        mock_entry, PLATFORMS
    )
    assert mock_entry.runtime_data is mock_coordinator


@pytest.mark.asyncio
async def test_async_unload_entry_success() -> None:
    """Test async_unload_entry unloads platforms."""
    mock_hass = MagicMock()
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    mock_entry = MagicMock()

    result = await async_unload_entry(mock_hass, mock_entry)

    assert result is True
    mock_hass.config_entries.async_unload_platforms.assert_awaited_once_with(
        mock_entry, PLATFORMS
    )


@pytest.mark.asyncio
async def test_async_unload_entry_failure() -> None:
    """Test async_unload_entry returns False on failure."""
    mock_hass = MagicMock()
    mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)
    mock_entry = MagicMock()

    result = await async_unload_entry(mock_hass, mock_entry)

    assert result is False
