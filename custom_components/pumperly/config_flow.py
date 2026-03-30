"""Config flow for Pumperly integration."""

from __future__ import annotations

import hashlib
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_LATITUDE, CONF_LONGITUDE, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    LocationSelector,
    LocationSelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)

from .api import PumperlyApiClient, PumperlyError
from .const import (
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

_LOGGER = logging.getLogger(__name__)


class PumperlyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pumperly."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._url: str = DEFAULT_URL
        self._latitude: float = 0.0
        self._longitude: float = 0.0
        self._fuel_types: list[str] = list(DEFAULT_FUEL_TYPES)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 1: Pumperly instance URL."""
        errors: dict[str, str] = {}

        if user_input is not None:
            url = user_input[CONF_URL].rstrip("/")
            self._url = url

            session = async_get_clientsession(self.hass)
            client = PumperlyApiClient(session, url)
            try:
                await client.async_get_config()
            except PumperlyError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected error validating Pumperly URL")
                errors["base"] = "unknown"
            else:
                return await self.async_step_location()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_URL, default=DEFAULT_URL): TextSelector(),
                }
            ),
            errors=errors,
        )

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 2: Location selection."""
        if user_input is not None:
            location = user_input["location"]
            self._latitude = location["latitude"]
            self._longitude = location["longitude"]
            return await self.async_step_fuel_types()

        default_lat = self.hass.config.latitude
        default_lon = self.hass.config.longitude

        return self.async_show_form(
            step_id="location",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "location",
                        default={
                            "latitude": default_lat,
                            "longitude": default_lon,
                        },
                    ): LocationSelector(LocationSelectorConfig(radius=False)),
                }
            ),
        )

    async def async_step_fuel_types(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 3: Select fuel types to track."""
        errors: dict[str, str] = {}

        if user_input is not None:
            selected = user_input.get(CONF_FUEL_TYPES, [])
            if not selected:
                errors[CONF_FUEL_TYPES] = "no_fuel_types"
            else:
                self._fuel_types = selected
                return await self.async_step_radius()

        options = [
            {"value": key, "label": label} for key, label in FUEL_TYPES.items()
        ]

        return self.async_show_form(
            step_id="fuel_types",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FUEL_TYPES, default=DEFAULT_FUEL_TYPES
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=options,
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_radius(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Step 4: Search radius."""
        if user_input is not None:
            radius_km = user_input[CONF_RADIUS_KM]

            unique_hash = hashlib.sha256(
                f"{self._url}:{self._latitude}:{self._longitude}".encode()
            ).hexdigest()[:12]
            await self.async_set_unique_id(unique_hash)
            self._abort_if_unique_id_configured()

            fuel_labels = [
                FUEL_TYPES.get(f, f) for f in self._fuel_types
            ]
            title = f"Pumperly ({', '.join(fuel_labels[:3])})"
            if len(fuel_labels) > 3:
                title += f" +{len(fuel_labels) - 3}"

            return self.async_create_entry(
                title=title,
                data={
                    CONF_URL: self._url,
                    CONF_LATITUDE: self._latitude,
                    CONF_LONGITUDE: self._longitude,
                    CONF_FUEL_TYPES: self._fuel_types,
                    CONF_RADIUS_KM: radius_km,
                },
            )

        return self.async_show_form(
            step_id="radius",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_RADIUS_KM, default=DEFAULT_RADIUS_KM
                    ): NumberSelector(
                        NumberSelectorConfig(
                            min=MIN_RADIUS_KM,
                            max=MAX_RADIUS_KM,
                            step=1,
                            unit_of_measurement="km",
                            mode=NumberSelectorMode.SLIDER,
                        )
                    ),
                }
            ),
        )
