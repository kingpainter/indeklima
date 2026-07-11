"""Tests for websocket.py handlers."""
from __future__ import annotations

from unittest.mock import MagicMock, patch
import pytest

from custom_components.indeklima.websocket import (
    ws_get_climate_data,
    ws_get_room_data,
    _get_coordinator,
)
from custom_components.indeklima.const import DOMAIN


def _make_coordinator(rooms_data=None, averages=None, trends=None, ventilation=None):
    """Build a minimal coordinator mock."""
    coord = MagicMock()
    coord.rooms = [{"name": "Stue"}, {"name": "Soveværelse"}]
    coord.weather_entity = "weather.home"
    coord.data = {
        "severity": 15.0,
        "status": "good",
        "open_windows": [],
        "open_internal_doors": [],
        "air_circulation": "moderate",
        "averages": averages or {"humidity": 45.0, "temperature": 22.0, "co2": 400.0, "pressure": 1013.0},
        "mold_risk": "low",
        "dehumidifier_recommendation": "no",
        "trends": trends or {"humidity": "stable", "co2": "stable", "severity": "stable"},
        "ventilation": ventilation or {
            "status": "no",
            "reason": ["Indeklima er OK"],
            "rooms": [],
            "outdoor_temp": 12.0,
            "outdoor_humidity": 70.0,
        },
        "rooms": rooms_data or {
            "Stue": {
                "status": "good",
                "severity": 10.0,
                "temperature": 22.0,
                "humidity": 45.0,
                "co2": 400.0,
                "pressure": 1013.0,
                "mold_risk": "low",
                "dehumidifier_recommendation": "no",
                "outdoor_windows_open": 0,
                "internal_doors_open": 1,
                "temperature_sensors_count": 1,
                "humidity_sensors_count": 1,
                "co2_sensors_count": 1,
                "pressure_sensors_count": 1,
                "mold_sensors_count": 0,
            },
            "Soveværelse": {
                "status": "warning",
                "severity": 35.0,
                "temperature": 19.0,
                "humidity": 65.0,
                "co2": None,
                "pressure": None,
                "mold_risk": "moderate",
                "dehumidifier_recommendation": "optional",
                "outdoor_windows_open": 0,
                "internal_doors_open": 0,
                "temperature_sensors_count": 1,
                "humidity_sensors_count": 1,
                "co2_sensors_count": 0,
                "pressure_sensors_count": 0,
                "mold_sensors_count": 0,
            },
        },
    }
    return coord


class TestGetCoordinator:
    def test_returns_coordinator_when_present(self):
        hass = MagicMock()
        coord = _make_coordinator()
        hass.data = {DOMAIN: {"entry_1": coord}}
        result = _get_coordinator(hass)
        assert result is coord

    def test_returns_none_when_domain_missing(self):
        hass = MagicMock()
        hass.data = {}
        result = _get_coordinator(hass)
        assert result is None

    def test_returns_none_when_no_data_attr(self):
        hass = MagicMock()
        hass.data = {DOMAIN: {"entry_1": MagicMock(spec=[])}}
        result = _get_coordinator(hass)
        assert result is None


