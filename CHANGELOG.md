# Changelog — Indeklima

All notable changes to this project are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [2.5.1] - 2026-05-17

### Changed
- **Mold risk now visible on all Lovelace cards** — previously only shown as a hidden chip when risk was elevated
- `indeklima-room-card`: mold chip always shown in footer with color coding (green = low, orange = moderate, red = high/critical)
- `indeklima-hub-card`: new dedicated "Skimmelrisiko" section showing global house average; per-room mold shown on every room row with icon + label
- `indeklima-tablet-card`: new "Skimmelrisiko" block in column 1 after air circulation; per-room mold always shown in room list

### Fixed
- Mold risk level "low" was invisible on room-card and hub-card room rows

---

## [2.5.0] - 2026-03-01

### Added
- **Mold risk sensor** (`CONF_MOLD_SENSORS`) — optional dedicated humidity sensor per room; falls back to room humidity sensor. Levels: `low` / `moderate` / `high` / `critical`. Threshold: RH ≥ 70% + temperature 5–35°C
- **Hub sensor `mold_risk_avg`** — global mold risk average across all rooms (19 hub sensors total)
- **Repair flow** (`repairs.py`) — actionable issues for `sensor_unavailable` and `coordinator_update_failed` raised automatically from coordinator
- **System health** — integration appears in Settings → System → System information
- **Diagnostics** — full diagnostics downloadable from Settings → Devices & Services
- **`entry.runtime_data`** — replaces `hass.data[DOMAIN]` for config entry data storage
- **Fast startup** — `SCAN_INTERVAL` reduced from 300s to 30s; first refresh no longer raises `ConfigEntryNotReady` if sensors are unavailable at boot

### Changed
- Quality Scale upgraded from Silver to **Gold Tier**
- Integration starts successfully even if sensors are unavailable at boot; data collected on next 30s cycle
- `__version__` defined exclusively in `const.py` — all other files import from there

### Fixed
- Panel scroll/viewport issue at 1440p+ (JS-driven height via ResizeObserver)
- Weather config display showing "ingen vejr konfig" incorrectly

---

## [2.4.1] - 2026-01-15

### Added
- Unit tests (109 passed, 67.81% coverage, CI green via GitHub Actions)

### Fixed
- `__version__` source of truth corrected to `const.py`
- Panel scroll bug on high-resolution screens
- Weather entity display in panel ventilation tab

---

## [2.4.0] - 2025-12-01

### Added
- Diagnostics platform — download from Settings → Devices & Services → Indeklima → ⋮
- System health integration
- Setup failure handling (`ConfigEntryNotReady` + `UpdateFailed`)
- Built-in sidebar panel (`indeklima-panel.js`) with WebSocket API
- `indeklima-cards.js` — Lovelace cards: `indeklima-hub-card`, `indeklima-tablet-card`, `indeklima-room-detail-card`

---

## [2.3.3] - 2025-10-01

### Added
- Pressure sensor support (`CONF_PRESSURE_SENSORS`) — informational only, does not affect severity scoring

---

## [2.3.2] - 2025-09-01

### Changed
- Documentation improvements

---

## [2.3.1] - 2025-08-01

### Changed
- Complete encoding cleanup — English constants only in Python code
- Danish translations exclusively in `translations/da.json`

---

## [2.3.0] - 2025-07-01

### Added
- Per-room metric sensors — separate HA entities per room for temperature, humidity, CO2, pressure

---

## [2.2.0] - 2025-06-01

### Added
- Air circulation system — Good/Moderate/Poor based on open internal doors
- Severity bonus: 5% reduction when air circulation is good

---

## [2.1.0] - 2025-05-01

### Added
- Ventilation recommendations (Yes/No/Optional) based on indoor climate + weather entity
- Automation blueprint for notification with cooldown

---

## [2.0.0] - 2025-04-01

### Added
- Device organisation — Hub device + per-room devices
- Modern entity naming (`sensor.indeklima_hub_*`, `sensor.indeklima_<room>_*`)
- 30-minute rolling trend analysis (Rising/Falling/Stable) using linear regression
- Multi-sensor averaging per room
