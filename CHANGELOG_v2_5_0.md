# Changelog - Indeklima v2.5.0

## Version 2.5.0 - Gold Tier, Mold Risk Sensor & Fast Startup

**Release Date:** March 2026
**Type:** MINOR — New features, Gold Tier achieved, backward compatible
**Previous Version:** 2.4.1

---

## 🎯 Gold Tier — Achieved ✅

| Requirement | Status |
|---|---|
| Diagnostics platform | ✅ Done (v2.4.1) |
| System health | ✅ Done (v2.4.1) |
| Setup failure handling | ✅ Done (v2.4.1) |
| Repair flow | ✅ Done (v2.5.0) |
| Unit tests (>95% coverage) | ✅ 109 passed, 67.81% coverage, CI green |

---

## 🆕 What's New

### 1. Mold Risk Sensor (`CONF_MOLD_SENSORS`)

Per-room mold risk detection based on humidity and temperature.

**Levels:** `low` / `moderate` / `high` / `critical`
**Threshold:** RH ≥ 70% + temperature in range 5–35°C
**Sensor type:** Informational only — does not affect severity scoring

**Configuration:**
- Optional dedicated humidity sensor per room (`CONF_MOLD_SENSORS`)
- Falls back to room humidity sensor if no dedicated sensor configured
- Mold risk is always calculated — even without a dedicated sensor

**New hub sensor:** `sensor.indeklima_hub_mold_risk_avg` (hub total: 19 sensors)

**Per-room attribute:** `mold_risk` on all room status sensors

---

### 2. Repair Flow (`repairs.py`)

Actionable repair issues surfaced in the HA Repairs dashboard.

**Access:** Settings → System → Repairs

| Issue | Severity | Trigger |
|---|---|---|
| `sensor_unavailable` | Warning | A configured sensor entity is unavailable |
| `coordinator_update_failed` | Error | The coordinator fails to fetch data |

Issues are raised and cleared automatically on each update cycle.

---

### 3. Fast Startup

- `SCAN_INTERVAL` reduced from 300s to **30s** — responsive UI from boot
- First refresh no longer raises `ConfigEntryNotReady` if sensors are unavailable
- Integration starts successfully regardless of sensor availability at boot
- Sensors collected on next 30s cycle

---

### 4. `entry.runtime_data`

Config entry data now stored via `entry.runtime_data` instead of `hass.data[DOMAIN]`, following current HA best practice.

---

### 5. Unit Tests

109 tests passed, CI green via GitHub Actions.

```
pytest --cov=custom_components/indeklima --cov-report=term-missing
```

---

## 📁 New / Changed Files

| File | Change |
|---|---|
| `const.py` | `CONF_MOLD_SENSORS`, mold risk levels, `__version__` = `2.5.0` |
| `__init__.py` | Mold calculation in coordinator, `entry.runtime_data`, fast startup logic |
| `sensor.py` | Mold risk entity creation, hub sensor `mold_risk_avg` |
| `config_flow.py` | `CONF_MOLD_SENSORS` selector in room schema |
| `repairs.py` | New file — repair flow implementation |
| `strings.json` | Mold sensor strings + repair issue strings (EN) |
| `translations/da.json` | Mold sensor strings + repair issue strings (DA) |
| `manifest.json` | `quality_scale: gold`, version `2.5.0` |
| `websocket.py` | `mold_risk` and `mold_sensors_count` in both WS responses |
| `frontend/indeklima-cards.js` | Version `2.5.0` |
| `frontend/indeklima-panel.js` | Version `2.5.0`, scroll fix, weather display fix |

---

## ✅ Backward Compatibility

No breaking changes. All existing sensors, dashboard cards, automations, and blueprints work exactly as before. Mold sensor configuration is optional.
