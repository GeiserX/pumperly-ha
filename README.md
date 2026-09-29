<p align="center">
  <img src="https://raw.githubusercontent.com/GeiserX/pumperly-ha/main/docs/images/banner.svg" alt="Pumperly for Home Assistant banner" width="900"/>
</p>

# Pumperly Fuel Prices for Home Assistant

[![HACS Validation](https://github.com/GeiserX/pumperly-ha/actions/workflows/validate.yml/badge.svg)](https://github.com/GeiserX/pumperly-ha/actions/workflows/validate.yml)
[![Tests](https://github.com/GeiserX/pumperly-ha/actions/workflows/tests.yml/badge.svg)](https://github.com/GeiserX/pumperly-ha/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/GeiserX/pumperly-ha/graph/badge.svg)](https://codecov.io/gh/GeiserX/pumperly-ha)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

A Home Assistant custom integration that tracks **fuel and EV charging prices** from a [Pumperly](https://github.com/GeiserX/Pumperly) instance. Get real-time price data for 16 fuel types across 36 countries, directly in your smart home dashboard.

## Features

- Track cheapest, nearest, and average prices for any fuel type
- Support for gasoline, diesel, LPG, CNG, LNG, hydrogen, EV charging, and AdBlue
- Configurable search radius (1-50 km)
- Multi-step config flow with location picker
- Works with the public instance (pumperly.com) or self-hosted
- Diagnostic sensors for instance-wide statistics
- Polls every 30 minutes

## Quick start

1. In HACS, open **Custom repositories** and add `https://github.com/GeiserX/pumperly-ha` with category **Integration**.
2. Install **Pumperly** and restart Home Assistant.
3. Go to **Settings** > **Devices & Services** > **Add Integration** and search for **Pumperly**.

Manual install, prerequisites and the setup steps are in [Installation](https://github.com/GeiserX/pumperly-ha/blob/main/docs/installation.md).

## Documentation

- [Installation and configuration](https://github.com/GeiserX/pumperly-ha/blob/main/docs/installation.md)
- [Entities and fuel types](https://github.com/GeiserX/pumperly-ha/blob/main/docs/entities.md): sensors, attributes, fuel codes, refresh interval
- [Examples](https://github.com/GeiserX/pumperly-ha/blob/main/docs/examples.md): a price-drop automation and a dashboard card
- [Related projects](https://github.com/GeiserX/pumperly-ha/blob/main/docs/related.md)

Related: [Pumperly](https://github.com/GeiserX/Pumperly), the open-source fuel and EV route planner, and its public instance [pumperly.com](https://pumperly.com).

## License

[GPL-3.0](https://github.com/GeiserX/pumperly-ha/blob/main/LICENSE)
