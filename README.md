# NHL Playoffs Dashboard

Home Assistant custom integration and Lovelace dashboard for NHL playoff tracking.

## What it contains

- `custom_components/nhl_playoffs/` — custom integration metadata and setup stub
- `lovelace/nhl_playoffs_dashboard.yaml` — Lovelace dashboard configuration
- `hacs.json` — HACS repository metadata for community distribution

## Installation

### Manual install

1. Copy `custom_components/nhl_playoffs/` into your Home Assistant `config/custom_components/` folder.
2. Restart Home Assistant.
3. Add the dashboard YAML from `lovelace/nhl_playoffs_dashboard.yaml` into your Lovelace dashboard.

### HACS install

This repository is configured for HACS. Add it as a custom repository in HACS if you want to install it from there.

## Usage

- The integration domain is `nhl_playoffs`.
- The dashboard file includes a simple starter page for the Stanley Cup playoffs.

## Notes

- The current integration stub returns `True` in `async_setup()`; add your NHL API logic in `custom_components/nhl_playoffs/`.
- For community sharing, keep `manifest.json` and `hacs.json` up to date with the integration metadata.

## License

Add your preferred license here if you want to share this publicly.
