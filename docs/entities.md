# Entities and fuel types

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

## Supported fuel types

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
