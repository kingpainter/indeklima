# Changelog v2.9.2

**Date:** 2026-07-11

## Added — test coverage for two known gaps + UI polish

This is a mixed stability + UI session, per the project's "on the horizon" list
(`instructions_for_claude_indeklima.md` §11/§14).

### Stability

- **`tests/test_config_flow.py` (new).** The config flow and options flow were
  previously excluded from coverage (`.coveragerc`) and only manually verified.
  This adds direct tests for both `IndeklimaConfigFlow` and
  `IndeklimaOptionsFlow`, instantiating the flow handlers directly and calling
  `async_step_*` methods (mocking `hass.async_set_unique_id`,
  `_abort_if_unique_id_configured`, and `entity_registry.async_get` where the
  real flow would need a live `hass`). Focus areas:
  - `CONF_ROOM_LED_CRITICAL_SEVERITY` (per-room LED alarm threshold override,
    added in v2.8.0) — stored when provided, omitted when not, and present in
    both the create-room and edit-room schemas.
  - `CONF_ROOM_QUIET_HOURS_START`/`END` per-room override, including a
    regression guard confirming `0` (midnight) is stored and not treated as
    "missing" (the code correctly uses `if val is not None`, not `if val:` —
    this test protects that from regressing).
  - `CONF_DEHUMIDIFIER_ON_DURATION`.
  - Full room add/edit/delete round trip in the `OptionsFlow`, including the
    window-sensor outdoor/indoor classification sub-step.

- **`tests/test_websocket.py` — two new test classes.**
  - `TestHistoricalBugFieldsAreForwarded`: direct regression tests confirming
    `dehumidifier_mode`, `kritisk_siden` and `led_alarm_active` — the three
    fields that were silently missing from both websocket payloads before
    v2.9.0 — are forwarded correctly by both `ws_get_climate_data` and
    `ws_get_room_data`.
  - `TestWebsocketCoversRealCoordinatorFields`: a future-proofing guard that
    calls the *real* `IndeklimaDataCoordinator._process_room()` (not a
    hand-written fixture) and diffs its actual output keys against what both
    websocket handlers expose. A hand-maintained test fixture can drift out of
    sync with the coordinator just as easily as `websocket.py` itself did —
    this test means a newly added coordinator field that isn't forwarded to
    the frontend will fail CI immediately, without anyone needing to remember
    to update a fixture by hand. `_process_room()` had no direct test at all
    before this.

### UI polish

While reviewing the panel/cards for the planned severity-ring animation and
colored trend arrows, both turned out to already be implemented (`.score-ring-fill`
already transitions `stroke-dashoffset`/`stroke` smoothly, and `_trendColor()`
already colors rising/falling arrows red/green) — no changes needed there.

- **Softer LED-alarm mirroring.** The UI's red 🔴 alarm indicators (room-card
  name icon, room-detail banner, `indeklima-cards.js` alarm chip and banner)
  previously used a hard/fast blink (`blink 1.2s`, opacity 1→0.55). Replaced
  with a calmer, slower fade (`led-alarm-fade` / `led-fade`, 2.4s,
  opacity 1→0.45) — the physical LED itself still blinks; this is a gentler
  UI echo of that state, in keeping with the project's calm, professional
  aesthetic rather than an aggressive alert flash.
- **"Critical since" glow.** The `kritisk_siden` badge (panel + both cards)
  now has a subtle pulsing red glow (`box-shadow`, using the same red used
  elsewhere for critical status) instead of static text, using the existing
  `--teal-glow`-style token pattern from the shared designer reference,
  applied here with red instead of the accent color since this is a critical
  indicator, not a branding element.

## Files changed

- `tests/test_config_flow.py` (new)
- `tests/test_websocket.py`
- `custom_components/indeklima/frontend/indeklima-panel.js`
- `custom_components/indeklima/frontend/indeklima-cards.js`
- `const.py` / `manifest.json`: version 2.9.1 → 2.9.2

## Known limitation

The new `test_config_flow.py` instantiates flow handlers directly rather than
going through the real `hass.config_entries.flow` manager, consistent with
the fully-mocked style already used throughout this test suite (see
`tests/test_init.py`'s `_make_coord()` pattern). This is lower-fidelity than a
full integration test against a real `hass` fixture, but avoids introducing
`pytest-homeassistant-custom-component`'s heavier `hass` fixture machinery
into a suite that has deliberately avoided it so far. Recommend running
`pytest tests/test_config_flow.py -v` after pulling this to confirm the exact
`FlowResult` dict keys match your installed Home Assistant version (`type`,
`step_id`, `data`, `options`, `errors`) — these were verified against the
existing `config_flow.py` code paths but not executed in this session.
