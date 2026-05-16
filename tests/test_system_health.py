"""Tests for system_health.py."""
from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock
import pytest

from custom_components.indeklima.system_health import async_system_health_info
from custom_components.indeklima.const import DOMAIN, __version__
from .conftest import mock_hass, make_state, ROOM_STUE


def _make_coordinator(data=None, rooms=None, weather_entity=None, last_update_success=True):
    coord = MagicMock()
    coord.data = data or {
        "severity": 15.0,
        "status": "good",
        "air_circulation": "moderate",
        "ventilation": {"status": "no"},
        "rooms": {
            "Stue": {"status": "good", "severity": 15.0},
        },
    }
    coord.rooms = rooms or [ROOM_STUE]
    coord.weather_entity = weather_entity
    coord.last_update_success = last_update_success
    return coord


class TestAsyncSystemHealthInfo:
    @pytest.mark.asyncio
    async def test_no_coordinator_returns_minimal(self, mock_hass):
        mock_hass.data = {}
        result = await async_system_health_info(mock_hass)
        assert result["integration_version"] == __version__
        assert result["config_entries"] == 0
        assert result["coordinator_status"] == "not_loaded"

    @pytest.mark.asyncio
    async def test_returns_version(self, mock_hass):
        coord = _make_coordinator()
        mock_hass.data = {DOMAIN: {"e1": coord}}
        mock_hass.states.get.return_value = make_state("45.0")
        result = await async_system_health_info(mock_hass)
        assert result["integration_version"] == __version__

    @pytest.mark.asyncio
    async def test_coordinator_ok_status(self, mock_hass):
        coord = _make_coordinator(last_update_success=True)
        mock_hass.data = {DOMAIN: {"e1": coord}}
        mock_hass.states.get.return_value = make_state("45.0")
        result = await async_system_health_info(mock_hass)
        assert result["coordinator_status"] == "ok"

    @pytest.mark.asyncio
    async def test_coordinator_failed_status(self, mock_hass):
        coord = _make_coordinator(last_update_success=False)
        mock_hass.data = {DOMAIN: {"e1": coord}}
        mock_hass.states.get.return_value = make_state("45.0")
        result = await async_system_health_info(mock_hass)
        assert result["coordinator_status"] == "update_failed"

    @pytest.mark.asyncio
    async def test_counts_rooms(self, mock_hass):
        coord = _make_coordinator()
        mock_hass.data = {DOMAIN: {"e1": coord}}
        mock_hass.states.get.return_value = make_state("45.0")
        result = await async_system_health_info(mock_hass)
        assert result["rooms_monitored"] == 1

    @pytest.mark.asyncio
    async def test_counts_unavailable_sensors(self, mock_hass):
        coord = _make_coordinator()
        mock_hass.data = {DOMAIN: {"e1": coord}}
        mock_hass.states.get.return_value = None  # all unavailable
        result = await async_system_health_info(mock_hass)
        assert result["sensors_unavailable"] > 0

    @pytest.mark.asyncio
    async def test_weather_configured_yes(self, mock_hass):
        coord = _make_coordinator(weather_entity="weather.home")
        mock_hass.data = {DOMAIN: {"e1": coord}}
        mock_hass.states.get.return_value = make_state("45.0")
        result = await async_system_health_info(mock_hass)
        assert result["weather_configured"] == "yes"

    @pytest.mark.asyncio
    async def test_weather_configured_no(self, mock_hass):
        coord = _make_coordinator(weather_entity=None)
        mock_hass.data = {DOMAIN: {"e1": coord}}
        mock_hass.states.get.return_value = make_state("45.0")
        result = await async_system_health_info(mock_hass)
        assert result["weather_configured"] == "no"

    @pytest.mark.asyncio
    async def test_critical_rooms_counted(self, mock_hass):
        coord = _make_coordinator(data={
            "severity": 70.0,
            "status": "critical",
            "air_circulation": "poor",
            "ventilation": {"status": "yes"},
            "rooms": {
                "Stue": {"status": "critical", "severity": 70.0},
                "Køkken": {"status": "good", "severity": 5.0},
            },
        })
        mock_hass.data = {DOMAIN: {"e1": coord}}
        mock_hass.states.get.return_value = make_state("45.0")
        result = await async_system_health_info(mock_hass)
        assert result["rooms_critical"] == 1
        assert result["rooms_warning"] == 0
