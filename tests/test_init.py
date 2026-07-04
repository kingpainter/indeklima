"""Tests for IndeklimaDataCoordinator in __init__.py."""
from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, patch, AsyncMock
import pytest

from custom_components.indeklima.const import (
    STATUS_GOOD,
    STATUS_WARNING,
    STATUS_CRITICAL,
    TREND_RISING,
    TREND_FALLING,
    TREND_STABLE,
    SEASON_SUMMER,
    SEASON_WINTER,
    CIRCULATION_GOOD,
    CIRCULATION_MODERATE,
    CIRCULATION_POOR,
    VENTILATION_YES,
    VENTILATION_NO,
    VENTILATION_OPTIONAL,
)
from .conftest import make_state, mock_hass, mock_entry


def _make_coord(hass, entry, rooms=None, weather_entity=None):
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
        coord.weather_entity = weather_entity
        coord.history = {"humidity": [], "co2": [], "severity": []}
        return coord


class TestGetSeason:
    def test_summer_months(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        for month in [5, 6, 7, 8, 9]:
            with patch("custom_components.indeklima.dt_util") as mock_dt:
                mock_dt.now.return_value = MagicMock(month=month)
                assert coord._get_season() == SEASON_SUMMER

    def test_winter_months(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        for month in [1, 2, 3, 4, 10, 11, 12]:
            with patch("custom_components.indeklima.dt_util") as mock_dt:
                mock_dt.now.return_value = MagicMock(month=month)
                assert coord._get_season() == SEASON_WINTER


class TestCalculateSeverity:
    def test_perfect_conditions(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_severity({"humidity": 45, "co2": 500}) == 0.0

    def test_high_humidity_adds_points(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_severity({"humidity": 70}) > 0

    def test_high_co2_adds_points(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_severity({"co2": 2000}) > 0

    def test_high_voc_adds_points(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_severity({"voc": 5.0}) > 0

    def test_high_formaldehyde_adds_points(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_severity({"formaldehyde": 0.5}) > 0

    def test_pressure_does_not_affect_severity(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        s1 = coord._calculate_severity({"humidity": 45})
        s2 = coord._calculate_severity({"humidity": 45, "pressure": 1100})
        assert s1 == s2

    def test_severity_capped_at_100(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_severity({
            "humidity": 100, "co2": 5000, "voc": 10.0, "formaldehyde": 1.0,
        }) <= 100.0

    def test_severity_never_negative(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_severity({}) >= 0.0


class TestGetStatusFromSeverity:
    def test_good(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._get_status_from_severity(0) == STATUS_GOOD
        assert coord._get_status_from_severity(29) == STATUS_GOOD

    def test_warning(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._get_status_from_severity(30) == STATUS_WARNING
        assert coord._get_status_from_severity(59) == STATUS_WARNING

    def test_critical(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._get_status_from_severity(60) == STATUS_CRITICAL
        assert coord._get_status_from_severity(100) == STATUS_CRITICAL


class TestCalculateTrend:
    def test_single_point_is_stable(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        assert coord._calculate_trend("humidity", 50.0) == TREND_STABLE

    def test_rising_trend(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        coord._calculate_trend("humidity", 30.0)
        coord._calculate_trend("humidity", 50.0)
        assert coord._calculate_trend("humidity", 80.0) == TREND_RISING

    def test_falling_trend(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        coord._calculate_trend("humidity", 80.0)
        coord._calculate_trend("humidity", 55.0)
        assert coord._calculate_trend("humidity", 20.0) == TREND_FALLING

    def test_stable_trend(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        coord._calculate_trend("humidity", 50.0)
        coord._calculate_trend("humidity", 50.0)
        assert coord._calculate_trend("humidity", 50.0) == TREND_STABLE

    def test_denominator_zero_returns_stable(self, mock_hass, mock_entry):
        from datetime import timezone
        coord = _make_coord(mock_hass, mock_entry)
        # Use timezone-aware datetime to match dt_util.utcnow() output
        now = datetime(2026, 5, 15, 12, 0, 0, tzinfo=timezone.utc)
        coord.history["co2"] = [(now, 500.0), (now, 500.0)]
        with patch("custom_components.indeklima.dt_util") as mock_dt:
            mock_dt.utcnow.return_value = now
            result = coord._calculate_trend("co2", 500.0)
        assert result == TREND_STABLE


class TestAirCirculation:
    def test_no_doors_poor(self, mock_hass, mock_entry):
        assert _make_coord(mock_hass, mock_entry)._calculate_air_circulation(0) == CIRCULATION_POOR

    def test_one_door_moderate(self, mock_hass, mock_entry):
        assert _make_coord(mock_hass, mock_entry)._calculate_air_circulation(1) == CIRCULATION_MODERATE

    def test_two_doors_moderate(self, mock_hass, mock_entry):
        assert _make_coord(mock_hass, mock_entry)._calculate_air_circulation(2) == CIRCULATION_MODERATE

    def test_three_doors_good(self, mock_hass, mock_entry):
        assert _make_coord(mock_hass, mock_entry)._calculate_air_circulation(3) == CIRCULATION_GOOD

    def test_many_doors_good(self, mock_hass, mock_entry):
        assert _make_coord(mock_hass, mock_entry)._calculate_air_circulation(10) == CIRCULATION_GOOD


class TestGetSensorValues:
    def test_available_sensor_returns_value(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None  # reset fixture default
        mock_hass.states.get.return_value = make_state("42.5")
        coord = _make_coord(mock_hass, mock_entry)
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"), \
             patch("custom_components.indeklima.raise_sensor_unavailable_issue") as mock_raise:
            values = coord._get_sensor_values(["sensor.test"], "Stue")
        assert values == [42.5]
        mock_raise.assert_not_called()

    def test_unavailable_sensor_returns_empty(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("unavailable", unavailable=True)
        coord = _make_coord(mock_hass, mock_entry)
        with patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            values = coord._get_sensor_values(["sensor.test"], "Stue")
        assert values == []

    def test_none_state_returns_empty(self, mock_hass, mock_entry):
        # fixture default: side_effect returns None — no change needed
        coord = _make_coord(mock_hass, mock_entry)
        with patch("custom_components.indeklima.raise_sensor_unavailable_issue"):
            values = coord._get_sensor_values(["sensor.test"], "Stue")
        assert values == []

    def test_multiple_sensors(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        def get_state(entity_id):
            return make_state("40.0") if "a" in entity_id else make_state("60.0")
        mock_hass.states.get.side_effect = get_state
        coord = _make_coord(mock_hass, mock_entry)
        with patch("custom_components.indeklima.clear_sensor_unavailable_issue"):
            values = coord._get_sensor_values(["sensor.a", "sensor.b"], "Stue")
        assert values == [40.0, 60.0]

    def test_no_room_name_skips_repair(self, mock_hass, mock_entry):
        # fixture default returns None — no change needed
        coord = _make_coord(mock_hass, mock_entry)
        with patch("custom_components.indeklima.raise_sensor_unavailable_issue") as mock_raise:
            coord._get_sensor_values(["sensor.test"])
        mock_raise.assert_not_called()


class TestGetWeatherData:
    def test_no_weather_entity_returns_empty(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry, weather_entity=None)
        assert coord._get_weather_data() == {}

    def test_unavailable_entity_returns_empty(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        mock_hass.states.get.return_value = make_state("unavailable", unavailable=True)
        coord = _make_coord(mock_hass, mock_entry, weather_entity="weather.home")
        assert coord._get_weather_data() == {}

    def test_none_state_returns_empty(self, mock_hass, mock_entry):
        # fixture default returns None
        coord = _make_coord(mock_hass, mock_entry, weather_entity="weather.home")
        assert coord._get_weather_data() == {}

    def test_returns_temperature_and_humidity(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        state = MagicMock()
        state.state = "sunny"
        state.attributes = {"temperature": 15.0, "humidity": 70.0}
        mock_hass.states.get.return_value = state
        coord = _make_coord(mock_hass, mock_entry, weather_entity="weather.home")
        data = coord._get_weather_data()
        assert data["temperature"] == 15.0
        assert data["humidity"] == 70.0

    def test_falls_back_to_current_temperature(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        state = MagicMock()
        state.state = "sunny"
        state.attributes = {"current_temperature": 12.0}
        mock_hass.states.get.return_value = state
        coord = _make_coord(mock_hass, mock_entry, weather_entity="weather.home")
        data = coord._get_weather_data()
        assert data["temperature"] == 12.0


class TestCalculateVentilationRecommendation:
    def _good_data(self):
        return {
            "open_windows": [],
            "rooms": {"Stue": {"humidity": 45.0, "co2": 500.0}},
        }

    def _bad_data(self):
        return {
            "open_windows": [],
            "rooms": {"Stue": {"humidity": 75.0, "co2": 1500.0}},
        }

    def test_good_climate_returns_no(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.states.get.return_value = None  # no weather
        result = coord._calculate_ventilation_recommendation(self._good_data())
        assert result["status"] == VENTILATION_NO

    def test_open_windows_returns_optional(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        data = {"open_windows": ["Stue"], "rooms": {}}
        result = coord._calculate_ventilation_recommendation(data)
        assert result["status"] == VENTILATION_OPTIONAL

    def test_bad_climate_no_weather_returns_yes(self, mock_hass, mock_entry):
        coord = _make_coord(mock_hass, mock_entry)
        mock_hass.states.get.return_value = None
        result = coord._calculate_ventilation_recommendation(self._bad_data())
        assert result["status"] == VENTILATION_YES

    def test_bad_climate_cold_outside_returns_optional(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        state = MagicMock()
        state.state = "sunny"
        state.attributes = {"temperature": 2.0, "humidity": 50.0}
        mock_hass.states.get.return_value = state
        coord = _make_coord(mock_hass, mock_entry, weather_entity="weather.home")
        result = coord._calculate_ventilation_recommendation(self._bad_data())
        assert result["status"] == VENTILATION_OPTIONAL

    def test_bad_climate_humid_outside_returns_no(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        state = MagicMock()
        state.state = "sunny"
        state.attributes = {"temperature": 18.0, "humidity": 80.0}
        mock_hass.states.get.return_value = state
        coord = _make_coord(mock_hass, mock_entry, weather_entity="weather.home")
        result = coord._calculate_ventilation_recommendation(self._bad_data())
        assert result["status"] == VENTILATION_NO

    def test_bad_climate_good_weather_returns_yes(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        state = MagicMock()
        state.state = "sunny"
        state.attributes = {"temperature": 15.0, "humidity": 50.0}
        mock_hass.states.get.return_value = state
        coord = _make_coord(mock_hass, mock_entry, weather_entity="weather.home")
        result = coord._calculate_ventilation_recommendation(self._bad_data())
        assert result["status"] == VENTILATION_YES

    def test_outdoor_temp_set_when_weather_available(self, mock_hass, mock_entry):
        mock_hass.states.get.side_effect = None
        state = MagicMock()
        state.state = "sunny"
        state.attributes = {"temperature": 15.0, "humidity": 50.0}
        mock_hass.states.get.return_value = state
        coord = _make_coord(mock_hass, mock_entry, weather_entity="weather.home")
        result = coord._calculate_ventilation_recommendation(self._good_data())
        assert result["outdoor_temp"] == 15.0
        assert result["outdoor_humidity"] == 50.0


# ── async_setup_entry / async_unload_entry / async_reload_entry ────────────
#
# These exercise the integration startup/shutdown lifecycle, in particular
# the v2.5.0 behaviour where a failing first refresh must NOT abort setup
# (sensors are picked up on the next 30s poll cycle instead).

def _mock_coordinator(rooms=None):
    """Build a MagicMock standing in for IndeklimaDataCoordinator."""
    coordinator = MagicMock()
    coordinator.async_config_entry_first_refresh = AsyncMock()
    coordinator.rooms = rooms if rooms is not None else []
    coordinator.async_setup_dehumidifier_listeners = MagicMock()
    coordinator.async_unload_dehumidifier_listeners = MagicMock()
    return coordinator


class TestAsyncSetupEntry:
    @pytest.mark.asyncio
    async def test_happy_path_registers_devices_and_platforms(self, mock_hass, mock_entry):
        from custom_components.indeklima import async_setup_entry
        from custom_components.indeklima.const import DOMAIN

        coordinator = _mock_coordinator(rooms=[{"name": "Stue"}, {"name": "Køkken"}])
        mock_hass.config_entries.async_forward_entry_setups = AsyncMock()
        mock_device_registry = MagicMock()

        with patch("custom_components.indeklima.IndeklimaDataCoordinator", return_value=coordinator), \
             patch("custom_components.indeklima.dr") as mock_dr, \
             patch("custom_components.indeklima.async_register_websocket_commands") as mock_ws, \
             patch("custom_components.indeklima.async_register_panel", new_callable=AsyncMock) as mock_panel:
            mock_dr.async_get.return_value = mock_device_registry
            result = await async_setup_entry(mock_hass, mock_entry)

        assert result is True
        coordinator.async_config_entry_first_refresh.assert_awaited_once()
        assert mock_entry.runtime_data is coordinator
        assert mock_hass.data[DOMAIN][mock_entry.entry_id] is coordinator
        # hub device + 2 room devices = 3 calls
        assert mock_device_registry.async_get_or_create.call_count == 3
        mock_ws.assert_called_once_with(mock_hass)
        mock_panel.assert_awaited_once_with(mock_hass)
        coordinator.async_setup_dehumidifier_listeners.assert_called_once()
        mock_entry.add_update_listener.assert_called_once()
        mock_entry.async_on_unload.assert_called_once()

    @pytest.mark.asyncio
    async def test_first_refresh_failure_does_not_block_setup(self, mock_hass, mock_entry):
        """Critical v2.5.0 behaviour: a failing first refresh must not abort setup —
        sensors are picked up on the next scan cycle instead (logs a warning only)."""
        from custom_components.indeklima import async_setup_entry

        coordinator = _mock_coordinator()
        coordinator.async_config_entry_first_refresh = AsyncMock(
            side_effect=Exception("sensors unavailable at boot")
        )
        mock_hass.config_entries.async_forward_entry_setups = AsyncMock()

        with patch("custom_components.indeklima.IndeklimaDataCoordinator", return_value=coordinator), \
             patch("custom_components.indeklima.dr") as mock_dr, \
             patch("custom_components.indeklima.async_register_websocket_commands"), \
             patch("custom_components.indeklima.async_register_panel", new_callable=AsyncMock):
            mock_dr.async_get.return_value = MagicMock()
            result = await async_setup_entry(mock_hass, mock_entry)

        assert result is True
        assert mock_entry.runtime_data is coordinator

    @pytest.mark.asyncio
    async def test_no_rooms_registers_only_hub_device(self, mock_hass, mock_entry):
        from custom_components.indeklima import async_setup_entry

        coordinator = _mock_coordinator(rooms=[])
        mock_hass.config_entries.async_forward_entry_setups = AsyncMock()
        mock_device_registry = MagicMock()

        with patch("custom_components.indeklima.IndeklimaDataCoordinator", return_value=coordinator), \
             patch("custom_components.indeklima.dr") as mock_dr, \
             patch("custom_components.indeklima.async_register_websocket_commands"), \
             patch("custom_components.indeklima.async_register_panel", new_callable=AsyncMock):
            mock_dr.async_get.return_value = mock_device_registry
            await async_setup_entry(mock_hass, mock_entry)

        assert mock_device_registry.async_get_or_create.call_count == 1


class TestAsyncUnloadEntry:
    @pytest.mark.asyncio
    async def test_unload_cancels_listeners_and_unloads_platforms(self, mock_hass, mock_entry):
        from custom_components.indeklima import async_unload_entry
        from custom_components.indeklima.const import DOMAIN

        coordinator = _mock_coordinator()
        mock_entry.runtime_data = coordinator
        mock_hass.data[DOMAIN] = {mock_entry.entry_id: coordinator}
        mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

        with patch("custom_components.indeklima.async_unregister_panel") as mock_unreg_panel, \
             patch("custom_components.indeklima.async_unregister_cards_resource", new_callable=AsyncMock) as mock_unreg_cards:
            result = await async_unload_entry(mock_hass, mock_entry)

        assert result is True
        mock_unreg_panel.assert_called_once_with(mock_hass)
        mock_unreg_cards.assert_awaited_once_with(mock_hass)
        coordinator.async_unload_dehumidifier_listeners.assert_called_once()
        assert mock_entry.entry_id not in mock_hass.data[DOMAIN]

    @pytest.mark.asyncio
    async def test_unload_handles_missing_runtime_data(self, mock_hass, mock_entry):
        """Should not crash if runtime_data is None (e.g. setup never completed)."""
        from custom_components.indeklima import async_unload_entry
        from custom_components.indeklima.const import DOMAIN

        mock_entry.runtime_data = None
        mock_hass.data[DOMAIN] = {mock_entry.entry_id: MagicMock()}
        mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)

        with patch("custom_components.indeklima.async_unregister_panel"), \
             patch("custom_components.indeklima.async_unregister_cards_resource", new_callable=AsyncMock):
            result = await async_unload_entry(mock_hass, mock_entry)

        assert result is True

    @pytest.mark.asyncio
    async def test_unload_platforms_failure_keeps_data(self, mock_hass, mock_entry):
        from custom_components.indeklima import async_unload_entry
        from custom_components.indeklima.const import DOMAIN

        coordinator = _mock_coordinator()
        mock_entry.runtime_data = coordinator
        mock_hass.data[DOMAIN] = {mock_entry.entry_id: coordinator}
        mock_hass.config_entries.async_unload_platforms = AsyncMock(return_value=False)

        with patch("custom_components.indeklima.async_unregister_panel"), \
             patch("custom_components.indeklima.async_unregister_cards_resource", new_callable=AsyncMock):
            result = await async_unload_entry(mock_hass, mock_entry)

        assert result is False
        assert mock_entry.entry_id in mock_hass.data[DOMAIN]


class TestAsyncReloadEntry:
    @pytest.mark.asyncio
    async def test_reload_calls_unload_then_setup(self, mock_hass, mock_entry):
        from custom_components.indeklima import async_reload_entry

        with patch("custom_components.indeklima.async_unload_entry", new_callable=AsyncMock) as mock_unload, \
             patch("custom_components.indeklima.async_setup_entry", new_callable=AsyncMock) as mock_setup:
            await async_reload_entry(mock_hass, mock_entry)

        mock_unload.assert_awaited_once_with(mock_hass, mock_entry)
        mock_setup.assert_awaited_once_with(mock_hass, mock_entry)
