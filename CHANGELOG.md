# 📘 NHL Playoffs Dashboard — Changelog

All notable changes to this project will be documented in this file.  
This project follows a simplified semantic versioning style.


### ❗ REQUIRED ACTIONS BEFORE UPDATING  
To avoid **conflicting sensor names**, **duplicate entities**, or **broken dashboards**, you MUST do the following before installing this update:

#### 1. **Delete the existing NHL Playoffs integration**
Home Assistant → Settings → Devices & Services → NHL Playoffs → Delete

This removes all old sensors that use the outdated naming scheme.

#### 2. **Delete your existing `nhl_playoffs_dashboard.yaml`**
The dashboard has been **fully rebuilt**, **simplified**, and **optimized**.

The new version:
- Uses fewer cards  
- Loads faster  
- Has cleaner logic  
- Includes the new live overlay  
- No longer requires layout-card  

---

## 🟩 **v2.3.0 — Live Game Overlay + Integration Cleanup Update**
**Release Date:** 2026‑05‑15

### 🚨 New Features
- Added **real‑time live game overlay** to all series cards.
- Added **Power Play indicator (PP triangle)**.
- Added **Empty Net indicator (EN)**.
- Added **live score display** (home & away).
- Added **period tracking** (1st, 2nd, 3rd, OT, 2OT, etc.).
- Added **time remaining** in the current period.
- Added **intermission detection** with `INT` display.
- Added **game state** support (Preview, Live, Final).

---

### 🧩 Sensor Naming Changes (IMPORTANT)
The integration now uses a **new, standardized sensor naming format**:

#### Old Format (removed)
```
sensor.playoffs_r1_west_1
sensor.playoffs_r1_east_1
...
```

#### New Format (current)
```
sensor.nhl_series_r1_west_1
sensor.nhl_series_r1_east_1
sensor.nhl_live_r1_west_1
sensor.nhl_live_r1_east_1
...
```

This change was required to support:
- Cleaner naming
- Better round mapping
- Live game sensor pairing
- Future multi‑season support

---


#### 3. **Reinstall the integration**
After deleting the old version, install the new one cleanly.

#### 4. **Follow the updated README instructions**
The README now includes:
- New dashboard layout  
- New sensor names  
- New banner + conference bars  
- New live game overlay setup  

---

### 🛠 Integration Enhancements
- Updated `live_coordinator.py` to process real‑time NHL API data.
- Updated `series_coordinator.py` for improved bracket mapping.
- Expanded `mapping_bracket.py` to support new rounds and series logic.
- Added new live sensor attributes:
  - `live_period`
  - `live_time_remaining`
  - `live_intermission`
  - `live_pp_team`
  - `live_empty_net_team`
  - `home_score`
  - `away_score`
  - `game_state`

---

### 🎨 Dashboard Improvements
- ~~Added **season‑aware banner** using:  (REMOVED)~~
  ```
  https://assets.nhle.com/logos/playoffs/png/scp-{YYYYYYYY}-horizontal-banner-en.png
  ```
- Added **Western Conference** and **Eastern Conference** title bars.
- Improved spacing, alignment, and readability.
- Updated button‑card templates for live overlays.
- Removed dependency on **layout-card** (no longer required).
- Added two new screenshots demonstrating:
  - Live PP triangle
  - Live EN + score + period + time remaining

---

## 🟦 **v2.2.0 — Season Banner & Layout Update**
**Release Date:** 2026‑05‑10

### New Features
- Added dynamic season banner support. 
- Added new bracket header layout.
- Improved grid structure for 5‑column bracket.
- Added support for future season switching.

### Dashboard Enhancements
- Updated styling for series cards.
- Improved mobile responsiveness.
- Added new color themes for conference separation.

---

## 🟥 **v2.1.0 — Integration Rewrite**
**Release Date:** 2026‑05‑05

### Major Changes
- Rewrote integration to use new sensor naming format:
  - `sensor.nhl_series_rX_*`
  - `sensor.nhl_live_rX_*`
- Improved coordinator performance.
- Added season selection during integration setup.
- Added automatic sensor creation based on bracket structure.

---

## 🟨 **v1.0.0 — Initial Release**
**Release Date:** 2026‑05‑01

### Features
- Full NHL Playoffs bracket generation.
- Round 1 → Stanley Cup Final support.
- Team logos, seeds, wins, and series metadata.
- Static bracket layout using button‑card.
- Initial screenshot set.

---

# 📌 Notes
For detailed feature descriptions and installation instructions, see the main README:

👉 https://github.com/astlgit/nhl_playoffs_ha_dashboard/blob/main/README.md