class TestWsGetClimateData:
    def _call(self, hass, coord=None):
        connection = MagicMock()
        msg = {"id": 1}
        if coord:
            hass.data = {DOMAIN: {"e1": coord}}
        ws_get_climate_data(hass, connection, msg)
        return connection

    def test_sends_result_with_severity(self):
        hass = MagicMock()
        coord = _make_coordinator()
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        conn.send_result.assert_called_once()
        result = conn.send_result.call_args[0][1]
        assert result["severity"] == 15.0

    def test_sends_result_with_rooms(self):
        hass = MagicMock()
        coord = _make_coordinator()
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        result = conn.send_result.call_args[0][1]
        assert result["room_count"] == 2
        room_names = [r["name"] for r in result["rooms"]]
        assert "Stue" in room_names
        assert "Soveværelse" in room_names

    def test_rooms_sorted_critical_first(self):
        hass = MagicMock()
        rooms_data = {
            "Stue": {"status": "good", "severity": 5.0, "temperature": None, "humidity": None,
                     "co2": None, "pressure": None, "outdoor_windows_open": 0, "internal_doors_open": 0,
                     "temperature_sensors_count": 0, "humidity_sensors_count": 0,
                     "co2_sensors_count": 0, "pressure_sensors_count": 0},
            "Køkken": {"status": "critical", "severity": 75.0, "temperature": None, "humidity": None,
                       "co2": None, "pressure": None, "outdoor_windows_open": 0, "internal_doors_open": 0,
                       "temperature_sensors_count": 0, "humidity_sensors_count": 0,
                       "co2_sensors_count": 0, "pressure_sensors_count": 0},
        }
        coord = _make_coordinator(rooms_data=rooms_data)
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        result = conn.send_result.call_args[0][1]
        assert result["rooms"][0]["name"] == "Køkken"

    def test_sends_error_when_no_coordinator(self):
        hass = MagicMock()
        hass.data = {}
        conn = self._call(hass)
        conn.send_error.assert_called_once()

    def test_weather_configured_field(self):
        hass = MagicMock()
        coord = _make_coordinator()
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        result = conn.send_result.call_args[0][1]
        assert result["ventilation"]["weather_configured"] is True

    def test_weather_not_configured(self):
        hass = MagicMock()
        coord = _make_coordinator()
        coord.weather_entity = None
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        result = conn.send_result.call_args[0][1]
        assert result["ventilation"]["weather_configured"] is False

    def test_mold_risk_in_result(self):
        hass = MagicMock()
        coord = _make_coordinator()
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        result = conn.send_result.call_args[0][1]
        assert "mold_risk" in result
        assert result["mold_risk"] == "low"

    def test_dehumidifier_recommendation_in_result(self):
        hass = MagicMock()
        coord = _make_coordinator()
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        result = conn.send_result.call_args[0][1]
        assert "dehumidifier_recommendation" in result
        assert result["dehumidifier_recommendation"] == "no"

    def test_room_has_mold_risk_field(self):
        hass = MagicMock()
        coord = _make_coordinator()
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        result = conn.send_result.call_args[0][1]
        stue = next(r for r in result["rooms"] if r["name"] == "Stue")
        assert stue["mold_risk"] == "low"

    def test_room_has_dehumidifier_recommendation_field(self):
        hass = MagicMock()
        coord = _make_coordinator()
        hass.data = {DOMAIN: {"e1": coord}}
        conn = self._call(hass, coord)
        result = conn.send_result.call_args[0][1]
        sovevaer = next(r for r in result["rooms"] if r["name"] == "Soveværelse")
        assert sovevaer["dehumidifier_recommendation"] == "optional"


class TestWsGetRoomData:
    def _call(self, hass, coord, room_name):
        connection = MagicMock()
        msg = {"id": 1, "room_name": room_name}
        hass.data = {DOMAIN: {"e1": coord}}
        ws_get_room_data(hass, connection, msg)
        return connection

    def test_returns_room_data(self):
        hass = MagicMock()
        coord = _make_coordinator()
        conn = self._call(hass, coord, "Stue")
        conn.send_result.assert_called_once()
        result = conn.send_result.call_args[0][1]
        assert result["name"] == "Stue"
        assert result["severity"] == 10.0

    def test_unknown_room_sends_error(self):
        hass = MagicMock()
        coord = _make_coordinator()
        conn = self._call(hass, coord, "Nonexistent")
        conn.send_error.assert_called_once()

    def test_no_coordinator_sends_error(self):
        hass = MagicMock()
        hass.data = {}
        connection = MagicMock()
        msg = {"id": 1, "room_name": "Stue"}
        ws_get_room_data(hass, connection, msg)
        connection.send_error.assert_called_once()

    def test_room_data_has_mold_risk(self):
        hass = MagicMock()
        coord = _make_coordinator()
        conn = self._call(hass, coord, "Stue")
        result = conn.send_result.call_args[0][1]
        assert "mold_risk" in result
        assert result["mold_risk"] == "low"

    def test_room_data_has_dehumidifier_recommendation(self):
        hass = MagicMock()
        coord = _make_coordinator()
        conn = self._call(hass, coord, "Soveværelse")
        result = conn.send_result.call_args[0][1]
        assert "dehumidifier_recommendation" in result
        assert result["dehumidifier_recommendation"] == "optional"


