# Changelog

All notable changes to Indeklima are documented in this file.

The format is inspired by [Keep a Changelog](https://keepachangelog.com/).
Detailed per-version notes are available in `CHANGELOG_v{major}_{minor}_{patch}.md`.

---

## [2.9.3] — 2026-07-11

### Fixed
- Real production bug in `sensor.py`: 6 sensor properties used
  `if not self.coordinator.data:` as a "no data yet" guard, which also
  (incorrectly) matched a valid-but-empty `{}` data dict, skipping the
  sensors' own default-value fallbacks. Changed to `is None` checks.
- Fixed a pre-existing test bug in `test_coordinator.py` (`dt_util.now()`
  mock missing `month=`, causing a `TypeError` in `_get_season()`).
- Fixed stale hardcoded version-string assertions in `test_const.py` and
  `test_diagnostics.py` left over from v2.9.2's version bump; the
  diagnostics one now compares against `const.__version__` so it won't go
  stale again.
- Fixed a bug in the new `TestWebsocketCoversRealCoordinatorFields` test
  helper (introduced in v2.9.2) that was missing `mold_risk_temp_min`/`max`
  on the manually-constructed coordinator instance.

See [`CHANGELOG_v2_9_3.md`](CHANGELOG_v2_9_3.md) for full technical detail.

---

## [2.9.2] — 2026-07-11

### Added
- `tests/test_config_flow.py` (new) — direct test coverage for the config flow
  and options flow, previously excluded from coverage and only manually
  verified. Focus on the per-room override fields added in v2.8.0
  (`CONF_ROOM_LED_CRITICAL_SEVERITY`, quiet-hours override) and the full room
  add/edit/delete round trip.
- `tests/test_websocket.py` — two new test classes: direct regression tests
  for the `dehumidifier_mode`/`kritisk_siden`/`led_alarm_active` fields that
  were missing before v2.9.0, plus a future-proofing test that diffs the real
  coordinator's `_process_room()` output against both websocket payloads, so
  a newly added field that isn't forwarded fails CI automatically.

### Changed (UI)
- Softened the LED-alarm mirroring in the panel and Lovelace cards from a
  hard 1.2s blink to a calmer 2.4s fade.
- Added a subtle pulsing glow to the "critical since" badge in the panel and
  both cards.

See [`CHANGELOG_v2_9_2.md`](CHANGELOG_v2_9_2.md) for full technical detail.

---

## [2.9.1] — 2026-07-10

### Fixed
- **Weather data missing whenever a window was open.** `_calculate_ventilation_recommendation()` only fetched weather data (`outdoor_temp`/`outdoor_humidity`) *after* checking for open windows. If any window anywhere in the house was open, the function returned early via the `open_windows` branch — before weather data was ever fetched. As a result, the panel showed "Weather data not available yet" even though the configured weather entity (`weather.hjem`, Met.no) had fully valid `temperature`/`humidity` attributes. Fixed by moving the weather fetch to the top of the function, before any early returns.

### Tests
- New `TestCalculateVentilationRecommendation` class in `tests/test_coordinator.py` with 3 regression tests (open windows + valid weather, no issues + valid weather, weather unavailable).

See [`CHANGELOG_v2_9_1.md`](CHANGELOG_v2_9_1.md) for full technical detail.

---

## [2.9.0] — 2026-07-04

### Fixed (critical prerequisite)
- `websocket.py` was missing `dehumidifier_mode` and `kritisk_siden` (critical-since) in both WebSocket payloads (`ws_get_climate_data` and `ws_get_room_data`) — invisible to the panel and cards even though the coordinator calculated them correctly.
- `led_alarm_active` only existed internally on the coordinator's `_dehumidifier_state`, not in `room_data` itself, so it couldn't be exposed to the frontend at all. Added to `room_data` in `_process_room()` and forwarded to both WebSocket payloads.

### Added (UI — panel + all 4 Lovelace cards)
- **Dehumidifier mode** — now shows "Manual"/"Automatic"/"Off" next to the dehumidifier recommendation everywhere it's displayed (compact room card, room detail view, house overview)
- **"Critical since HH:MM"** — shown as a red warning line when a room's status is critical, based on the new critical-since timestamp
- **LED alarm mirroring** — a red 🔴 indicator now shows in the UI when a room's LED alarm is active, so it's visible without physically being in the room. Shown as an icon next to the room name (compact view), a pulsing banner (detail view), and a badge in the footer chips (room card)

### Deliberately out of scope
- The hub card and tablet card (house overview) were **not** updated with the new per-room details (mode/critical-since/LED alarm) — it would make the compact overview views too cluttered.

See [`CHANGELOG_v2_9_0.md`](CHANGELOG_v2_9_0.md) for full technical detail.

---

## [2.8.0] — 2026-07-04

### Added
Builds on v2.7.0's red LED alarm for critical indoor climate.

- **Blinking alarm instead of solid red.** The LED blinks red/off every 3 seconds while a room is in critical alarm, implemented as a self-rescheduling timer chain that stops cleanly as soon as the alarm clears.
- **Recovery hysteresis.** The alarm stays active until the room has been non-critical for 2 consecutive update cycles (~60 seconds at the 30s scan interval), so the LED doesn't flicker back and forth around the threshold.
- **"Critical since" timestamp.** A new `kritisk_siden` (critical-since) attribute on each room's status sensor, set immediately (no hysteresis) when the room's actual severity status becomes critical, and cleared immediately when it no longer is. Works for every room regardless of whether an LED or dehumidifier is configured.
- **Configurable per-room alarm threshold.** New optional "LED red-alarm threshold" field in room setup (both create and edit), 1–100. Falls back to the global critical threshold (60) if not set. This threshold only controls the LED alarm — it does not change the room's official status classification.

### Deliberately not built
- Mobile notification on alarm — would require its own cooldown logic and a per-room notification target; can be added separately if wanted.

See [`CHANGELOG_v2_8_0.md`](CHANGELOG_v2_8_0.md) for full technical detail.

---

## [2.7.0] — 2026-07-04

### Added
- **Dehumidifier LED: red alarm on critical indoor climate.** The LED switches to red as soon as a room's overall severity status becomes critical — regardless of whether the dehumidifier is currently running manually (blue), automatically (yellow), or is off. Red takes top priority and always overrides the mode color.
  - The threshold is the room's severity status (broader than mold risk alone — also includes CO₂, VOC and formaldehyde), not just humidity/mold.
  - The color is recalculated on every update cycle (every 30 seconds), not just on dehumidifier start/stop, so the LED reacts immediately both when conditions worsen and when they improve again.
  - The dehumidifier's own control mode (manual/auto/off) is unaffected by the alarm — it's purely a visual LED overlay.

### Deliberately not built
- The auto-dehumidifier does not stop early when the recommendation switches to "no" — the full 45-minute timer is preserved to avoid short-cycling the physical dehumidifier.

See [`CHANGELOG_v2_7_0.md`](CHANGELOG_v2_7_0.md) for full technical detail.

---

## [2.6.1] — 2026-07-04

### Fixed
- **Bug:** the `mold_risk` sensor's "sensors used" attribute was never populated, even when a room had a dedicated mold/humidity sensor configured. Cause: `IndeklimaRoomMetricSensor.extra_state_attributes` looked up the key `mold_risk_sensors_count`, while the coordinator actually stores the count under `mold_sensors_count`. `sensor.py` now uses the correct key for the `mold_risk` metric.

### Tests
- Added full test coverage for the integration's setup/teardown lifecycle (`async_setup_entry`, `async_unload_entry`, `async_reload_entry` in `tests/test_init.py`), including the critical v2.5.0 behavior where a failing first refresh must not block setup.
- Added tests for the `mold_sensors_count` attribute in `tests/test_coordinator.py`.
- New `tests/test_sensor.py` file with basic coverage of the `mold_risk` and `dehumidifier_recommendation` sensor entities (previously untested).

### No functional changes
This release contains no functional changes — only an attribute bugfix and expanded test coverage.

See [`CHANGELOG_v2_6_1.md`](CHANGELOG_v2_6_1.md) for full technical detail.

---

## [2.6.0] — 2026-07-03

### Added
- **Built-in dehumidifier automation** — replaces an external HA automation:
  - Button control: Indeklima itself listens for an optional button entity per room and toggles the dehumidifier
  - Automatic on/off based on the dehumidifier recommendation (humidity + mold risk)
  - LED feedback (optional `light` entity per room): blue = manual, yellow = automatic, off = off
  - Per-room auto-off timer (configurable duration, default 45 min)
  - Configurable quiet hours — global time window (OptionsFlow) + optional per-room override
- The `dehumidifier_recommendation` sensor now has a `mode` attribute (manual/auto/off)

### Fixed
- **Critical**: `CONF_WINDOW_ENTITY` didn't match the actual stored configuration key (`"entity"` vs. `"entity_id"`). This caused room editing to crash, and meant window/door detection had in practice never worked. Fixed without requiring a data migration.
- `_get_room_schema()` made defensive against data/code mismatches (`.get()` instead of direct dict indexing)
- `sensor.py`: added a missing `None` guard for `coordinator.data` in the hub sensors' `extra_state_attributes`, which caused an `AttributeError` on startup
- `strings.json`: fixed existing JSON corruption (a misplaced `issues` block) that would have failed `hassfest` validation in CI

### Tests
- ~20 new/updated tests for dehumidifier control, quiet hours and button listeners
- All 9 existing tests in `TestCalculateDehumidifierRecommendation` updated for the new function signature

See [`CHANGELOG_v2_6_0.md`](CHANGELOG_v2_6_0.md) for full technical detail.

---

## Earlier versions

See the individual `CHANGELOG_v{version}.md` files (and the `UPGRADE_HISTORY/` folder) in the repo root for details on versions before 2.6.0 (2.0.0 → 2.5.14).
