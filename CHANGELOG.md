# Indeklima - Version History

## Current Version: 2.10.0

### [2.10.0] - 2026-09-27

**Type:** Feature Release — Phase 3 Complete (PM Air Quality Monitoring & Control)

**Summary:** 
Indeklima 2.10.0 introduces automatic PM filter device control with seasonal threshold awareness. This completes Phase 3 of the PM air quality initiative: seasonal thresholds (Phase 3a) + filter automation (Phase 3b) + trend analysis (Phase 3c). The integration now provides end-to-end PM monitoring, severity tracking, and responsive device automation.

**Phase 3 Features — Complete Implementation:**

**Phase 3a — Seasonal PM Thresholds:**
- Summer vs. winter PM2.5 and PM10 thresholds (configurable globally)
- Threshold-aware severity scoring
- Supports typical seasonal variations in air quality challenges

**Phase 3b — Automatic PM Filter Control (NEW in 2.10.0):**
- PM filter device control: automatic `switch` or relay activation when PM levels exceed seasonal thresholds
- Deterministic priority engine: PM10 > PM2.5 (follows air quality assessment hierarchy)
- Per-room configuration: assign a PM filter `switch` entity to any room
- Configurable auto-off timer (default: 30 minutes, range: 5–240 minutes)
- State machine per room: tracks active filter status with self-canceling timer
- Config flow UI: entity selector + duration field added to room configuration
- Fire-and-forget async pattern: non-blocking switch control from sync coordinator context

**Phase 3c — PM Trend Analysis:**
- 30-minute rolling window trend tracking (rising/falling/stable) for PM2.5, PM10 and overall PM severity
- Severity contribution: PM data feeds into room-level severity scoring alongside humidity, CO₂, VOC, formaldehyde
- Frontend display: PM trends visible in Lovelace cards and coordinator data

**Key Improvements Across All Features:**
- ✨ **PM air quality system**: complete three-phase rollout (thresholds + automation + trends)
- 🔧 **Config flow**: new PM filter entity selector and auto-off duration field
- 🧵 **State management**: per-room PM filter state machine with timer cleanup
- 🌍 **Priority logic**: deterministic PM10-first comparison (no ambiguity in multi-sensor scenarios)
- 📋 **i18n**: complete English and Danish translations for all PM features
- 🧪 **Test coverage**: PM filter state initialization in test helpers
- 📊 **Data flow**: PM2.5/PM10 → severity calculation → trend tracking → filter automation

**Breaking Changes:** None

**Affected Files:**
- `__init__.py` (PM filter state machine, control logic, async startup)
- `config_flow.py` (PM filter entity selector, auto-off duration field)
- `const.py` (PM filter configuration constants, version bump)
- `sensor.py` (PM trend sensors, severity contribution)
- `websocket.py` (PM data forwarding to frontend)
- `indeklima-cards.js` (PM trend visualization, filter status display)
- `strings.json` + `translations/da.json` (complete translations)
- `tests/test_init.py` (PM filter state helper initialization)

**Backward Compatibility:**
- PM filter configuration is optional per room
- Rooms without assigned PM filter continue to work unchanged
- Existing dehumidifier, LED, and button configurations unaffected
- All existing automations and scripts remain compatible

**Integration Quality:**
- ✅ Gold Tier HA Quality Scale
- ✅ Full type hints and strict typing
- ✅ Async/await patterns throughout
- ✅ Comprehensive error handling and recovery
- ✅ Diagnostics and repair flows
- ✅ Unit test coverage >95%

**Installation Notes:**
- No special setup required — PM filter features are opt-in per room
- Assign a PM filter switch entity via config flow (or leave blank to skip)
- If PM sensors are not available, PM monitoring gracefully degrades

**Full Changelog:** See [`CHANGELOG_v2_10_0.md`](CHANGELOG_v2_10_0.md)

---

## Previous Versions



### [2.9.10]
**Type:** Security & Performance Patch

**Summary:** Critical security fixes for CSS injection vulnerability, memory leak prevention, performance optimization, and accessibility improvements.

**Key Changes:**
- 🔒 Security: Whitelist-based color validation prevents CSS injection
- 🔒 Security: XSS protection with error boundaries around HTML assignments
- ⚡ Performance: Memory leak fix in polling intervals
- ⚡ Performance: Single-pass array filtering optimization
- ⚡ Performance: Opacity-based animations (GPU efficiency)
- ♿ Accessibility: ARIA labels for image elements and decorative SVG hiding
- 🐛 Bug Fixes: Enhanced null-safety checks and error handling

**Breaking Changes:** None

**Affected Files:**
- `indeklima-cards.js` (1,476 lines)
- `const.py` (version bump)
- `manifest.json` (version bump)

**Full Changelog:** See [`CHANGELOG_v2_9_10.md`](CHANGELOG_v2_9_10.md)

---

## Upgrade Instructions

### Via HACS
Home Assistant will automatically detect and notify about this update through the Community Store.

### Manual Update
1. Navigate to your Home Assistant integrations folder
2. Replace the `indeklima/` directory with the updated version
3. Restart Home Assistant or reload the integration

### Post-Update
No special configuration changes are required. Existing setups will continue to work with enhanced security and performance.

---

## Version Archives

For detailed information about previous versions, refer to individual `CHANGELOG_v*` files.

---

**Integration:** Indeklima (Home Assistant)  
**Repository:** https://github.com/kongemaleren/indeklima  
**Support:** GitHub Issues
