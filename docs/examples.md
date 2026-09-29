# Examples

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
