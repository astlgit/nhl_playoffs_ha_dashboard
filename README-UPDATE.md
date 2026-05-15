# 🏒 NHL Playoffs Dashboard — Update Notes  
A summary of the newest enhancements added to the NHL Playoffs Home Assistant Dashboard.  
For full installation instructions and complete feature documentation, see the main README:

👉 https://github.com/astlgit/nhl_playoffs_ha_dashboard/blob/main/README.md

---

## 🚨 Live Game Overlay System (New!)  
The dashboard now includes a fully dynamic **live game status bar** inside each series card.  
This brings real‑time, broadcast‑style information directly into the bracket.

### 🔥 Live Game Enhancements  
- **Power Play Indicator (PP Triangle)**  
  Displays automatically when a team is on the power play.

- **Empty Net Indicator (EN)**  
  Appears when a team pulls their goalie.

- **Live Score Display**  
  Home and away scores update in real time.

- **Period Tracking**  
  Shows 1st, 2nd, 3rd, OT, 2OT, etc.

- **Time Remaining**  
  Displays the time left in the current period.  
  Shows **INT** during intermission.

- **Compact, Broadcast‑Style Layout**  
  Fits cleanly inside each series card without breaking the bracket.

---

## 🖼️ New Screenshots  
Two new images have been added to the repository to showcase the live game overlay:

1. **Live Game — Power Play Active (PP Triangle)**  
2. **Live Game — Empty Net + Score + Period + Time Remaining**

These demonstrate the new real‑time interface in action.

---

## 🟦 Conference Title Bars (New!)  
The dashboard now includes bold, themed conference headers:

### Western Conference  
- Deep navy gradient  
- Blue accent border  
- Strong uppercase typography  

### Eastern Conference  
- Deep red gradient  
- Red accent border  
- Matching typography  

These headers visually separate the two sides of the bracket and align with NHL branding.

---

## 🧩 Integration Enhancements  
Several backend improvements were made to support the new live overlay system:

### New Live Sensor Attributes  
- `live_period`  
- `live_time_remaining`  
- `live_intermission`  
- `live_pp_team`  
- `live_empty_net_team`  
- `home_score`  
- `away_score`  
- `game_state`  

### Coordinator Updates  
- `live_coordinator.py` now processes real‑time NHL API data.  
- `series_coordinator.py` updated for improved bracket mapping.  

### Mapping Updates  
`mapping_bracket.py` now includes updated round and series logic for all playoff rounds.

---

## 🎨 Dashboard Layout Improvements  
The dashboard now includes:

- Western & Eastern conference title bars  
- Updated series cards  
- Live game overlays  
- Cleaner spacing  
- Improved readability  

These changes make the dashboard feel more like a real NHL broadcast.

---

## 📌 Next Planned Updates  
- Dynamic Finals banner  
- Conference shield logos  
- Optional compact layout  
- Game Center modal  
- Multi‑season selector  
- Automatic dark/light mode  

---

## 🙌 Thank You  
These updates bring the dashboard closer to a true NHL broadcast experience.  
Thank you for using and supporting the NHL Playoffs Dashboard!

