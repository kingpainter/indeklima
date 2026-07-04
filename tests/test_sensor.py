"""Tests for the mold_risk / dehumidifier_recommendation sensor entities.

Mold risk is a CALCULATED value (outdoor/room temperature + the room's own
humidity sensor) — it is not backed by a physical mold sensor, so these
entities are always created regardless of sensor configuration (see
sensor.py::async_setup_entry).
"""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from custom_components.indeklima.sensor import (
    IndeklimaGlobalSensor,
    IndeklimaRoomMetricSensor,
    IndeklimaRoomSensor,
)
from custom_components.indeklima.const import (
    SENSOR_TYPES,
    ROOM_SENSOR_TYPES,
    MOLD_RISK_LOW,
    MOLD_RISK_HIGH,
    DEHUMIDIFIER_NO,
    DEHUMIDIFIER_YES,
    DEHUM_MODE_AUTO,
)
from .conftest import mock_hass, mock_entry  # noqa: F401  (fixtures)


def _make_global_sensor(entry, sensor_type, coordinator_data=None):
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    return IndeklimaGlobalSensor(coordinator, entry, sensor_type, SENSOR_TYPES[sensor_type])


def _make_room_metric_sensor(entry, room_name, sensor_type, coordinator_data=None):
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    room_id = room_name.lower()
    return IndeklimaRoomMetricSensor(coordinator, entry, room_name, room_id, sensor_type)


def _make_room_status_sensor(entry, room_name, coordinator_data=None):
    coordinator = MagicMock()
    coordinator.data = coordinator_data
    room_id = room_name.lower()
    return IndeklimaRoomSensor(coordinator, entry, room_name, room_id, "status")


class TestRoomStatusSensorKritiskSiden:
    """kritisk_siden attribute on the room status sensor (v2.7.0+)."""

    def test_kritisk_siden_present_when_critical(self, mock_entry):
        data = {"rooms": {"Bad": {"status": "critical", "kritisk_siden": "2026-07-04T12:00:00"}}}
        sensor = _make_room_status_sensor(mock_entry, "Bad", coordinator_data=data)
        assert sensor.extra_state_attributes["kritisk_siden"] == "2026-07-04T12:00:00"

    def test_kritisk_siden_absent_when_not_critical(self, mock_entry):
        data = {"rooms": {"Bad": {"status": "good"}}}
        sensor = _make_room_status_sensor(mock_entry, "Bad", coordinator_data=data)
        assert "kritisk_siden" not in sensor.extra_state_attributes


class TestGlobalMoldRiskSensor:
    """sensor_type == 'mold_risk_avg' (hub-level, worst-room mold risk)."""

    def test_no_coordinator_data_returns_none(self, mock_entry):
        sensor = _make_global_sensor(mock_entry, "mold_risk_avg", coordinator_data=None)
        assert sensor.native_value is None

    def test_returns_mold_risk_from_coordinator_data(self, mock_entry):
        sensor = _make_global_sensor(
            mock_entry, "mold_risk_avg", coordinator_data={"mold_risk": MOLD_RISK_HIGH}
        )
        assert sensor.native_value == MOLD_RISK_HIGH

    def test_missing_mold_risk_key_defaults_to_low(self, mock_entry):
        sensor = _make_global_sensor(mock_entry, "mold_risk_avg", coordinator_data={})
        assert sensor.native_value == MOLD_RISK_LOW

    def test_unique_id_and_device_link(self, mock_entry):
        sensor = _make_global_sensor(mock_entry, "mold_risk_avg", coordinator_data={})
        assert sensor._attr_unique_id == f"{mock_entry.entry_id}_mold_risk_avg"
        assert sensor._attr_device_info["identifiers"] == {
            ("indeklima", f"{mock_entry.entry_id}_hub")
        }


class TestRoomMoldRiskSensor:
    """sensor_type == 'mold_risk' (per-room, always created)."""

    def test_no_coordinator_data_returns_none(self, mock_entry):
        sensor = _make_room_metric_sensor(mock_entry, "Stue", "mold_risk", coordinator_data=None)
        assert sensor.native_value is None

    def test_returns_room_mold_risk_as_is(self, mock_entry):
        data = {"rooms": {"Stue": {"mold_risk": MOLD_RISK_HIGH}}}
        sensor = _make_room_metric_sensor(mock_entry, "Stue", "mold_risk", coordinator_data=data)
        # String states are returned as-is, not rounded like numeric metrics
        assert sensor.native_value == MOLD_RISK_HIGH

    def test_room_missing_from_data_returns_none(self, mock_entry):
        data = {"rooms": {}}
        sensor = _make_room_metric_sensor(mock_entry, "Stue", "mold_risk", coordinator_data=data)
        assert sensor.native_value is None

    def test_no_sensor_count_attribute_for_calculated_value(self, mock_entry):
        """Mold risk has no dedicated physical sensor by default, so no
        'sensorer_brugt' attribute unless mold_sensors_count is present."""
        data = {"rooms": {"Stue": {"mold_risk": MOLD_RISK_LOW}}}
        sensor = _make_room_metric_sensor(mock_entry, "Stue", "mold_risk", coordinator_data=data)
        assert "sensorer_brugt" not in sensor.extra_state_attributes

    def test_sensor_count_attribute_present_with_dedicated_mold_sensor(self, mock_entry):
        """Regression test for fixed bug (2026-07-04): the mold_risk sensor's
        'sensorer_brugt' attribute must read the coordinator's actual
        'mold_sensors_count' key, not the generic f'{sensor_type}_sensors_count'
        pattern used by other metrics."""
        data = {"rooms": {"Stue": {"mold_risk": MOLD_RISK_HIGH, "mold_sensors_count": 1}}}
        sensor = _make_room_metric_sensor(mock_entry, "Stue", "mold_risk", coordinator_data=data)
        assert sensor.extra_state_attributes["sensorer_brugt"] == 1


class TestRoomDehumidifierRecommendationSensor:
    """sensor_type == 'dehumidifier_recommendation' (per-room, always created)."""

    def test_returns_recommendation_as_is(self, mock_entry):
        data = {"rooms": {"Bad": {"dehumidifier_recommendation": DEHUMIDIFIER_YES}}}
        sensor = _make_room_metric_sensor(
            mock_entry, "Bad", "dehumidifier_recommendation", coordinator_data=data
        )
        assert sensor.native_value == DEHUMIDIFIER_YES

    def test_defaults_handled_when_key_missing(self, mock_entry):
        data = {"rooms": {"Bad": {}}}
        sensor = _make_room_metric_sensor(
            mock_entry, "Bad", "dehumidifier_recommendation", coordinator_data=data
        )
        assert sensor.native_value is None

    def test_tilstand_attribute_reflects_dehumidifier_mode(self, mock_entry):
        data = {
            "rooms": {
                "Bad": {
                    "dehumidifier_recommendation": DEHUMIDIFIER_YES,
                    "dehumidifier_mode": DEHUM_MODE_AUTO,
                }
            }
        }
        sensor = _make_room_metric_sensor(
            mock_entry, "Bad", "dehumidifier_recommendation", coordinator_data=data
        )
        assert sensor.extra_state_attributes["tilstand"] == DEHUM_MODE_AUTO

    def test_no_tilstand_attribute_without_dehumidifier_mode(self, mock_entry):
        data = {"rooms": {"Bad": {"dehumidifier_recommendation": DEHUMIDIFIER_NO}}}
        sensor = _make_room_metric_sensor(
            mock_entry, "Bad", "dehumidifier_recommendation", coordinator_data=data
        )
        assert "tilstand" not in sensor.extra_state_attributes
