# Usage

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

## Fuel types

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

## Data refresh

Prices are polled every **30 minutes**. Fuel prices rarely change more frequently than this, and it keeps API load reasonable.

## Examples

### Fuel price drop notification

```yaml
automation:
  - alias: "Fuel price drop alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.pumperly_cheapest_diesel_b7
        below: 1.30
    action:
      - service: notify.mobile_app_<device_id>  # your phone's notify action, see Developer Tools > Actions
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