# ── Regression guard: websocket must forward the historical bug fields ─────
#
# dehumidifier_mode, kritisk_siden and led_alarm_active were all computed
# correctly by the coordinator but silently missing from both websocket
# payloads before v2.9.0 (invisible to the panel/cards despite being correct
# in coordinator.data). These fields are the direct regression case.

class TestHistoricalBugFieldsAreForwarded:
    def _room_with_alarm_fields(self):
        return {
            "status": "critical",
            "severity": 72.0,
            "temperature": 24.0,
            "humidity": 78.0,
            "co2": 1800.0,
            "pressure": 1005.0,
            "mold_risk": "high",
            "dehumidifier_recommendation": "yes",
            "dehumidifier_mode": "auto",
            "kritisk_siden": "2026-07-10T08:15:00+00:00",
            "led_alarm_active": True,
            "has_dehumidifier": True,
            "outdoor_windows_open": 0,
            "internal_doors_open": 0,
            "temperature_sensors_count": 1,
            "humidity_sensors_count": 1,
            "co2_sensors_count": 1,
            "pressure_sensors_count": 1,
            "mold_sensors_count": 0,
        }

    def test_climate_data_forwards_alarm_fields(self):
        hass = MagicMock()
        coord = _make_coordinator(rooms_data={"Bryggers": self._room_with_alarm_fields()})
        hass.data = {DOMAIN: {"e1": coord}}
        connection = MagicMock()
        ws_get_climate_data(hass, connection, {"id": 1})
        result = connection.send_result.call_args[0][1]
        room = next(r for r in result["rooms"] if r["name"] == "Bryggers")
        assert room["dehumidifier_mode"] == "auto"
        assert room["kritisk_siden"] == "2026-07-10T08:15:00+00:00"
        assert room["led_alarm_active"] is True

    def test_room_data_forwards_alarm_fields(self):
        hass = MagicMock()
        coord = _make_coordinator(rooms_data={"Bryggers": self._room_with_alarm_fields()})
        hass.data = {DOMAIN: {"e1": coord}}
        connection = MagicMock()
        ws_get_room_data(hass, connection, {"id": 1, "room_name": "Bryggers"})
        result = connection.send_result.call_args[0][1]
        assert result["dehumidifier_mode"] == "auto"
        assert result["kritisk_siden"] == "2026-07-10T08:15:00+00:00"
        assert result["led_alarm_active"] is True


# ── Future-proofing: diff the REAL coordinator output against what the ──────
# websocket handlers expose, instead of a hand-maintained fixture list.
#
# This is the guard the historical bug actually needed: a hand-written test
# fixture (like the one above, and the one `_make_coordinator()` uses) can
# drift out of sync with the real coordinator just as easily as websocket.py
# did. Calling the real `_process_room()` and diffing its keys against the
# websocket payload keys means a *newly added* coordinator field that isn't
# forwarded will fail CI immediately, without anyone having to remember to
# update this test by hand.

