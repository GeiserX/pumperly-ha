"""Tests for the Pumperly API client."""

from __future__ import annotations

import aiohttp
import pytest
from aiohttp import ClientSession
from aiohttp.test_utils import TestServer
from aiohttp.web import Application, Request, Response, json_response

from custom_components.pumperly.api import (
    PumperlyApiClient,
    PumperlyConnectionError,
    PumperlyError,
)


def test_compute_bbox() -> None:
    """Test bounding box computation."""
    bbox = PumperlyApiClient._compute_bbox(38.0, -1.0, 10.0)
    assert len(bbox) == 4
    min_lon, min_lat, max_lon, max_lat = bbox
    assert min_lat < 38.0 < max_lat
    assert min_lon < -1.0 < max_lon


def test_compute_bbox_symmetry() -> None:
    """Test bbox is roughly symmetric around the center."""
    lat, lon = 40.0, -3.0
    bbox = PumperlyApiClient._compute_bbox(lat, lon, 5.0)
    min_lon, min_lat, max_lon, max_lat = bbox
    assert pytest.approx(max_lat - lat, abs=0.01) == pytest.approx(lat - min_lat, abs=0.01)


def test_haversine_zero_distance() -> None:
    """Same point should return 0."""
    dist = PumperlyApiClient._haversine(38.0, -1.0, 38.0, -1.0)
    assert dist == pytest.approx(0.0, abs=0.01)


def test_haversine_known_distance() -> None:
    """Test with a known pair of coordinates."""
    dist = PumperlyApiClient._haversine(40.4168, -3.7038, 41.3851, 2.1734)
    assert 490 < dist < 520


def test_haversine_commutative() -> None:
    """Distance should be the same regardless of direction."""
    d1 = PumperlyApiClient._haversine(38.0, -1.0, 40.0, 2.0)
    d2 = PumperlyApiClient._haversine(40.0, 2.0, 38.0, -1.0)
    assert d1 == pytest.approx(d2, abs=0.001)


@pytest.mark.asyncio
async def test_get_config_success() -> None:
    """Test fetching config successfully."""
    app = Application()

    async def handle_config(request: Request) -> Response:
        return json_response({"version": "1.0"})

    app.router.add_get("/api/config", handle_config)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = PumperlyApiClient(session, str(server.make_url("")))
            result = await client.async_get_config()
            assert result["version"] == "1.0"


@pytest.mark.asyncio
async def test_get_config_404_raises() -> None:
    """Test that 404 on config raises PumperlyError."""
    app = Application()

    async def handle_config(request: Request) -> Response:
        return Response(status=404)

    app.router.add_get("/api/config", handle_config)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = PumperlyApiClient(session, str(server.make_url("")))
            with pytest.raises(PumperlyError, match="not found"):
                await client.async_get_config()


@pytest.mark.asyncio
async def test_get_stats_returns_defaults_on_404() -> None:
    """Test that 404 on stats returns default totals."""
    app = Application()

    async def handle_stats(request: Request) -> Response:
        return Response(status=404)

    app.router.add_get("/api/stats", handle_stats)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = PumperlyApiClient(session, str(server.make_url("")))
            result = await client.async_get_stats()
            assert result == {"totals": {"stations": 0, "prices": 0}}


@pytest.mark.asyncio
async def test_get_stats_success() -> None:
    """Test fetching stats successfully."""
    app = Application()

    async def handle_stats(request: Request) -> Response:
        return json_response({"totals": {"stations": 100, "prices": 500}})

    app.router.add_get("/api/stats", handle_stats)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = PumperlyApiClient(session, str(server.make_url("")))
            result = await client.async_get_stats()
            assert result["totals"]["stations"] == 100


@pytest.mark.asyncio
async def test_connection_error() -> None:
    """Test that unreachable server raises PumperlyConnectionError."""
    async with ClientSession() as session:
        client = PumperlyApiClient(session, "http://127.0.0.1:1")
        with pytest.raises(PumperlyConnectionError):
            await client.async_get_config()


@pytest.mark.asyncio
async def test_nearest_stations_uses_nearest_endpoint() -> None:
    """Test that nearest endpoint is tried first."""
    app = Application()

    async def handle_nearest(request: Request) -> Response:
        return json_response(
            {
                "features": [
                    {
                        "geometry": {"coordinates": [-1.0, 38.0]},
                        "properties": {"price": 1.3, "distance_km": 1.0},
                    }
                ]
            }
        )

    app.router.add_get("/api/stations/nearest", handle_nearest)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = PumperlyApiClient(session, str(server.make_url("")))
            stations = await client.async_get_nearest_stations(38.0, -1.0, 10.0, "B7", 5)
            assert len(stations) == 1
            assert stations[0]["properties"]["price"] == 1.3


@pytest.mark.asyncio
async def test_nearest_stations_fallback_to_bbox() -> None:
    """Test fallback to bbox query when nearest returns 404."""
    app = Application()

    async def handle_nearest(request: Request) -> Response:
        return Response(status=404)

    async def handle_stations(request: Request) -> Response:
        return json_response(
            {
                "features": [
                    {
                        "geometry": {"coordinates": [-1.0, 38.0]},
                        "properties": {"price": 1.5},
                    }
                ]
            }
        )

    app.router.add_get("/api/stations/nearest", handle_nearest)
    app.router.add_get("/api/stations", handle_stations)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = PumperlyApiClient(session, str(server.make_url("")))
            stations = await client.async_get_nearest_stations(38.0, -1.0, 10.0, "B7", 5)
            assert len(stations) == 1


@pytest.mark.asyncio
async def test_http_500_raises() -> None:
    """Test that HTTP 500 raises PumperlyError."""
    app = Application()

    async def handle(request: Request) -> Response:
        return Response(status=500)

    app.router.add_get("/api/config", handle)

    async with TestServer(app) as server:
        async with ClientSession() as session:
            client = PumperlyApiClient(session, str(server.make_url("")))
            with pytest.raises(PumperlyError):
                await client.async_get_config()
