"""Async API client for Pumperly."""

from __future__ import annotations

import math
from typing import Any

import aiohttp


class PumperlyError(Exception):
    """Base exception for Pumperly API errors."""


class PumperlyConnectionError(PumperlyError):
    """Connection error communicating with Pumperly."""


class PumperlyApiClient:
    """Async HTTP client for the Pumperly REST API."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._base_url = base_url.rstrip("/")

    async def _request(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        """Make an HTTP request to the Pumperly API."""
        url = f"{self._base_url}{path}"
        try:
            async with self._session.request(
                method, url, params=params, timeout=aiohttp.ClientTimeout(total=30)
            ) as resp:
                if resp.status == 404:
                    return None
                resp.raise_for_status()
                return await resp.json()
        except aiohttp.ClientConnectionError as err:
            raise PumperlyConnectionError(
                f"Cannot connect to Pumperly at {self._base_url}"
            ) from err
        except aiohttp.ClientError as err:
            raise PumperlyError(
                f"Error communicating with Pumperly: {err}"
            ) from err

    async def async_get_config(self) -> dict[str, Any]:
        """Get Pumperly instance configuration."""
        result = await self._request("GET", "/api/config")
        if result is None:
            raise PumperlyError("Config endpoint not found")
        return result

    async def async_get_stats(self) -> dict[str, Any]:
        """Get Pumperly statistics."""
        result = await self._request("GET", "/api/stats")
        if result is None:
            return {"totals": {"stations": 0, "prices": 0}}
        return result

    async def async_get_nearest_stations(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        fuel: str,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Fetch nearest stations for a fuel type.

        Tries the /api/stations/nearest endpoint first. If unavailable (404),
        falls back to /api/stations with a computed bounding box, sorting
        results by distance client-side.
        """
        stations = await self._try_nearest_endpoint(lat, lon, radius_km, fuel, limit)
        if stations is not None:
            return stations

        return await self._fallback_bbox_query(lat, lon, radius_km, fuel, limit)

    async def _try_nearest_endpoint(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        fuel: str,
        limit: int,
    ) -> list[dict[str, Any]] | None:
        """Try the dedicated nearest-stations endpoint."""
        result = await self._request(
            "GET",
            "/api/stations/nearest",
            params={
                "lat": lat,
                "lon": lon,
                "radius_km": radius_km,
                "fuel": fuel,
                "limit": limit,
            },
        )
        if result is None:
            return None

        features = result.get("features", []) if isinstance(result, dict) else result
        return features[:limit] if isinstance(features, list) else []

    async def _fallback_bbox_query(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        fuel: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Fall back to bounding-box query with client-side distance sort."""
        bbox = self._compute_bbox(lat, lon, radius_km)
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"

        result = await self._request(
            "GET",
            "/api/stations",
            params={"bbox": bbox_str, "fuel": fuel},
        )
        if result is None:
            return []

        features = result.get("features", []) if isinstance(result, dict) else []
        if not isinstance(features, list):
            return []

        for feature in features:
            coords = (
                feature.get("geometry", {}).get("coordinates", [None, None])
            )
            if coords and len(coords) >= 2:
                dist = self._haversine(lat, lon, coords[1], coords[0])
                feature.setdefault("properties", {})["distance_km"] = round(dist, 2)

        features.sort(
            key=lambda f: f.get("properties", {}).get("distance_km", float("inf"))
        )

        return [
            f
            for f in features[:limit]
            if f.get("properties", {}).get("distance_km", float("inf")) <= radius_km
        ]

    @staticmethod
    def _compute_bbox(
        lat: float, lon: float, radius_km: float
    ) -> tuple[float, float, float, float]:
        """Compute a bounding box around a point.

        Returns (min_lon, min_lat, max_lon, max_lat).
        """
        lat_offset = radius_km / 111.0
        lon_offset = radius_km / (111.0 * math.cos(math.radians(lat)))

        return (
            round(lon - lon_offset, 6),
            round(lat - lat_offset, 6),
            round(lon + lon_offset, 6),
            round(lat + lat_offset, 6),
        )

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km between two points using the Haversine formula."""
        r = 6371.0
        d_lat = math.radians(lat2 - lat1)
        d_lon = math.radians(lon2 - lon1)
        a = (
            math.sin(d_lat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(d_lon / 2) ** 2
        )
        return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
