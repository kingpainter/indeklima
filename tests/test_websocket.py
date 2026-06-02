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
