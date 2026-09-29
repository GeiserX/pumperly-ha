# Installation and configuration

## Prerequisites

- A running [Pumperly](https://github.com/GeiserX/Pumperly) instance, or use the public instance at `https://pumperly.com`
- Home Assistant 2024.1.0 or later
- [HACS](https://hacs.xyz/) installed

## Installation

### HACS (recommended)

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

