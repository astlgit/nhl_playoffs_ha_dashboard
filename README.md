# NHL Playoffs Dashboard

Home Assistant custom integration and Lovelace dashboard for NHL playoff tracking.

## What it contains

- `custom_components/nhl_playoffs/` — Home Assistant integration files
- `lovelace/nhl_playoffs_dashboard.yaml` — Lovelace dashboard configuration
- `www/nhl/` — Local images folder (contains `tbd.png` placeholder and setup instructions)
- `images/` — Screenshots for documentation
- `hacs.json` — HACS repository metadata

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

## Screenshots

### Full Season View (2024)

![Full Season 2024](images/Full%20Season%202024.png)

*Complete playoff bracket for the 2023-2024 NHL season showing all rounds and teams.*

### Integration Setup

![Integration API](images/Intergration%20api.png)

*Home Assistant integration configuration screen for setting up the NHL Playoffs integration.*

### Partial Season View (2026)

![Partial Season 2026](images/Partial%20Season%202026.png)

*Dashboard view showing current playoff progress for the 2025-2026 season.*

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
- **TBD Placeholder Image**: When teams aren't determined yet, the dashboard shows `/local/nhl/tbd.png`. You need to add this image file to your Home Assistant `config/www/nhl/tbd.png` folder.
- Add your NHL API and data-fetching logic inside `custom_components/nhl_playoffs/coordinator/` and `custom_components/nhl_playoffs/sensors/`.
- Keep `manifest.json` and `hacs.json` updated with any dependency or metadata changes.

## Future Improvements (TODO)

### Current Flaws
- **Static year display**: Cup logo and year labels are hardcoded to show "2026" regardless of selected season
- **Title responsiveness**: Dashboard title may not fit properly on screens smaller than 10 inches

### Planned Features
- **Interactive button cards**: Make playoff round cards clickable to show current/future game details, live scores, and series statistics
- **Dynamic logo updates**: Automatically change the Stanley Cup logo to match the selected season year (current or past)
- **YAML optimization**: Refactor dashboard configuration to use reusable templates and reduce file size
- **Mobile optimization**: Improve responsive design for tablets and phones
- **Enhanced sensor data**: Add game times, venues, player stats, and injury reports to sensor attributes
- **Error handling**: Better fallback displays when API data is unavailable or incomplete
- **Localization**: Add multi-language support for international users
- **Performance improvements**: Optimize data fetching and reduce dashboard load times
- **Series progress indicators**: Add visual progress bars showing wins needed for advancement
- **Game notifications**: Optional notifications for game starts, goals, and series conclusions

## License

This project is licensed under the **MIT License**. See the terms below:

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
