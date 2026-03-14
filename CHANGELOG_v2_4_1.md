# Changelog - Indeklima v2.4.1

## Version 2.4.1 - Diagnostics, System Health & Setup Failure Handling

**Release Date:** March 2026  
**Type:** MINOR — New Gold Tier features, backward compatible  
**Previous Version:** 2.4.0

---

## 🎯 Gold Tier Progress

This release adds three key features required for Gold Tier compliance on the Home Assistant Integration Quality Scale.

---

## 🆕 What's New

### 1. Integration Diagnostics (`diagnostics.py`)

Users can now download a full diagnostics report directly from the Home Assistant UI.

**How to access:**
- Settings → Devices & Services → Indeklima → ⋮ (three dots) → **Download diagnostics**
- Also available per device (hub + each room) from the device info page

**Config entry diagnostics includes:**
- Integration version
- All configured rooms and their sensor entity IDs
- Live sensor availability (which sensors are reachable right now)
- Current coordinator data (all room readings, averages, trends, ventilation)
- Configured threshold options

**Per-device diagnostics includes:**
- Hub device: global severity, status, all room summaries, ventilation/circulation
- Room device: individual sensor availability, current readings, severity score

✅ No sensitive data is exposed. `async_redact_data` is applied to all config data.

---

### 2. System Health (`system_health.py`)

Indeklima now shows up in the Home Assistant system health overview.

**How to access:**
- Settings → System → Repairs → ⋮ → **System information** → scroll to Indeklima

**Shows:**
| Field | Description |
|-------|-------------|
| Integration version | Current version (e.g. 2.4.1) |
| Config entries loaded | Number of active config entries |
| Coordinator status | `ok` or `update_failed` |
| Rooms monitored | Total rooms configured |
| Overall status | `good` / `warning` / `critical` |
| Severity score | e.g. `24.3 / 100` |
| Sensors configured | Total sensor entities across all rooms |
| Sensors unavailable | How many sensors are currently offline |
| Rooms in critical state | Count of critical rooms |
| Rooms in warning state | Count of warning rooms |
| Ventilation recommendation | `yes` / `no` / `optional` |
| Air circulation | `good` / `moderate` / `poor` |
| Weather entity configured | `yes` / `no` |

---

### 3. Setup Failure Handling (`__init__.py`)

Two improvements to how the integration handles errors:

#### `ConfigEntryNotReady` — Setup retry
If `async_config_entry_first_refresh()` fails during integration setup (e.g. HA is starting up and sensors aren't ready yet), the integration now raises `ConfigEntryNotReady` with a clear error message.

**Before (v2.4.0):** Unhandled exception → integration fails permanently until manual reload  
**After (v2.4.1):** `ConfigEntryNotReady` → HA automatically retries setup every 30s, no restart needed

#### `UpdateFailed` — Coordinator error handling
The `_async_update_data()` method now wraps its logic in a try/except that raises `UpdateFailed` on unexpected errors.

**Before:** Unhandled Python exceptions silently crashed the update cycle  
**After:** `UpdateFailed` → HA marks entities as unavailable and shows the error in the integration page

---

## 📁 New Files

```
custom_components/indeklima/
├── diagnostics.py          # Config entry + device diagnostics
└── system_health.py        # System health info
```

---

## 🔄 Changed Files

| File | Change |
|------|--------|
| `__init__.py` | + `ConfigEntryNotReady` on setup, + `UpdateFailed` in coordinator |
| `strings.json` | + `system_health` translation section |
| `da.json` | + `system_health` translation section (Danish) |
| `const.py` | Version → 2.4.1 |
| `manifest.json` | Version → 2.4.1 |

---

## ✅ Backward Compatibility

No breaking changes. All existing sensors, dashboard cards, and blueprints work exactly as before.

---

## 🎯 Quality Tier

Still **Silver Tier** officially — Gold Tier requires unit tests (>95% coverage) in addition to diagnostics, system health, and proper error handling. Tests are planned for v2.5.0.

---

## 🐛 Bug Fixes

- Integration no longer requires manual reload if sensors are temporarily unavailable at HA startup
- Coordinator update errors are now properly surfaced in the HA UI instead of being silently swallowed
