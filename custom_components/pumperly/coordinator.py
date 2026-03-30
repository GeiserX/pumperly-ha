"""Data update coordinator for Pumperly."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import PumperlyApiClient, PumperlyConnectionError, PumperlyError
from .const import (
    CONF_FUEL_TYPES,
    CONF_RADIUS_KM,
    CONF_STATION_LIMIT,
    DEFAULT_STATION_LIMIT,
    DOMAIN,
    UPDATE_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)

type PumperlyConfigEntry = ConfigEntry[PumperlyCoordinator]


class PumperlyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator that polls Pumperly for station prices."""

    config_entry: PumperlyConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: PumperlyApiClient,
        config_entry: PumperlyConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=UPDATE_INTERVAL_MINUTES),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the Pumperly API."""
        data: dict[str, Any] = {"stations": {}, "stats": {}}
        config = self.config_entry.data

        lat = config[CONF_LATITUDE]
        lon = config[CONF_LONGITUDE]
        radius_km = config[CONF_RADIUS_KM]
        fuel_types: list[str] = config[CONF_FUEL_TYPES]
        limit = config.get(CONF_STATION_LIMIT, DEFAULT_STATION_LIMIT)

        try:
            stats = await self.client.async_get_stats()
            data["stats"] = stats.get("totals", {})
        except PumperlyError as err:
            _LOGGER.debug("Failed to fetch stats: %s", err)

        for fuel_type in fuel_types:
            try:
                stations = await self.client.async_get_nearest_stations(
                    lat=lat,
                    lon=lon,
                    radius_km=radius_km,
                    fuel=fuel_type,
                    limit=limit,
                )
                data["stations"][fuel_type] = stations
            except PumperlyConnectionError as err:
                raise UpdateFailed(
                    f"Cannot connect to Pumperly at {config[CONF_URL]}"
                ) from err
            except PumperlyError as err:
                _LOGGER.warning(
                    "Failed to fetch stations for %s: %s", fuel_type, err
                )
                data["stations"][fuel_type] = []

        return data
