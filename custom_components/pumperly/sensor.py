"""Sensor platform for Pumperly."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_FUEL_TYPES, DOMAIN, FUEL_ICONS, FUEL_TYPES
from .coordinator import PumperlyConfigEntry, PumperlyCoordinator
from .entity import PumperlyEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: PumperlyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Pumperly sensors from a config entry."""
    coordinator: PumperlyCoordinator = entry.runtime_data

    fuel_types: list[str] = entry.data[CONF_FUEL_TYPES]
    entities: list[SensorEntity] = []

    for fuel_type in fuel_types:
        entities.extend(
            [
                PumperlyCheapestSensor(coordinator, fuel_type),
                PumperlyNearestSensor(coordinator, fuel_type),
                PumperlyAverageSensor(coordinator, fuel_type),
            ]
        )

    entities.extend(
        [
            PumperlyTotalStationsSensor(coordinator),
            PumperlyTotalPricesSensor(coordinator),
        ]
    )

    async_add_entities(entities)


def _fuel_label(fuel_type: str) -> str:
    """Return a human-readable label for a fuel type."""
    return FUEL_TYPES.get(fuel_type, fuel_type)


def _get_stations(coordinator: PumperlyCoordinator, fuel_type: str) -> list[dict]:
    """Safely get station list for a fuel type."""
    if coordinator.data is None:
        return []
    return coordinator.data.get("stations", {}).get(fuel_type, [])


def _station_props(station: dict[str, Any]) -> dict[str, Any]:
    """Extract properties from a station feature."""
    return station.get("properties", {})


def _station_coords(station: dict[str, Any]) -> tuple[float | None, float | None]:
    """Extract coordinates from a station feature."""
    coords = station.get("geometry", {}).get("coordinates", [])
    if len(coords) >= 2:
        return coords[1], coords[0]
    return None, None


def _station_extra_attrs(station: dict[str, Any]) -> dict[str, Any]:
    """Build extra state attributes from a station."""
    props = _station_props(station)
    lat, lon = _station_coords(station)
    return {
        "station_name": props.get("name"),
        "brand": props.get("brand"),
        "address": props.get("address"),
        "city": props.get("city"),
        "distance_km": props.get("distance_km"),
        "reported_at": props.get("reportedAt"),
        "latitude": lat,
        "longitude": lon,
        "station_id": props.get("id"),
    }


def _get_currency(stations: list[dict]) -> str | None:
    """Get currency from the first station with a price."""
    for station in stations:
        currency = _station_props(station).get("currency")
        if currency:
            return currency
    return None


class PumperlyCheapestSensor(PumperlyEntity, SensorEntity):
    """Sensor showing the cheapest station price for a fuel type."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.MONETARY

    def __init__(
        self, coordinator: PumperlyCoordinator, fuel_type: str
    ) -> None:
        """Initialize the cheapest sensor."""
        super().__init__(coordinator)
        self._fuel_type = fuel_type
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_cheapest_{fuel_type}"
        )
        self._attr_translation_key = "cheapest"
        self._attr_translation_placeholders = {"fuel": _fuel_label(fuel_type)}
        self._attr_icon = FUEL_ICONS.get(fuel_type, "mdi:gas-station")

    @property
    def native_value(self) -> float | None:
        """Return the cheapest price."""
        stations = _get_stations(self.coordinator, self._fuel_type)
        if not stations:
            return None
        prices = [
            _station_props(s).get("price")
            for s in stations
            if _station_props(s).get("price") is not None
        ]
        if not prices:
            return None
        cheapest_price = min(prices)
        return round(cheapest_price, 3)

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the currency unit."""
        stations = _get_stations(self.coordinator, self._fuel_type)
        return _get_currency(stations)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return attributes of the cheapest station."""
        stations = _get_stations(self.coordinator, self._fuel_type)
        if not stations:
            return None
        cheapest = min(
            (s for s in stations if _station_props(s).get("price") is not None),
            key=lambda s: _station_props(s)["price"],
            default=None,
        )
        if cheapest is None:
            return None
        return _station_extra_attrs(cheapest)


class PumperlyNearestSensor(PumperlyEntity, SensorEntity):
    """Sensor showing the nearest station price for a fuel type."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.MONETARY

    def __init__(
        self, coordinator: PumperlyCoordinator, fuel_type: str
    ) -> None:
        """Initialize the nearest sensor."""
        super().__init__(coordinator)
        self._fuel_type = fuel_type
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_nearest_{fuel_type}"
        )
        self._attr_translation_key = "nearest"
        self._attr_translation_placeholders = {"fuel": _fuel_label(fuel_type)}
        self._attr_icon = "mdi:map-marker-radius"

    @property
    def native_value(self) -> float | None:
        """Return the price of the nearest station."""
        stations = _get_stations(self.coordinator, self._fuel_type)
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

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the currency unit."""
        stations = _get_stations(self.coordinator, self._fuel_type)
        return _get_currency(stations)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return attributes of the nearest station."""
        stations = _get_stations(self.coordinator, self._fuel_type)
        if not stations:
            return None
        nearest = min(
            (s for s in stations if _station_props(s).get("distance_km") is not None),
            key=lambda s: _station_props(s)["distance_km"],
            default=None,
        )
        if nearest is None:
            return None
        return _station_extra_attrs(nearest)


class PumperlyAverageSensor(PumperlyEntity, SensorEntity):
    """Sensor showing the average price across fetched stations."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_device_class = SensorDeviceClass.MONETARY

    def __init__(
        self, coordinator: PumperlyCoordinator, fuel_type: str
    ) -> None:
        """Initialize the average sensor."""
        super().__init__(coordinator)
        self._fuel_type = fuel_type
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_average_{fuel_type}"
        )
        self._attr_translation_key = "average"
        self._attr_translation_placeholders = {"fuel": _fuel_label(fuel_type)}
        self._attr_icon = "mdi:chart-line"

    @property
    def native_value(self) -> float | None:
        """Return the average price across stations."""
        stations = _get_stations(self.coordinator, self._fuel_type)
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

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the currency unit."""
        stations = _get_stations(self.coordinator, self._fuel_type)
        return _get_currency(stations)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the number of stations in the average."""
        stations = _get_stations(self.coordinator, self._fuel_type)
        prices = [
            _station_props(s).get("price")
            for s in stations
            if _station_props(s).get("price") is not None
        ]
        return {"station_count": len(prices)} if prices else None


class PumperlyTotalStationsSensor(PumperlyEntity, SensorEntity):
    """Diagnostic sensor showing total stations tracked by the instance."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:gas-station"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_translation_key = "total_stations"

    def __init__(self, coordinator: PumperlyCoordinator) -> None:
        """Initialize the total stations sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_total_stations"
        )

    @property
    def native_value(self) -> int | None:
        """Return total station count."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("stats", {}).get("stations")


class PumperlyTotalPricesSensor(PumperlyEntity, SensorEntity):
    """Diagnostic sensor showing total price records tracked by the instance."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_icon = "mdi:tag-multiple"
    _attr_state_class = SensorStateClass.TOTAL
    _attr_translation_key = "total_prices"

    def __init__(self, coordinator: PumperlyCoordinator) -> None:
        """Initialize the total prices sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = (
            f"{coordinator.config_entry.entry_id}_total_prices"
        )

    @property
    def native_value(self) -> int | None:
        """Return total price record count."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("stats", {}).get("prices")
