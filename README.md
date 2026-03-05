# Zonspaarpot 2.0

Home Assistant custom integration for the Zonspaarpot (Power Return Optimizer / SSM-PRO) local API.

## Features

- Polls local API endpoints:
  - `GET /api`
  - `GET /api/v2/config`
  - `GET /api/v2/actual`
- Exposes sensors for:
  - Home consumption
  - Additional consumption
  - Active mode
  - HomeWizard values (if available)
  - P1 diagnostics
- Control entities:
  - Mode select (`Optimizing`, `Maximum load`, `API mode`)
  - Setload number (`0..2300` watt via `PUT /api/v2/setload`)

## Installation (HACS - custom repository)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=wmostert76&repository=zonspaarpot-2-0&category=integration)

Or follow these steps:
1. Install [HACS](https://hacs.xyz/) if you haven't already.
2. Add this repository as a [custom integration repository](https://hacs.xyz/docs/faq/custom_repositories) in HACS.
3. Restart Home Assistant.
4. Add the integration through the Home Assistant configuration flow.

## Installation (manual)

1. Copy `custom_components/zonspaarpot_2_0` to your Home Assistant `custom_components` folder.
2. Restart Home Assistant.
3. Add integration: `Settings -> Devices & Services -> Add Integration -> Zonspaarpot 2.0`.

## Configuration

- Host/IP: for example `192.168.180.109`
- Scan interval: in seconds (2..300, default 10)

## Notes

- The integration uses the device's local HTTP API without authentication.
- Ensure Home Assistant can reach the device on your LAN.
