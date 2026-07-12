# Changelog v2.9.3

**Date:** 2026-07-11

## Fixed — CI failures surfaced after v2.9.2, plus one real production bug

The v2.9.2 CI run surfaced 6 failing tests. Triaged into three categories:

### 1. Bug in the new v2.9.2 tests (test-only, no production impact)
- `TestWebsocketCoversRealCoordinatorFields` in `tests/test_websocket.py`
  called the real `_process_room()` without setting `mold_risk_temp_min`/
  `mold_risk_temp_max` **and `mold_risk_humidity`** on the manually-constructed
  coordinator instance, which `_calculate_mold_risk()` reads. Added all three
  attributes (matching `DEFAULT_MOLD_RISK_TEMP_MIN`/`MAX`/`DEFAULT_MOLD_RISK_HUMIDITY`
  from `const.py`) to the test helper, plus `quiet_hours_start`/`quiet_hours_end`
  defensively (not strictly required for this test's no-dehumidifier room, but
  traced the full `_process_room()` call chain this time to avoid a third
  round of one-attribute-at-a-time CI failures).

### 2. Stale hardcoded version strings (test-only, no production impact)
- `tests/test_const.py::test_version_value` and
  `tests/test_diagnostics.py::test_returns_dict_with_version` both hardcoded
  `"2.5.2"` — stale since a much earlier release, exposed by the v2.9.2
  version bump. `test_const.py`'s check is now bumped to the current version
  (and commented to note it needs bumping on every release — there's no way
  to make a self-referential version pin "robust", since it tests
  `const.__version__` against itself). `test_diagnostics.py`'s check is now
  compared against the imported `const.__version__` instead of a hardcoded
  string, so it verifies diagnostics correctly *surfaces* whatever the
  current version is, rather than pinning an arbitrary number — this one
  will not go stale again.

### 3. Genuine pre-existing bugs, unrelated to the v2.9.2 session

- **`tests/test_coordinator.py::TestQuietHours::test_recommendation_respects_room_override`**
  patched `dt_util.now()` with `MagicMock(hour=13)` only. The dehumidifier
  recommendation path also calls `_get_season()`, which reads
  `dt_util.now().month` — since `month` was never set on the mock, it
  returned a bare `MagicMock`, causing `TypeError: '<=' not supported between
  instances of 'int' and 'MagicMock'` in `_get_season()`. Fixed by adding
  `month=7` to the mock.

- **`custom_components/indeklima/sensor.py` — real production bug.** All six
  `native_value`/`extra_state_attributes` properties across
  `IndeklimaGlobalSensor`, `IndeklimaRoomSensor` and `IndeklimaRoomMetricSensor`
  guarded against missing coordinator data with `if not self.coordinator.data:`.
  In Python, an empty dict (`{}`) is falsy — so this guard treated
  "coordinator has run and produced an empty-but-present data dict" the same
  as "coordinator has never run" (`data is None`), returning `None`/`{}`
  immediately instead of falling through to the sensor's own
  `.get(key, default)` fallback (e.g. `mold_risk_avg` defaulting to
  `MOLD_RISK_LOW`). Caught by
  `tests/test_sensor.py::TestGlobalMoldRiskSensor::test_missing_mold_risk_key_defaults_to_low`.
  Fixed all 6 occurrences to check `self.coordinator.data is None` instead.
  Real-world impact is likely low (`coordinator.data` is always a fully
  populated dict after `_async_do_update()` in normal operation), but this
  is a genuine correctness fix, not just a test fix.

## Files changed

- `tests/test_websocket.py`, `tests/test_const.py`, `tests/test_diagnostics.py`,
  `tests/test_coordinator.py`
- `custom_components/indeklima/sensor.py`
- `const.py` / `manifest.json`: version 2.9.2 → 2.9.3
