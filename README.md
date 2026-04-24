# NHL Playoffs Dashboard

Home Assistant custom integration and Lovelace dashboard for NHL playoff tracking.

## What it contains

- `custom_components/nhl_playoffs/`
  - `manifest.json` — integration metadata for Home Assistant and HACS
  - `config_flow.py` — UI setup flow for the integration
  - `const.py` — domain, option keys, and default values
  - `sensor.py` — sensor platform setup entrypoint
  - `coordinator/` — data update coordinator logic
  - `sensors/` — sensor entity definitions
  - `translations/en.json` — integration translations and UI strings
- `lovelace/nhl_playoffs_dashboard.yaml` — Lovelace dashboard configuration for the playoff view
- `hacs.json` — HACS repository metadata for community distribution

## Installation

### Manual install

1. Copy the full `custom_components/nhl_playoffs/` folder into your Home Assistant `config/custom_components/` directory.
2. Restart Home Assistant.
3. Install the required Lovelace custom cards:
   - `button-card`
   - `layout-card`
4. Open Home Assistant and add the `NHL Playoffs` integration from the Integrations page.
5. Use the dashboard YAML in `lovelace/nhl_playoffs_dashboard.yaml` to create or update your Lovelace view.

### HACS install

1. In HACS, go to `Integrations` > `Custom repositories`.
2. Add this repository as a custom integration repository.
3. Install the `NHL Playoffs Dashboard` integration from HACS.
4. Install the required Lovelace cards from HACS:
   - `button-card`
   - `layout-card`
5. Restart Home Assistant after installation.

> `lovelace/nhl_playoffs_dashboard.yaml` includes the required resource references for these custom cards.

## Required Lovelace resources

If you are using the dashboard YAML directly, make sure the following resources are available in Home Assistant:

- `button-card`: `/hacsfiles/button-card/button-card.js`
- `layout-card`: `/hacsfiles/layout-card/layout-card.js`

If you install the cards through HACS, these URLs will be added automatically.

## Usage

### Configuration

1. After installation, go to **Settings** > **Devices & Services** > **Integrations**.
2. Click **Create Integration** and select **NHL Playoffs**.
3. In the config flow, choose your season mode:
   - **Current season (auto-detect)**: Fetches data for the current year automatically.
   - **Manual season (override)**: Select a specific year to display past playoffs (e.g., `20232024` for the 2023-2024 season).
4. Complete the setup.

### Dashboard

- The dashboard YAML is a starter page for the Stanley Cup playoffs bracket display.
- It expects sensor entities named `sensor.playoffs_r1_west_*`, `sensor.playoffs_r2_west_*`, etc.

## Notes

- The custom component currently includes the basic integration structure and sensor platform wiring.
- The dashboard requires these Lovelace custom cards:
  - `button-card`
  - `layout-card`
- Add your NHL API and data-fetching logic inside `custom_components/nhl_playoffs/coordinator/` and `custom_components/nhl_playoffs/sensors/`.
- Keep `manifest.json` and `hacs.json` updated with any dependency or metadata changes.

## License

This project is licensed under the **MIT License**. See the terms below:

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
