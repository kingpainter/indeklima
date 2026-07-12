"""Tests for diagnostics.py."""
from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock
import pytest

from custom_components.indeklima.diagnostics import (
    async_get_config_entry_diagnostics,
    async_get_device_diagnostics,
    _get_coordinator,
)
from custom_components.indeklima.const import DOMAIN, __version__
from .conftest import mock_hass, mock_entry, make_state, ENTRY_DATA, ENTRY_OPTIONS


def _make_hass_with_states(state_map: dict):
    hass = MagicMock()
    hass.data = {}

    def get_state(entity_id):
        val = state_map.get(entity_id)
        if val is None:
            return None
        return make_state(str(val))

    hass.states.get.side_effect = get_state
    return hass


def _make_coordinator_with_data():
    coord = MagicMock()
    coord.data = {
        "severity": 15.0,
        "status": "good",
        "air_circulation": "moderate",
        "open_windows": [],
        "open_internal_doors": [],
        "averages": {"humidity": 45.0, "temperature": 22.0},
        "trends": {"humidity": "stable"},
        "ventilation": {"status": "no"},
        "rooms": {
            "Stue": {
                "status": "good",
                "severity": 15.0,
                "temperature": 22.0,
                "humidity": 45.0,
                "co2": 400.0,
                "pressure": 1013.0,
                "outdoor_windows_open": 0,
                "internal_doors_open": 0,
            }
        },
    }
    coord.last_update_success = True
    return coord


class TestGetCoordinator:
    def test_returns_coordinator(self):
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "e1"
        coord = MagicMock()
        coord.data = {}
        coord.rooms = []
        hass.data = {DOMAIN: {"e1": coord}}
        result = _get_coordinator(hass, entry)
        assert result is coord

    def test_returns_none_when_missing(self):
        hass = MagicMock()
        entry = MagicMock()
        entry.entry_id = "e1"
        hass.data = {}
        result = _get_coordinator(hass, entry)
        assert result is None


class TestAsyncGetConfigEntryDiagnostics:
    @pytest.mark.asyncio
    async def test_returns_dict_with_version(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({
            "sensor.stue_humidity": "45.0",
            "sensor.stue_temperature": "22.0",
            "sensor.stue_co2": "400.0",
            "sensor.stue_pressure": "1013.0",
        })
        coord = _make_coordinator_with_data()
        hass.data = {DOMAIN: {mock_entry.entry_id: coord}}

        result = await async_get_config_entry_diagnostics(hass, mock_entry)

        assert "integration_version" in result
        # Compare against the real const.__version__ rather than a hardcoded
        # string, so this test doesn't go stale on every version bump -- it
        # verifies diagnostics correctly surfaces whatever the current
        # version is, not that the version equals a specific pinned number.
        assert result["integration_version"] == __version__

    @pytest.mark.asyncio
    async def test_returns_sensor_availability(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({
            "sensor.stue_humidity": "45.0",
        })
        coord = _make_coordinator_with_data()
        hass.data = {DOMAIN: {mock_entry.entry_id: coord}}

        result = await async_get_config_entry_diagnostics(hass, mock_entry)

        assert "sensor_availability" in result
        stue = result["sensor_availability"].get("Stue", {})
        assert "humidity_sensors" in stue

    @pytest.mark.asyncio
    async def test_unavailable_sensor_marked_false(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({})  # all sensors None/unavailable
        coord = _make_coordinator_with_data()
        hass.data = {DOMAIN: {mock_entry.entry_id: coord}}

        result = await async_get_config_entry_diagnostics(hass, mock_entry)

        stue = result["sensor_availability"]["Stue"]
        for sensor in stue.get("humidity_sensors", []):
            assert sensor["available"] is False

    @pytest.mark.asyncio
    async def test_live_data_included(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({})
        coord = _make_coordinator_with_data()
        hass.data = {DOMAIN: {mock_entry.entry_id: coord}}

        result = await async_get_config_entry_diagnostics(hass, mock_entry)

        assert "live_data" in result
        assert result["live_data"]["severity"] == 15.0

    @pytest.mark.asyncio
    async def test_no_coordinator_gives_empty_live_data(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({})
        hass.data = {}

        result = await async_get_config_entry_diagnostics(hass, mock_entry)

        assert result["live_data"] == {}


class TestAsyncGetDeviceDiagnostics:
    def _make_hub_device(self, entry_id):
        device = MagicMock()
        device.identifiers = {("indeklima", f"{entry_id}_hub")}
        device.sw_version = "2.4.1"
        return device

    def _make_room_device(self, entry_id, room_id):
        device = MagicMock()
        device.identifiers = {("indeklima", f"{entry_id}_room_{room_id}")}
        device.sw_version = "2.4.1"
        return device

    @pytest.mark.asyncio
    async def test_hub_device_returns_hub_type(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({})
        coord = _make_coordinator_with_data()
        hass.data = {DOMAIN: {mock_entry.entry_id: coord}}
        device = self._make_hub_device(mock_entry.entry_id)

        result = await async_get_device_diagnostics(hass, mock_entry, device)

        assert result["device_type"] == "hub"
        assert "live_data" in result

    @pytest.mark.asyncio
    async def test_hub_device_includes_room_summary(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({})
        coord = _make_coordinator_with_data()
        hass.data = {DOMAIN: {mock_entry.entry_id: coord}}
        device = self._make_hub_device(mock_entry.entry_id)

        result = await async_get_device_diagnostics(hass, mock_entry, device)

        assert "rooms_by_status" in result["live_data"]

    @pytest.mark.asyncio
    async def test_room_device_returns_room_type(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({})
        coord = _make_coordinator_with_data()
        hass.data = {DOMAIN: {mock_entry.entry_id: coord}}
        device = self._make_room_device(mock_entry.entry_id, "stue")

        result = await async_get_device_diagnostics(hass, mock_entry, device)

        assert result["device_type"] == "room"
        assert result["room_name"] == "Stue"

    @pytest.mark.asyncio
    async def test_unknown_room_returns_error(self, mock_hass, mock_entry):
        hass = _make_hass_with_states({})
        coord = _make_coordinator_with_data()
        hass.data = {DOMAIN: {mock_entry.entry_id: coord}}
        device = self._make_room_device(mock_entry.entry_id, "nonexistent_room")

        result = await async_get_device_diagnostics(hass, mock_entry, device)

        assert "error" in result
