"""Tests for IndeklimaDataCoordinator._process_room, mold risk,
dehumidifier recommendation, and async update logic."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from custom_components.indeklima.const import (
    MOLD_RISK_LOW,
    MOLD_RISK_MODERATE,
    MOLD_RISK_HIGH,
    MOLD_RISK_CRITICAL,
    DEHUMIDIFIER_YES,
    DEHUMIDIFIER_NO,
    DEHUMIDIFIER_OPTIONAL,
    DEHUM_MODE_MANUAL,
    DEHUM_MODE_AUTO,
    DEHUM_MODE_OFF,
    CONF_ROOM_QUIET_HOURS_START,
    CONF_ROOM_QUIET_HOURS_END,
    CONF_DEHUMIDIFIER_LED,
    CONF_DEHUMIDIFIER_BUTTON,
    CONF_DEHUMIDIFIER_ON_DURATION,
    STATUS_GOOD,
    STATUS_WARNING,
    STATUS_CRITICAL,
    CONF_HUMIDITY_SENSORS,
    CONF_TEMPERATURE_SENSORS,
    CONF_CO2_SENSORS,
    CONF_PRESSURE_SENSORS,
    CONF_MOLD_SENSORS,
    CONF_WINDOW_SENSORS,
    CONF_WINDOW_ENTITY,
    CONF_WINDOW_IS_OUTDOOR,
    CONF_DEHUMIDIFIER,
)
from custom_components.indeklima.const import (
    CONF_ROOM_LED_CRITICAL_SEVERITY,
    DEHUM_LED_BLINK_INTERVAL,
    DEHUM_LED_RECOVERY_CYCLES,
)
from .conftest import make_state, mock_hass, mock_entry


def _make_coord(hass, entry, rooms=None, weather_entity=None,
                mold_risk_humidity=70, mold_risk_temp_min=5, mold_risk_temp_max=35,
                data=None):
    from custom_components.indeklima import IndeklimaDataCoordinator
    with patch(
        "custom_components.indeklima.DataUpdateCoordinator.__init__",
        return_value=None,
    ):
        coord = IndeklimaDataCoordinator.__new__(IndeklimaDataCoordinator)
        coord.hass = hass
        coord.entry = entry
        coord.rooms = rooms if rooms is not None else []
        coord.humidity_summer_max = 60
        coord.humidity_winter_max = 55
        coord.co2_max = 1000
        coord.voc_max = 3.0
        coord.formaldehyde_max = 0.15
        coord.mold_risk_humidity = mold_risk_humidity
        coord.mold_risk_temp_min = mold_risk_temp_min
        coord.mold_risk_temp_max = mold_risk_temp_max
        coord.weather_entity = weather_entity
        coord.quiet_hours_start = 23
        coord.quiet_hours_end = 6
        coord._dehumidifier_state = {}
        coord._button_unsubs = []
        coord._led_blink_unsubs = {}
        coord._room_critical_since = {}
        coord.history = {"humidity": [], "co2": [], "severity": []}
        coord.data = data
        return coord


# ── _calculate_mold_risk ──────────────────────────────────────────────────────

class TestCalculateMoldRisk:
    def test_none_humidity_returns_low(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_mold_risk(None, 20.0) == MOLD_RISK_LOW

    def test_low_humidity_returns_low(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_mold_risk(65.0, 20.0) == MOLD_RISK_LOW

    def test_at_threshold_returns_moderate(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_mold_risk(70.0, 20.0) == MOLD_RISK_MODERATE

    def test_above_threshold_5_returns_high(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_mold_risk(75.0, 20.0) == MOLD_RISK_HIGH

    def test_above_threshold_15_returns_critical(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_mold_risk(85.0, 20.0) == MOLD_RISK_CRITICAL

    def test_temp_too_cold_returns_low(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_mold_risk(85.0, 2.0) == MOLD_RISK_LOW

    def test_temp_too_hot_returns_low(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_mold_risk(85.0, 40.0) == MOLD_RISK_LOW

    def test_none_temperature_assumes_in_range(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        # No temp -> temp_in_range = True -> mold risk based only on humidity
        assert coord._calculate_mold_risk(70.0, None) == MOLD_RISK_MODERATE

    def test_custom_thresholds(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry, mold_risk_humidity=80)
        assert coord._calculate_mold_risk(79.0, 20.0) == MOLD_RISK_LOW
        assert coord._calculate_mold_risk(80.0, 20.0) == MOLD_RISK_MODERATE

    def test_critical_boundary(self, mock_hass, mock_entry):
        # 70 + 15 = 85 -> critical
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_mold_risk(84.9, 20.0) == MOLD_RISK_HIGH
        assert coord._calculate_mold_risk(85.0, 20.0) == MOLD_RISK_CRITICAL


# ── _calculate_dehumidifier_recommendation ────────────────────────────────────

class TestCalculateDehumidifierRecommendation:
    def _base_room(self, humidity=50.0, mold_risk=MOLD_RISK_LOW,
                   outdoor_open=0, hour=12):
        return {
            "humidity": humidity,
            "mold_risk": mold_risk,
            "outdoor_windows_open": outdoor_open,
        }

    def test_outdoor_window_open_returns_no(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = self._base_room(outdoor_open=1, mold_risk=MOLD_RISK_HIGH)
        assert coord._calculate_dehumidifier_recommendation(room, {}) == DEHUMIDIFIER_NO

    def test_high_mold_risk_returns_yes(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = self._base_room(mold_risk=MOLD_RISK_HIGH)
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=12)
            result = coord._calculate_dehumidifier_recommendation(room, {})
        assert result == DEHUMIDIFIER_YES

    def test_critical_mold_risk_returns_yes(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = self._base_room(mold_risk=MOLD_RISK_CRITICAL)
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._calculate_dehumidifier_recommendation(room, {})
        assert result == DEHUMIDIFIER_YES

    def test_night_low_mold_returns_no(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = self._base_room(humidity=65.0, mold_risk=MOLD_RISK_LOW)
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=2)
            result = coord._calculate_dehumidifier_recommendation(room, {})
        assert result == DEHUMIDIFIER_NO

    def test_night_moderate_mold_still_optional(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        # Night suppression only skips when mold_risk == LOW.
        # Moderate mold bypasses night suppression and reaches humidity check.
        # humidity=50 (below threshold 55/60) + moderate mold -> OPTIONAL
        room = self._base_room(humidity=50.0, mold_risk=MOLD_RISK_MODERATE)
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=2)
            result = coord._calculate_dehumidifier_recommendation(room, {})
        assert result == DEHUMIDIFIER_OPTIONAL

    def test_high_humidity_low_mold_returns_optional(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = self._base_room(humidity=65.0, mold_risk=MOLD_RISK_LOW)
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._calculate_dehumidifier_recommendation(room, {})
        assert result == DEHUMIDIFIER_OPTIONAL

    def test_high_humidity_moderate_mold_returns_yes(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = self._base_room(humidity=65.0, mold_risk=MOLD_RISK_MODERATE)
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._calculate_dehumidifier_recommendation(room, {})
        assert result == DEHUMIDIFIER_YES

    def test_good_conditions_returns_no(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = self._base_room(humidity=45.0, mold_risk=MOLD_RISK_LOW)
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._calculate_dehumidifier_recommendation(room, {})
        assert result == DEHUMIDIFIER_NO

    def test_moderate_mold_no_humidity_breach_returns_optional(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = self._base_room(humidity=50.0, mold_risk=MOLD_RISK_MODERATE)
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._calculate_dehumidifier_recommendation(room, {})
        assert result == DEHUMIDIFIER_OPTIONAL


# ── _process_room ─────────────────────────────────────────────────────────────

class TestProcessRoom:
    def _make_state_map(self, values: dict):
        """Return a side_effect function mapping entity_id -> state value."""
        def get_state(entity_id):
            if entity_id in values:
                return make_state(str(values[entity_id]))
            return None
        return get_state

    def test_collects_scalar_sensors(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.hum": "55.0",
            "sensor.temp": "21.5",
            "sensor.co2": "850",
        })
        room_cfg = {
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_TEMPERATURE_SENSORS: ["sensor.temp"],
            CONF_CO2_SENSORS: ["sensor.co2"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            result = coord._process_room(room_cfg, data)
        assert result["humidity"] == 55.0
        assert result["temperature"] == 21.5
        assert result["co2"] == 850.0

    def test_averages_multiple_sensors(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.hum1": "40.0",
            "sensor.hum2": "60.0",
        })
        room_cfg = {
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.hum1", "sensor.hum2"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            result = coord._process_room(room_cfg, data)
        assert result["humidity"] == 50.0
        assert result["humidity_sensors_count"] == 2

    def test_mold_risk_uses_dedicated_sensor(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.hum": "55.0",
            "sensor.mold": "80.0",  # dedicated mold sensor is higher
        })
        room_cfg = {
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_MOLD_SENSORS: ["sensor.mold"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            result = coord._process_room(room_cfg, data)
        # Dedicated mold sensor (80%) should trigger high/critical risk
        assert result["mold_risk"] in (MOLD_RISK_HIGH, MOLD_RISK_CRITICAL)
        assert result["mold_humidity"] == 80.0

    def test_mold_sensors_count_set_when_dedicated_sensor_configured(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.hum": "55.0",
            "sensor.mold": "72.0",
        })
        room_cfg = {
            "name": "Bad",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_MOLD_SENSORS: ["sensor.mold"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            result = coord._process_room(room_cfg, data)
        assert result["mold_sensors_count"] == 1
        assert result["mold_humidity"] == 72.0

    def test_mold_sensors_count_absent_without_dedicated_sensor(self, mock_hass, mock_entry):
        """Mold risk is a calculated value (outdoor/room temp + room humidity sensor),
        not a physical mold sensor — no dedicated sensor configured means no count."""
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.hum": "72.0",
        })
        room_cfg = {
            "name": "Bad",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            result = coord._process_room(room_cfg, data)
        assert "mold_sensors_count" not in result
        assert result["mold_risk"] == MOLD_RISK_MODERATE  # fallback to room humidity (72% >= 70%)

    def test_mold_risk_falls_back_to_humidity(self, mock_hass, mock_entry):
        # 72% is above 70 (moderate) but below 75 (high threshold = 70+5)
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.hum": "76.0",  # 76 >= 70+5 -> MOLD_RISK_HIGH
        })
        room_cfg = {
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            result = coord._process_room(room_cfg, data)
        assert result["mold_risk"] == MOLD_RISK_HIGH

    def test_outdoor_window_counted(self, mock_hass, mock_entry):
        def get_state(entity_id):
            if entity_id == "binary_sensor.window":
                s = MagicMock()
                s.state = "on"
                return s
            return None
        mock_hass.states.get.side_effect = get_state
        room_cfg = {
            "name": "Stue",
            CONF_WINDOW_SENSORS: [{
                CONF_WINDOW_ENTITY: "binary_sensor.window",
                CONF_WINDOW_IS_OUTDOOR: True,
            }],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        result = coord._process_room(room_cfg, data)
        assert result["outdoor_windows_open"] == 1
        assert "Stue" in data["open_windows"]

    def test_internal_door_counted(self, mock_hass, mock_entry):
        def get_state(entity_id):
            if entity_id == "binary_sensor.door":
                s = MagicMock()
                s.state = "on"
                return s
            return None
        mock_hass.states.get.side_effect = get_state
        room_cfg = {
            "name": "Stue",
            CONF_WINDOW_SENSORS: [{
                CONF_WINDOW_ENTITY: "binary_sensor.door",
                CONF_WINDOW_IS_OUTDOOR: False,
            }],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        result = coord._process_room(room_cfg, data)
        assert result["internal_doors_open"] == 1
        assert "Stue" in data["open_internal_doors"]

    def test_severity_and_status_set(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.hum": "45.0",
            "sensor.co2": "500.0",
        })
        room_cfg = {
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_CO2_SENSORS: ["sensor.co2"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            result = coord._process_room(room_cfg, data)
        assert "severity" in result
        assert result["severity"] == 0.0
        assert result["status"] == STATUS_GOOD

    def test_dehumidifier_skipped_when_not_configured(self, mock_hass, mock_entry):
        room_cfg = {"name": "Stue"}
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        result = coord._process_room(room_cfg, data)
        assert result["has_dehumidifier"] is False
        assert result["dehumidifier_recommendation"] == DEHUMIDIFIER_NO

    def test_dehumidifier_calculated_when_configured(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.hum": "72.0",
        })
        room_cfg = {
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_DEHUMIDIFIER: "switch.dehumidifier",
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._process_room(room_cfg, data)
        assert result["has_dehumidifier"] is True
        assert result["dehumidifier_recommendation"] != DEHUMIDIFIER_NO

    def test_legacy_string_window_sensor(self, mock_hass, mock_entry):
        """Backward compat: window_sensors as plain string list."""
        def get_state(entity_id):
            s = MagicMock()
            s.state = "on"
            return s
        mock_hass.states.get.side_effect = get_state
        room_cfg = {
            "name": "Stue",
            CONF_WINDOW_SENSORS: ["binary_sensor.window_old"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        result = coord._process_room(room_cfg, data)
        assert result["outdoor_windows_open"] == 1

    def test_none_entity_id_in_window_sensor_skipped(self, mock_hass, mock_entry):
        room_cfg = {
            "name": "Stue",
            CONF_WINDOW_SENSORS: [{CONF_WINDOW_ENTITY: None, CONF_WINDOW_IS_OUTDOOR: True}],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        result = coord._process_room(room_cfg, data)
        assert result["outdoor_windows_open"] == 0

    def test_pressure_sensor_collected(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = self._make_state_map({
            "sensor.pressure": "1013.25",
        })
        room_cfg = {
            "name": "Stue",
            CONF_PRESSURE_SENSORS: ["sensor.pressure"],
        }
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": [], "open_internal_doors": []}
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            result = coord._process_room(room_cfg, data)
        assert result["pressure"] == pytest.approx(1013.25)


# ── _async_do_update integration ─────────────────────────────────────────────

class TestAsyncDoUpdate:
    async def _run_update(self, coord):
        with patch("custom_components.indeklima.raise_coordinator_failed_issue"), \
             patch("custom_components.indeklima.clear_coordinator_failed_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 6, 1, 12, 0, 0)
            return await coord._async_do_update()

    @pytest.mark.asyncio
    async def test_empty_rooms_returns_defaults(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry, rooms=[])
        result = await self._run_update(coord)
        assert result["status"] == STATUS_GOOD
        assert result["severity"] == 0
        assert result["rooms"] == {}

    @pytest.mark.asyncio
    async def test_single_room_processed(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("50.0")
        rooms = [{
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_TEMPERATURE_SENSORS: ["sensor.temp"],
        }]
        coord = _make_coord(mock_hass, mock_entry, rooms=rooms)
        result = await self._run_update(coord)
        assert "Stue" in result["rooms"]
        assert result["rooms"]["Stue"]["humidity"] == 50.0

    @pytest.mark.asyncio
    async def test_room_exception_does_not_abort_update(self, mock_hass, mock_entry):
        """A broken room should be skipped; other rooms still processed."""
        good_room = {
            "name": "GodtRum",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
        }
        # Bad room: _process_room will raise because of intentionally bad config
        bad_room = {"name": "DaarligtRum", CONF_HUMIDITY_SENSORS: None}

        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("50.0")

        coord = _make_coord(mock_hass, mock_entry, rooms=[bad_room, good_room])

        # Patch _process_room to raise on bad_room, succeed on good_room
        original_process = coord._process_room
        def selective_process(room, data):
            if room["name"] == "DaarligtRum":
                raise ValueError("simulated bad room")
            return original_process(room, data)

        coord._process_room = selective_process

        with patch("custom_components.indeklima.raise_coordinator_failed_issue"), \
             patch("custom_components.indeklima.clear_coordinator_failed_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 6, 1, 12, 0, 0)
            result = await coord._async_do_update()

        # Bad room skipped, good room present
        assert "GodtRum" in result["rooms"]
        assert "DaarligtRum" not in result["rooms"]

    @pytest.mark.asyncio
    async def test_global_mold_risk_is_worst_room(self, mock_hass, mock_entry):
        # Use explicit entity IDs that don't overlap on substring match
        def get_state(entity_id):
            if entity_id == "sensor.stue_hum":
                return make_state("50.0")   # low mold
            if entity_id == "sensor.soverum_hum":
                return make_state("85.0")   # critical mold (>= 70+15)
            return None
        mock_hass.states.get.side_effect = get_state

        rooms = [
            {"name": "Stue", CONF_HUMIDITY_SENSORS: ["sensor.stue_hum"]},
            {"name": "Soverum", CONF_HUMIDITY_SENSORS: ["sensor.soverum_hum"]},
        ]
        coord = _make_coord(mock_hass, mock_entry, rooms=rooms)

        with patch("custom_components.indeklima.raise_coordinator_failed_issue"), \
             patch("custom_components.indeklima.clear_coordinator_failed_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 6, 1, 12, 0, 0)
            result = await coord._async_do_update()

        assert result["mold_risk"] == MOLD_RISK_CRITICAL

    @pytest.mark.asyncio
    async def test_circulation_bonus_applied(self, mock_hass, mock_entry):
        def get_state(entity_id):
            if "door" in entity_id:
                s = MagicMock(); s.state = "on"; return s
            if "hum" in entity_id:
                return make_state("70.0")
            return None
        mock_hass.states.get.side_effect = get_state

        rooms = [{
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_WINDOW_SENSORS: [{
                CONF_WINDOW_ENTITY: "binary_sensor.door",
                CONF_WINDOW_IS_OUTDOOR: False,
            }],
        }]
        coord = _make_coord(mock_hass, mock_entry, rooms=rooms)

        with patch("custom_components.indeklima.raise_coordinator_failed_issue"), \
             patch("custom_components.indeklima.clear_coordinator_failed_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 6, 1, 12, 0, 0)
            result = await coord._async_do_update()

        # Room severity without bonus would be 30; with 5% bonus -> 28.5
        room_sev = result["rooms"]["Stue"]["severity"]
        global_sev = result["severity"]
        assert global_sev < room_sev  # bonus reduces global below room score

    @pytest.mark.asyncio
    async def test_global_dehumidifier_worst_room_wins(self, mock_hass, mock_entry):
        # Stue: low humidity -> NO; Soverum: 85% humidity -> critical mold -> YES
        def get_state(entity_id):
            if entity_id == "sensor.soverum_hum":
                return make_state("85.0")  # critical mold -> DEHUMIDIFIER_YES
            return make_state("45.0")      # Stue: low -> DEHUMIDIFIER_NO
        mock_hass.states.get.side_effect = get_state

        rooms = [
            {"name": "Stue",
             CONF_HUMIDITY_SENSORS: ["sensor.stue_hum"],
             CONF_DEHUMIDIFIER: "switch.stue_dehum"},
            {"name": "Soverum",
             CONF_HUMIDITY_SENSORS: ["sensor.soverum_hum"],
             CONF_DEHUMIDIFIER: "switch.sov_dehum"},
        ]
        coord = _make_coord(mock_hass, mock_entry, rooms=rooms)

        with patch("custom_components.indeklima.raise_coordinator_failed_issue"), \
             patch("custom_components.indeklima.clear_coordinator_failed_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 6, 1, 12, 0, 0)
            result = await coord._async_do_update()

        # Soverum at 85% -> critical mold -> DEHUMIDIFIER_YES wins globally
        assert result["dehumidifier_recommendation"] == DEHUMIDIFIER_YES


# ── Quiet hours ──────────────────────────────────────────────

class TestQuietHours:
    def test_room_uses_hub_default_when_no_override(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        coord.quiet_hours_start = 23
        coord.quiet_hours_end = 6
        room = {"name": "Stue"}
        assert coord._get_quiet_hours(room) == (23, 6)

    def test_room_override_takes_precedence(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        coord.quiet_hours_start = 23
        coord.quiet_hours_end = 6
        room = {
            "name": "Bad",
            CONF_ROOM_QUIET_HOURS_START: 21,
            CONF_ROOM_QUIET_HOURS_END: 8,
        }
        assert coord._get_quiet_hours(room) == (21, 8)

    def test_is_quiet_hours_within_window(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = {"name": "Stue"}
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=2)
            assert coord._is_quiet_hours(room) is True

    def test_is_quiet_hours_outside_window(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = {"name": "Stue"}
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=14)
            assert coord._is_quiet_hours(room) is False

    def test_room_override_changes_quiet_window(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = {
            "name": "Bad",
            CONF_ROOM_QUIET_HOURS_START: 12,
            CONF_ROOM_QUIET_HOURS_END: 15,
        }
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=13)
            assert coord._is_quiet_hours(room) is True

    def test_recommendation_respects_room_override(self, mock_hass, mock_entry):
        """Hub default is 23-06, but this room overrides to 12-15 (currently quiet).
        Low mold risk during the room's own quiet window -> NO despite hub saying it's daytime."""
        coord = _make_coord(mock_hass, mock_entry)
        room_data = {
            "humidity": 65.0,
            "mold_risk": MOLD_RISK_LOW,
            "outdoor_windows_open": 0,
        }
        room = {
            "name": "Bad",
            CONF_ROOM_QUIET_HOURS_START: 12,
            CONF_ROOM_QUIET_HOURS_END: 15,
        }
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(hour=13)
            result = coord._calculate_dehumidifier_recommendation(room_data, room)
        assert result == DEHUMIDIFIER_NO


# ── Dehumidifier control: start / stop / button / LED / auto ──────────────

class TestDehumidifierControl:
    def _room(self, **overrides):
        room = {
            "name": "Bad",
            CONF_DEHUMIDIFIER: "switch.affugter",
            CONF_DEHUMIDIFIER_LED: "light.bad_led",
            CONF_DEHUMIDIFIER_BUTTON: "sensor.bad_knap",
        }
        room.update(overrides)
        return room

    @pytest.mark.asyncio
    async def test_start_turns_on_switch_and_sets_manual_mode(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.services.async_call = AsyncMock()
        mock_hass.async_create_task = MagicMock()
        room = self._room()

        await coord._async_start_dehumidifier(room, DEHUM_MODE_MANUAL)

        mock_hass.services.async_call.assert_any_call(
            "switch", "turn_on", {"entity_id": "switch.affugter"}, blocking=False
        )
        assert coord._dehumidifier_state["Bad"]["mode"] == DEHUM_MODE_MANUAL
        assert coord._dehumidifier_state["Bad"]["unsub_timer"] is not None

    @pytest.mark.asyncio
    async def test_start_sets_led_manual_color(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.services.async_call = AsyncMock()
        captured = []
        mock_hass.async_create_task = MagicMock(side_effect=lambda coro: captured.append(coro))
        room = self._room()

        await coord._async_start_dehumidifier(room, DEHUM_MODE_MANUAL)
        for coro in captured:
            await coro

        mock_hass.services.async_call.assert_any_call(
            "light", "turn_on",
            {"entity_id": "light.bad_led", "rgb_color": [0, 100, 255], "brightness_pct": 76},
            blocking=False,
        )

    @pytest.mark.asyncio
    async def test_start_sets_led_auto_color(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.services.async_call = AsyncMock()
        captured = []
        mock_hass.async_create_task = MagicMock(side_effect=lambda coro: captured.append(coro))
        room = self._room()

        await coord._async_start_dehumidifier(room, DEHUM_MODE_AUTO)
        for coro in captured:
            await coro

        mock_hass.services.async_call.assert_any_call(
            "light", "turn_on",
            {"entity_id": "light.bad_led", "rgb_color": [255, 255, 133], "brightness_pct": 76},
            blocking=False,
        )

    @pytest.mark.asyncio
    async def test_stop_turns_off_switch_when_on(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.services.async_call = AsyncMock()
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("on")
        room = self._room()
        coord._dehumidifier_state["Bad"] = {"mode": DEHUM_MODE_MANUAL, "unsub_timer": MagicMock()}

        await coord._async_stop_dehumidifier(room)

        mock_hass.services.async_call.assert_any_call(
            "switch", "turn_off", {"entity_id": "switch.affugter"}, blocking=False
        )
        assert coord._dehumidifier_state["Bad"]["mode"] == DEHUM_MODE_OFF

    @pytest.mark.asyncio
    async def test_stop_skips_turn_off_when_already_off(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.services.async_call = AsyncMock()
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("off")
        room = self._room()

        await coord._async_stop_dehumidifier(room)

        for call in mock_hass.services.async_call.call_args_list:
            assert call.args[:2] != ("switch", "turn_off")

    @pytest.mark.asyncio
    async def test_stop_cancels_pending_timer(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.services.async_call = AsyncMock()
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("off")
        timer_unsub = MagicMock()
        room = self._room()
        coord._dehumidifier_state["Bad"] = {"mode": DEHUM_MODE_AUTO, "unsub_timer": timer_unsub}

        await coord._async_stop_dehumidifier(room)

        timer_unsub.assert_called_once()

    @pytest.mark.asyncio
    async def test_button_press_turns_on_when_off(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.services.async_call = AsyncMock()
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("off")
        room = self._room()

        await coord._async_handle_button_press(room)

        mock_hass.services.async_call.assert_any_call(
            "switch", "turn_on", {"entity_id": "switch.affugter"}, blocking=False
        )
        assert coord._dehumidifier_state["Bad"]["mode"] == DEHUM_MODE_MANUAL

    @pytest.mark.asyncio
    async def test_button_press_turns_off_when_on(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.services.async_call = AsyncMock()
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("on")
        room = self._room()

        await coord._async_handle_button_press(room)

        mock_hass.services.async_call.assert_any_call(
            "switch", "turn_off", {"entity_id": "switch.affugter"}, blocking=False
        )
        assert coord._dehumidifier_state["Bad"]["mode"] == DEHUM_MODE_OFF

    @pytest.mark.asyncio
    async def test_button_press_noop_without_switch_configured(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        room = {"name": "Bad"}  # no CONF_DEHUMIDIFIER
        # Should not raise even though nothing is configured
        await coord._async_handle_button_press(room)
        assert "Bad" not in coord._dehumidifier_state

    def test_auto_control_starts_when_recommended(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        captured = []
        mock_hass.async_create_task = MagicMock(side_effect=lambda coro: captured.append(coro))
        room = self._room()
        room_data = {"dehumidifier_recommendation": DEHUMIDIFIER_YES}

        coord._maybe_auto_control_dehumidifier(room, room_data)

        assert len(captured) == 1
        captured[0].close()  # avoid "never awaited" warning; we only check scheduling

    def test_auto_control_does_not_override_manual(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()
        room = self._room()
        coord._dehumidifier_state["Bad"] = {"mode": DEHUM_MODE_MANUAL, "unsub_timer": None}
        room_data = {"dehumidifier_recommendation": DEHUMIDIFIER_YES}

        coord._maybe_auto_control_dehumidifier(room, room_data)

        mock_hass.async_create_task.assert_not_called()

    def test_auto_control_skips_when_not_recommended(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()
        room = self._room()
        room_data = {"dehumidifier_recommendation": DEHUMIDIFIER_NO}

        coord._maybe_auto_control_dehumidifier(room, room_data)

        mock_hass.async_create_task.assert_not_called()


# ── Button listener setup / teardown ──────────────────────────

class TestDehumidifierListeners:
    def test_setup_registers_listener_only_for_rooms_with_button(self, mock_hass, mock_entry):
        rooms = [
            {"name": "Bad", CONF_DEHUMIDIFIER_BUTTON: "sensor.bad_knap"},
            {"name": "Stue"},  # no button configured
        ]
        coord = _make_coord(mock_hass, mock_entry, rooms=rooms)
        with patch("custom_components.indeklima.async_track_state_change_event") as mock_track:
            mock_track.return_value = MagicMock()
            coord.async_setup_dehumidifier_listeners()
        assert mock_track.call_count == 1
        assert len(coord._button_unsubs) == 1

    def test_unload_cancels_listeners_and_timers(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        listener_unsub = MagicMock()
        timer_unsub = MagicMock()
        coord._button_unsubs = [listener_unsub]
        coord._dehumidifier_state = {"Bad": {"mode": DEHUM_MODE_AUTO, "unsub_timer": timer_unsub}}

        coord.async_unload_dehumidifier_listeners()

        listener_unsub.assert_called_once()
        timer_unsub.assert_called_once()
        assert coord._button_unsubs == []


# ── LED critical-alert override (severity-status == critical → red) ─────────

class TestDehumidifierLedCriticalAlert:
    def _critical_room_cfg(self):
        return {
            "name": "Bad",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_CO2_SENSORS: ["sensor.co2"],
            CONF_DEHUMIDIFIER: "switch.affugter",
            CONF_DEHUMIDIFIER_LED: "light.bad_led",
        }

    def _get_state_fn(self, humidity, co2):
        def get_state(entity_id):
            if entity_id == "sensor.hum":
                return make_state(str(humidity))
            if entity_id == "sensor.co2":
                return make_state(str(co2))
            return None
        return get_state

    def test_led_turns_red_when_room_status_critical(self, mock_hass, mock_entry):
        # humidity excess 30*3=90 (capped 30) + co2 excess capped 30 = severity 60 -> critical
        mock_hass.states.get.side_effect = self._get_state_fn(humidity=90.0, co2=5000)
        room_cfg = self._critical_room_cfg()
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._process_room(room_cfg, data)

        assert result["status"] == STATUS_CRITICAL
        assert coord._dehumidifier_state["Bad"]["led_color"] == "red"

    def test_led_stays_red_even_when_mode_is_auto(self, mock_hass, mock_entry):
        """RED alarm overrides the auto/manual colour, per design decision."""
        mock_hass.states.get.side_effect = self._get_state_fn(humidity=90.0, co2=5000)
        room_cfg = self._critical_room_cfg()
        coord = _make_coord(mock_hass, mock_entry)
        coord._dehumidifier_state["Bad"] = {"mode": DEHUM_MODE_AUTO, "unsub_timer": None}
        mock_hass.async_create_task = MagicMock()
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._process_room(room_cfg, data)

        assert result["status"] == STATUS_CRITICAL
        assert coord._dehumidifier_state["Bad"]["led_color"] == "red"
        # Underlying control mode is untouched -- only the LED colour is overridden
        assert coord._dehumidifier_state["Bad"]["mode"] == DEHUM_MODE_AUTO

    def test_led_reverts_to_manual_color_after_recovery(self, mock_hass, mock_entry):
        room_cfg = self._critical_room_cfg()
        coord = _make_coord(mock_hass, mock_entry)
        coord._dehumidifier_state["Bad"] = {
            "mode": DEHUM_MODE_MANUAL, "unsub_timer": None, "led_color": "red",
        }
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = self._get_state_fn(humidity=45.0, co2=500)
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            result = coord._process_room(room_cfg, data)

        assert result["status"] != STATUS_CRITICAL
        assert coord._dehumidifier_state["Bad"]["led_color"] == "blue"

    def test_led_reverts_to_off_after_recovery_when_not_running(self, mock_hass, mock_entry):
        room_cfg = self._critical_room_cfg()
        coord = _make_coord(mock_hass, mock_entry)
        coord._dehumidifier_state["Bad"] = {
            "mode": DEHUM_MODE_OFF, "unsub_timer": None, "led_color": "red",
        }
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = self._get_state_fn(humidity=45.0, co2=500)
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            coord._process_room(room_cfg, data)

        assert coord._dehumidifier_state["Bad"]["led_color"] == "off"

    def test_no_redundant_service_call_when_color_unchanged(self, mock_hass, mock_entry):
        """LED service should not be re-triggered every 30s cycle if the colour hasn't changed."""
        room_cfg = self._critical_room_cfg()
        coord = _make_coord(mock_hass, mock_entry)
        coord._dehumidifier_state["Bad"] = {
            "mode": DEHUM_MODE_OFF, "unsub_timer": None, "led_color": "off",
        }
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = self._get_state_fn(humidity=45.0, co2=500)
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            coord._process_room(room_cfg, data)

        mock_hass.async_create_task.assert_not_called()

    def test_no_led_block_when_no_led_configured(self, mock_hass, mock_entry):
        """Rooms without a configured LED entity must never populate 'led_color' in
        _dehumidifier_state — the LED-refresh block should be skipped entirely."""
        room_cfg = {
            "name": "Bad",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_CO2_SENSORS: ["sensor.co2"],
            CONF_DEHUMIDIFIER: "switch.affugter",
            # no CONF_DEHUMIDIFIER_LED
        }
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()
        mock_hass.states.get.side_effect = self._get_state_fn(humidity=90.0, co2=5000)
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            coord._process_room(room_cfg, data)

        assert "led_color" not in coord._dehumidifier_state.get("Bad", {})


