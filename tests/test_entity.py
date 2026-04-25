"""Tests for the Pumperly base entity - exercises the actual source code."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from custom_components.pumperly.entity import PumperlyEntity
from custom_components.pumperly.const import DOMAIN

from .conftest import make_mock_coordinator


def test_entity_has_entity_name() -> None:
    """Test entity has _attr_has_entity_name set to True."""
    coordinator = make_mock_coordinator()
    entity = PumperlyEntity(coordinator)
    assert entity._attr_has_entity_name is True


def test_entity_device_info_called_with_correct_args() -> None:
    """Test entity creates DeviceInfo with correct parameters."""
    from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType

    coordinator = make_mock_coordinator(entry_id="my-entry-123")

    # Reset the mock to capture our call
    DeviceInfo.reset_mock()

    entity = PumperlyEntity(coordinator)

    # Verify DeviceInfo was called with the right kwargs
    DeviceInfo.assert_called_once()
    call_kwargs = DeviceInfo.call_args
    assert call_kwargs.kwargs["identifiers"] == {(DOMAIN, "my-entry-123")}
    assert call_kwargs.kwargs["name"] == "Pumperly"
    assert call_kwargs.kwargs["manufacturer"] == "Pumperly"
    assert call_kwargs.kwargs["model"] == "Fuel Price Tracker"
    assert call_kwargs.kwargs["configuration_url"] == "https://pumperly.example.com"


def test_entity_device_info_entry_type() -> None:
    """Test entity device_info uses SERVICE entry type."""
    from homeassistant.helpers.device_registry import DeviceInfo, DeviceEntryType

    coordinator = make_mock_coordinator()
    DeviceInfo.reset_mock()

    entity = PumperlyEntity(coordinator)

    call_kwargs = DeviceInfo.call_args
    assert call_kwargs.kwargs["entry_type"] is DeviceEntryType.SERVICE


def test_entity_stores_coordinator() -> None:
    """Test entity stores reference to coordinator."""
    coordinator = make_mock_coordinator()
    entity = PumperlyEntity(coordinator)
    assert entity.coordinator is coordinator
