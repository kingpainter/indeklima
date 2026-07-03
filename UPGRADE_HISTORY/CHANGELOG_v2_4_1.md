# Changelog - Indeklima v2.4.1

## Version 2.4.1 - Diagnostics, System Health, Repair Flow & Fixes

**Release Date:** May 2026
**Type:** MINOR — New Gold Tier features, bug fixes, backward compatible
**Previous Version:** 2.4.0

---

## 🎯 Gold Tier Progress

This release completes all remaining Gold Tier requirements except verified test coverage:

| Requirement | Status |
|---|---|
| Diagnostics platform | ✅ Done (v2.4.1) |
| System health | ✅ Done (v2.4.1) |
| Setup failure handling | ✅ Done (v2.4.1) |
| Repair flow | ✅ Done (v2.4.1) |
| Unit tests (>95%) | 🔄 Tests written, coverage to be verified |

---

## 🆕 What's New

### 1. Integration Diagnostics (`diagnostics.py`)

Users can download a full diagnostics report directly from the HA UI.

**Access:** Settings → Devices & Services → Indeklima → ⋮ → Download diagnostics

**Config entry diagnostics includes:**
- Integration version
- All configured rooms and their sensor entity IDs
- Live sensor availability (which sensors are reachable right now)
- Current coordinator data (all room readings, averages, trends, ventilation)
- Configured threshold options

**Per-device diagnostics includes:**
- Hub device: global severity, status, all room summaries, ventilation/circulation
- Room device: individual sensor availability, current readings, severity score

---

### 2. System Health (`system_health.py`)

Indeklima now appears in the HA system health overview.

**Access:** Settings → System → Repairs → ⋮ → System information → Indeklima

---

### 3. Repair Flow (`repairs.py`)

Actionable repair issues are now surfaced in the HA Repairs dashboard.

**Access:** Settings → System → Repairs

**Two issue types:**

| Issue | Severity | Trigger |
|---|---|---|
| `sensor_unavailable` | Warning | A configured sensor entity is unavailable |
| `coordinator_update_failed` | Error | The coordinator fails to fetch data |

- Issues are raised automatically during each update cycle
- Issues are cleared automatically when the problem resolves
- Both issues present a confirm-and-dismiss repair flow

---

### 4. Setup Failure Handling (`__init__.py`)

- `ConfigEntryNotReady` raised on first refresh failure → HA retries automatically every 30s
- `UpdateFailed` raised on coordinator errors → entities marked unavailable, error shown in UI
- Coordinator-failed repair issue raised/cleared automatically on each update

---

### 5. Unit Tests (`tests/`)

Full test suite added:

| File | Coverage |
|---|---|
| `test_const.py` | version, constants, `normalize_room_id` |
| `test_init.py` | season, severity, status, trends, circulation, sensor values |
| `test_repairs.py` | issue raising/clearing, fix flow factory |
| `test_websocket.py` | WS handlers, room sorting, error paths |
| `test_diagnostics.py` | config entry + device diagnostics |

Run with:
```
pytest --cov=custom_components/indeklima --cov-report=term-missing
```

---

### 6. Bug Fixes

| Bug | Fix |
|---|---|
| Panel showed `v2.3.4` despite manifest saying `2.4.1` | `__version__` was defined in `const.py` at `2.3.4` — now correctly `2.4.1`. `const.py` is the single source of truth. |
| Panel showed "ingen vejr konfig" despite weather entity being configured | Panel now uses `weather_configured` field from WS response to distinguish "not configured" from "configured but no outdoor issues" |
| Shadow DOM scroll/viewport broken on 1440p+ screens | JS-driven height via `ResizeObserver` + `getBoundingClientRect()` replaces CSS-only approach |
| `_CACHE_KEY` used in `_load()` but never defined | Now defined in `constructor` |
| All sensors showed `—` after restart | Timing issue — coordinator not finished with first update when panel loaded. No code change needed; documented as known startup behavior. |

---

## 📁 New Files

```
custom_components/indeklima/
└── repairs.py              # Repair flow for sensor + coordinator issues

tests/
├── __init__.py
├── conftest.py             # Shared fixtures
├── test_const.py
├── test_init.py
├── test_repairs.py
├── test_websocket.py
└── test_diagnostics.py

pytest.ini
requirements_test.txt
```

---

## 🔄 Changed Files

| File | Change |
|---|---|
| `const.py` | `__version__` bumped to `2.4.1` (single source of truth) |
| `__init__.py` | Repair flow integrated; `_get_sensor_values` raises/clears issues per entity; version docstring fixed |
| `manifest.json` | `quality_scale: silver` added |
| `strings.json` | `issues` section added (EN) |
| `translations/da.json` | `issues` section added (DA) |
| `frontend/indeklima-panel.js` | Scroll fix, `_CACHE_KEY`, weather display fix, version bump |
| `websocket.py` | Version header updated |
| `sensor.py` | Version docstring updated |
| `config_flow.py` | Version docstring updated |
| `panel.py` | Version header updated |

---

## ✅ Backward Compatibility

No breaking changes. All existing sensors, dashboard cards, automations, and blueprints work exactly as before.
