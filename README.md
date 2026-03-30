# Pumperly Fuel Prices for Home Assistant

[![HACS Validation](https://github.com/GeiserX/pumperly-ha/actions/workflows/validate.yml/badge.svg)](https://github.com/GeiserX/pumperly-ha/actions/workflows/validate.yml)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Home Assistant custom integration that tracks **fuel and EV charging prices** from a [Pumperly](https://github.com/GeiserX/Pumperly) instance. Get real-time price data for 16 fuel types across 36 countries, directly in your smart home dashboard.

## Features

- Track cheapest, nearest, and average prices for any fuel type
- Support for gasoline, diesel, LPG, CNG, LNG, hydrogen, EV charging, and AdBlue
- Configurable search radius (1-50 km)
- Multi-step config flow with location picker
- Works with the public instance (pumperly.com) or self-hosted
- Diagnostic sensors for instance-wide statistics

## Prerequisites

- A running [Pumperly](https://github.com/GeiserX/Pumperly) instance, or use the public instance at `https://pumperly.com`
- Home Assistant 2024.1.0 or later
- [HACS](https://hacs.xyz/) installed

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click the three dots in the top-right corner and select **Custom repositories**
3. Add `https://github.com/GeiserX/pumperly-ha` with category **Integration**
4. Search for "Pumperly" and install it
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/pumperly` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to **Settings** > **Devices & Services** > **Add Integration**
2. Search for **Pumperly**
3. Follow the multi-step setup:
   - **Step 1**: Enter your Pumperly instance URL (default: `https://pumperly.com`)
   - **Step 2**: Select the location to search around (defaults to your Home zone)
   - **Step 3**: Choose which fuel types to track
   - **Step 4**: Set the search radius in kilometers

## Entities

For each configured fuel type, three sensors are created:

| Sensor | Description | Icon |
|--------|-------------|------|
| `sensor.pumperly_cheapest_{fuel}` | Lowest price among nearby stations | Fuel-specific |
| `sensor.pumperly_nearest_{fuel}` | Price at the closest station | `mdi:map-marker-radius` |
| `sensor.pumperly_average_{fuel}` | Average price across fetched stations | `mdi:chart-line` |

Each fuel sensor includes these extra attributes:
- `station_name`, `brand`, `address`, `city`
- `distance_km`, `reported_at`
- `latitude`, `longitude`

Two diagnostic sensors are always created:

| Sensor | Description |
|--------|-------------|
| `sensor.pumperly_total_stations` | Total stations in the Pumperly instance |
| `sensor.pumperly_total_prices` | Total price records in the Pumperly instance |

## Supported Fuel Types

| Code | Description |
|------|-------------|
| `E5` | Gasoline E5 (95) |
| `E5_PREMIUM` | Gasoline E5 Premium |
| `E10` | Gasoline E10 |
| `E5_98` | Gasoline E5 98 |
| `E98_E10` | Gasoline E98/E10 |
| `B7` | Diesel B7 |
| `B7_PREMIUM` | Diesel B7 Premium |
| `B_AGRICULTURAL` | Agricultural Diesel |
| `HVO` | HVO (Renewable Diesel) |
| `B10` | Diesel B10 |
| `LPG` | LPG (Autogas) |
| `CNG` | CNG (Compressed Natural Gas) |
| `LNG` | LNG (Liquefied Natural Gas) |
| `H2` | Hydrogen |
| `EV` | EV Charging |
| `ADBLUE` | AdBlue |

## Example Automations

### Fuel price drop notification

```yaml
automation:
  - alias: "Fuel price drop alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.pumperly_cheapest_diesel_b7
        below: 1.30
    action:
      - service: notify.mobile_app
        data:
          title: "Cheap Diesel!"
          message: >
            Diesel dropped to {{ states('sensor.pumperly_cheapest_diesel_b7') }}
            {{ state_attr('sensor.pumperly_cheapest_diesel_b7', 'currency') }}
            at {{ state_attr('sensor.pumperly_cheapest_diesel_b7', 'station_name') }}
            ({{ state_attr('sensor.pumperly_cheapest_diesel_b7', 'distance_km') }} km away)
```

### Dashboard card

```yaml
type: entities
title: Fuel Prices
entities:
  - entity: sensor.pumperly_cheapest_diesel_b7
    name: Cheapest Diesel
    secondary_info: last-updated
  - entity: sensor.pumperly_nearest_diesel_b7
    name: Nearest Diesel
  - entity: sensor.pumperly_average_diesel_b7
    name: Average Diesel
  - entity: sensor.pumperly_cheapest_gasoline_e5_95
    name: Cheapest Gasoline
```

## Data Refresh

Prices are polled every **30 minutes**. Fuel prices rarely change more frequently than this, and it keeps API load reasonable.

## Links

- [Pumperly](https://github.com/GeiserX/Pumperly) - The open-source fuel & EV route planner
- [pumperly.com](https://pumperly.com) - Public Pumperly instance
