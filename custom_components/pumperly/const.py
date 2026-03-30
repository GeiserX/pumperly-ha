"""Constants for the Pumperly integration."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "pumperly"

CONF_FUEL_TYPES: Final = "fuel_types"
CONF_RADIUS_KM: Final = "radius_km"
CONF_STATION_LIMIT: Final = "station_limit"

DEFAULT_URL: Final = "https://pumperly.com"
DEFAULT_RADIUS_KM: Final = 10
DEFAULT_STATION_LIMIT: Final = 5
DEFAULT_FUEL_TYPES: Final = ["B7", "E5"]

MIN_RADIUS_KM: Final = 1
MAX_RADIUS_KM: Final = 50

UPDATE_INTERVAL_MINUTES: Final = 30

FUEL_TYPES: Final = {
    "E5": "Gasoline E5 (95)",
    "E5_PREMIUM": "Gasoline E5 Premium",
    "E10": "Gasoline E10",
    "E5_98": "Gasoline E5 98",
    "E98_E10": "Gasoline E98/E10",
    "B7": "Diesel B7",
    "B7_PREMIUM": "Diesel B7 Premium",
    "B_AGRICULTURAL": "Agricultural Diesel",
    "HVO": "HVO (Renewable Diesel)",
    "B10": "Diesel B10",
    "LPG": "LPG (Autogas)",
    "CNG": "CNG (Compressed Natural Gas)",
    "LNG": "LNG (Liquefied Natural Gas)",
    "H2": "Hydrogen",
    "EV": "EV Charging",
    "ADBLUE": "AdBlue",
}

FUEL_ICONS: Final = {
    "E5": "mdi:gas-station",
    "E5_PREMIUM": "mdi:gas-station",
    "E10": "mdi:gas-station",
    "E5_98": "mdi:gas-station",
    "E98_E10": "mdi:gas-station",
    "B7": "mdi:gas-station",
    "B7_PREMIUM": "mdi:gas-station",
    "B_AGRICULTURAL": "mdi:tractor",
    "HVO": "mdi:leaf",
    "B10": "mdi:gas-station",
    "LPG": "mdi:gas-station",
    "CNG": "mdi:gas-station",
    "LNG": "mdi:gas-station",
    "H2": "mdi:molecule-co2",
    "EV": "mdi:ev-station",
    "ADBLUE": "mdi:water",
}