class TestWebsocketCoversRealCoordinatorFields:
    def _make_real_coordinator(self, hass, entry):
        from custom_components.indeklima import IndeklimaDataCoordinator
        with patch(
            "custom_components.indeklima.DataUpdateCoordinator.__init__",
            return_value=None,
        ):
            coord = IndeklimaDataCoordinator.__new__(IndeklimaDataCoordinator)
            coord.hass = hass
            coord.entry = entry
            coord.rooms = []
            coord.humidity_summer_max = 60
            coord.humidity_winter_max = 55
            coord.co2_max = 1000
            coord.voc_max = 3.0
            coord.formaldehyde_max = 0.15
            coord.weather_entity = None
            coord.history = {"humidity": [], "co2": [], "severity": []}
            coord._dehumidifier_state = {}
            coord._room_critical_since = {}
            return coord

    def _real_room_data(self):
        """Run the actual coordinator `_process_room()` for a fully-sensored
        room (no dehumidifier/LED configured, to keep this test focused on
        sensor/status/mold fields rather than the async LED-blink machinery,
        which has its own dedicated coverage in test_coordinator.py)."""
        from custom_components.indeklima.const import (
            CONF_HUMIDITY_SENSORS,
            CONF_TEMPERATURE_SENSORS,
            CONF_CO2_SENSORS,
            CONF_PRESSURE_SENSORS,
            CONF_MOLD_SENSORS,
        )

        hass = MagicMock()
        states = {
            "sensor.stue_humidity": "45",
            "sensor.stue_temperature": "21",
            "sensor.stue_co2": "600",
            "sensor.stue_pressure": "1013",
            "sensor.stue_mold": "45",
        }

        def _get_state(entity_id):
            state = MagicMock()
            state.state = states.get(entity_id, "unavailable")
            return state

        hass.states.get.side_effect = _get_state
        entry = MagicMock()
        coord = self._make_real_coordinator(hass, entry)

        room = {
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: ["sensor.stue_humidity"],
            CONF_TEMPERATURE_SENSORS: ["sensor.stue_temperature"],
            CONF_CO2_SENSORS: ["sensor.stue_co2"],
            CONF_PRESSURE_SENSORS: ["sensor.stue_pressure"],
            CONF_MOLD_SENSORS: ["sensor.stue_mold"],
        }
        data = {"open_windows": [], "open_internal_doors": []}

        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            room_data = coord._process_room(room, data)

        coord.data = {
            "severity": room_data["severity"],
            "status": room_data["status"],
            "open_windows": [],
            "open_internal_doors": [],
            "air_circulation": "poor",
            "averages": {},
            "mold_risk": room_data.get("mold_risk", "low"),
            "dehumidifier_recommendation": "no",
            "trends": {"humidity": "stable", "co2": "stable", "severity": "stable"},
            "ventilation": {"status": "no", "reason": [], "rooms": [], "outdoor_temp": None, "outdoor_humidity": None},
            "rooms": {"Stue": room_data},
        }
        return coord, room_data

    def test_climate_data_summary_covers_all_real_fields(self):
        # mold_humidity is deliberately hub/detail-only -- it is not part of
        # the per-room summary list used for the room overview/sorting.
        excluded = {"mold_humidity"}

        coord, room_data = self._real_room_data()
        hass = MagicMock()
        hass.data = {DOMAIN: {"e1": coord}}
        connection = MagicMock()
        ws_get_climate_data(hass, connection, {"id": 1})
        result = connection.send_result.call_args[0][1]
        room_out = next(r for r in result["rooms"] if r["name"] == "Stue")

        for key in room_data:
            if key in excluded:
                continue
            assert key in room_out, (
                f"Coordinator field '{key}' from _process_room() is not exposed "
                f"in ws_get_climate_data's room summary -- update websocket.py"
            )

    def test_room_data_detail_covers_all_real_fields(self):
        coord, room_data = self._real_room_data()
        hass = MagicMock()
        hass.data = {DOMAIN: {"e1": coord}}
        connection = MagicMock()
        ws_get_room_data(hass, connection, {"id": 1, "room_name": "Stue"})
        result = connection.send_result.call_args[0][1]

        for key in room_data:
            assert key in result, (
                f"Coordinator field '{key}' from _process_room() is not exposed "
                f"in ws_get_room_data -- update websocket.py"
            )