# ── LED alarm state machine: blink, hysteresis, per-room threshold, kritisk_siden ──

class TestLedCriticalAlarmMachine:
    def _room_cfg(self, led=True, threshold=None):
        cfg = {
            "name": "Bad",
            CONF_HUMIDITY_SENSORS: ["sensor.hum"],
            CONF_CO2_SENSORS: ["sensor.co2"],
            CONF_DEHUMIDIFIER: "switch.affugter",
        }
        if led:
            cfg[CONF_DEHUMIDIFIER_LED] = "light.bad_led"
        if threshold is not None:
            cfg[CONF_ROOM_LED_CRITICAL_SEVERITY] = threshold
        return cfg

    def _get_state_fn(self, humidity, co2):
        def get_state(entity_id):
            if entity_id == "sensor.hum":
                return make_state(str(humidity))
            if entity_id == "sensor.co2":
                return make_state(str(co2))
            return None
        return get_state

    def test_entering_critical_starts_blink_alarm(self, mock_hass, mock_entry):
        # humidity excess 30*3=90 (capped 30) + co2 excess capped 30 = severity 60 -> critical
        mock_hass.states.get.side_effect = self._get_state_fn(90.0, 5000)
        room_cfg = self._room_cfg()
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()
        mock_hass.services.async_call = MagicMock()
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt, \
             patch("custom_components.indeklima.async_call_later") as mock_call_later:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 7, 4, 12, 0, 0)
            mock_call_later.return_value = MagicMock()
            result = coord._process_room(room_cfg, data)

        assert result["status"] == STATUS_CRITICAL
        state = coord._dehumidifier_state["Bad"]
        assert state["led_alarm_active"] is True
        assert state["led_color"] == "red"
        mock_hass.services.async_call.assert_any_call(
            "light", "turn_on",
            {"entity_id": "light.bad_led", "rgb_color": [255, 0, 0], "brightness_pct": 100},
            blocking=False,
        )
        # A blink timer must have been scheduled at DEHUM_LED_BLINK_INTERVAL
        assert mock_call_later.call_args.args[1] == DEHUM_LED_BLINK_INTERVAL

    def test_alarm_persists_through_hysteresis_then_clears(self, mock_hass, mock_entry):
        room_cfg = self._room_cfg()
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()
        mock_hass.services.async_call = MagicMock()

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt, \
             patch("custom_components.indeklima.async_call_later") as mock_call_later:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 7, 4, 12, 0, 0)
            mock_call_later.return_value = MagicMock()

            # Cycle 1: critical -> alarm starts
            mock_hass.states.get.side_effect = self._get_state_fn(90.0, 5000)
            coord._process_room(room_cfg, {"open_windows": [], "open_internal_doors": []})
            assert coord._dehumidifier_state["Bad"]["led_alarm_active"] is True

            # Cycle 2: recovers, but hysteresis (DEHUM_LED_RECOVERY_CYCLES=2) keeps alarm active
            mock_hass.states.get.side_effect = self._get_state_fn(45.0, 500)
            coord._process_room(room_cfg, {"open_windows": [], "open_internal_doors": []})
            assert coord._dehumidifier_state["Bad"]["led_alarm_active"] is True
            assert coord._dehumidifier_state["Bad"]["recovery_count"] == 1

            # Cycle 3: second consecutive good cycle -> alarm clears, reverts to mode colour
            coord._process_room(room_cfg, {"open_windows": [], "open_internal_doors": []})
            assert coord._dehumidifier_state["Bad"]["led_alarm_active"] is False
            assert coord._dehumidifier_state["Bad"]["led_color"] == "off"

    def test_per_room_threshold_override_triggers_earlier(self, mock_hass, mock_entry):
        # humidity=70 -> excess (70-60)*3=30, co2=500 (fine) => severity=30 -> WARNING globally
        mock_hass.states.get.side_effect = self._get_state_fn(70.0, 500)
        room_cfg = self._room_cfg(threshold=30)
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()
        mock_hass.services.async_call = MagicMock()
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt, \
             patch("custom_components.indeklima.async_call_later") as mock_call_later:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 7, 4, 12, 0, 0)
            mock_call_later.return_value = MagicMock()
            result = coord._process_room(room_cfg, data)

        assert result["status"] == STATUS_WARNING  # official classification unaffected
        assert coord._dehumidifier_state["Bad"]["led_alarm_active"] is True  # LED-only override triggered

    def test_default_threshold_does_not_trigger_below_60(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = self._get_state_fn(70.0, 500)
        room_cfg = self._room_cfg()  # no override -> default threshold 60
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()
        mock_hass.services.async_call = MagicMock()
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt, \
             patch("custom_components.indeklima.async_call_later") as mock_call_later:
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 7, 4, 12, 0, 0)
            mock_call_later.return_value = MagicMock()
            coord._process_room(room_cfg, data)

        assert coord._dehumidifier_state["Bad"].get("led_alarm_active", False) is False

    def test_kritisk_siden_set_and_stable_across_cycles(self, mock_hass, mock_entry):
        """kritisk_siden works independently of LED configuration."""
        room_cfg = self._room_cfg(led=False)
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt, \
             patch("custom_components.indeklima.async_call_later"):
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.side_effect = [
                datetime(2026, 7, 4, 12, 0, 0),
                datetime(2026, 7, 4, 12, 0, 30),
            ]

            mock_hass.states.get.side_effect = self._get_state_fn(90.0, 5000)
            result1 = coord._process_room(room_cfg, {"open_windows": [], "open_internal_doors": []})
            result2 = coord._process_room(room_cfg, {"open_windows": [], "open_internal_doors": []})

        assert result1["kritisk_siden"] == "2026-07-04T12:00:00"
        # Stable across a second consecutive critical cycle -- not re-set to the 2nd utcnow() value
        assert result2["kritisk_siden"] == "2026-07-04T12:00:00"

    def test_kritisk_siden_cleared_immediately_on_recovery(self, mock_hass, mock_entry):
        """Unlike the LED alarm, kritisk_siden has no hysteresis -- it clears the
        instant the room's real status leaves critical."""
        room_cfg = self._room_cfg(led=False)
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.async_create_task = MagicMock()

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.dt_util") as mock_dt, \
             patch("custom_components.indeklima.async_call_later"):
            mock_dt.now.return_value = MagicMock(month=6, hour=14)
            mock_dt.utcnow.return_value = datetime(2026, 7, 4, 12, 0, 0)

            mock_hass.states.get.side_effect = self._get_state_fn(90.0, 5000)
            coord._process_room(room_cfg, {"open_windows": [], "open_internal_doors": []})

            mock_hass.states.get.side_effect = self._get_state_fn(45.0, 500)
            result = coord._process_room(room_cfg, {"open_windows": [], "open_internal_doors": []})

        assert "kritisk_siden" not in result

    def test_unload_cancels_led_blink_timers(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        blink_unsub = MagicMock()
        coord._led_blink_unsubs = {"Bad": blink_unsub}

        coord.async_unload_dehumidifier_listeners()

        blink_unsub.assert_called_once()
        assert coord._led_blink_unsubs == {}
