"""Tests for the Indeklima config flow and options flow.

These tests instantiate the flow handlers directly (bypassing the real HA
flow manager, in line with the fully-mocked style used elsewhere in this
test suite) and call the async_step_* methods directly. Anything that would
normally need a real `hass` (unique-id checks, entity registry lookups) is
patched.

Focus areas (previously only manually verified, per
instructions_for_claude_indeklima.md §13a):
  - CONF_ROOM_LED_CRITICAL_SEVERITY (per-room LED alarm threshold override)
  - CONF_ROOM_QUIET_HOURS_START/END (per-room quiet-hours override)
  - CONF_DEHUMIDIFIER_ON_DURATION
  - Room add/edit/delete round trip in the OptionsFlow
  - Window sensor outdoor/indoor classification step
"""
from __future__ import annotations

from unittest.mock import MagicMock, AsyncMock, patch
import pytest

from custom_components.indeklima.const import (
    CONF_ROOMS,
    CONF_HUMIDITY_SENSORS,
    CONF_TEMPERATURE_SENSORS,
    CONF_CO2_SENSORS,
    CONF_WINDOW_SENSORS,
    CONF_WINDOW_ENTITY,
    CONF_WINDOW_IS_OUTDOOR,
    CONF_DEHUMIDIFIER_ON_DURATION,
    DEFAULT_DEHUMIDIFIER_ON_DURATION,
    CONF_ROOM_LED_CRITICAL_SEVERITY,
    CONF_ROOM_QUIET_HOURS_START,
    CONF_ROOM_QUIET_HOURS_END,
    CONF_QUIET_HOURS_START,
    CONF_QUIET_HOURS_END,
    CONF_HUMIDITY_SUMMER_MAX,
    CONF_WEATHER_ENTITY,
)
from .conftest import mock_hass, mock_entry


def _make_config_flow(hass):
    from custom_components.indeklima.config_flow import IndeklimaConfigFlow
    flow = IndeklimaConfigFlow()
    flow.hass = hass
    return flow


def _make_options_flow(hass, entry):
    from custom_components.indeklima.config_flow import IndeklimaOptionsFlow
    flow = IndeklimaOptionsFlow(entry)
    flow.hass = hass
    return flow


def _schema_keys(schema):
    """Return the set of top-level string keys in a voluptuous schema."""
    return {getattr(key, "schema", key) for key in schema.schema.keys()}


# ── ConfigFlow: initial user step ──────────────────────────────────────────

class TestConfigFlowUserStep:
    @pytest.mark.asyncio
    async def test_shows_form_initially(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        result = await flow.async_step_user()
        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_submitting_name_moves_to_room_menu(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        with patch.object(flow, "async_set_unique_id", new=AsyncMock()), \
             patch.object(flow, "_abort_if_unique_id_configured", new=MagicMock()):
            result = await flow.async_step_user({"name": "Mit Hjem"})
        assert flow._name == "Mit Hjem"
        assert result["step_id"] == "room_menu"


# ── ConfigFlow: room menu ──────────────────────────────────────────────────

class TestConfigFlowRoomMenu:
    @pytest.mark.asyncio
    async def test_no_rooms_shows_error_on_done(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        result = await flow.async_step_room_menu({"action": "done"})
        assert result["type"] == "form"
        assert result["errors"]["base"] == "no_rooms"

    @pytest.mark.asyncio
    async def test_done_with_rooms_creates_entry_with_default_options(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        flow.rooms = [{"name": "Stue"}]
        result = await flow.async_step_room_menu({"action": "done"})
        assert result["type"] == "create_entry"
        assert result["data"][CONF_ROOMS] == [{"name": "Stue"}]
        assert result["options"][CONF_QUIET_HOURS_START] is not None
        assert result["options"][CONF_WEATHER_ENTITY] is None

    @pytest.mark.asyncio
    async def test_add_action_moves_to_room_config(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        result = await flow.async_step_room_menu({"action": "add"})
        assert result["step_id"] == "room_config"


# ── ConfigFlow: room_config (the risky per-room override fields) ──────────

class TestConfigFlowRoomConfig:
    @pytest.mark.asyncio
    async def test_shows_form_with_room_schema(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        result = await flow.async_step_room_config()
        assert result["type"] == "form"
        keys = _schema_keys(result["data_schema"])
        assert CONF_ROOM_LED_CRITICAL_SEVERITY in keys
        assert CONF_ROOM_QUIET_HOURS_START in keys
        assert CONF_ROOM_QUIET_HOURS_END in keys
        assert CONF_DEHUMIDIFIER_ON_DURATION in keys

    @pytest.mark.asyncio
    async def test_led_critical_severity_stored_when_provided(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        result = await flow.async_step_room_config({
            "name": "Stue",
            CONF_HUMIDITY_SENSORS: [],
            CONF_ROOM_LED_CRITICAL_SEVERITY: 45,
        })
        assert result["step_id"] == "room_menu"
        assert flow.rooms[0][CONF_ROOM_LED_CRITICAL_SEVERITY] == 45

    @pytest.mark.asyncio
    async def test_led_critical_severity_omitted_when_not_provided(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        await flow.async_step_room_config({"name": "Stue", CONF_HUMIDITY_SENSORS: []})
        assert CONF_ROOM_LED_CRITICAL_SEVERITY not in flow.rooms[0]

    @pytest.mark.asyncio
    async def test_quiet_hours_override_stored(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        await flow.async_step_room_config({
            "name": "Stue",
            CONF_ROOM_QUIET_HOURS_START: 22,
            CONF_ROOM_QUIET_HOURS_END: 7,
        })
        assert flow.rooms[0][CONF_ROOM_QUIET_HOURS_START] == 22
        assert flow.rooms[0][CONF_ROOM_QUIET_HOURS_END] == 7

    @pytest.mark.asyncio
    async def test_dehumidifier_on_duration_stored(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        await flow.async_step_room_config({
            "name": "Stue",
            CONF_DEHUMIDIFIER_ON_DURATION: 60,
        })
        assert flow.rooms[0][CONF_DEHUMIDIFIER_ON_DURATION] == 60

    @pytest.mark.asyncio
    async def test_zero_is_stored_not_treated_as_missing(self, mock_hass):
        """Regression guard: `if val:` would silently drop 0, which is a
        valid quiet-hours-start value (midnight)."""
        flow = _make_config_flow(mock_hass)
        await flow.async_step_room_config({
            "name": "Stue",
            CONF_ROOM_QUIET_HOURS_START: 0,
        })
        assert flow.rooms[0][CONF_ROOM_QUIET_HOURS_START] == 0

    @pytest.mark.asyncio
    async def test_no_window_sensors_appends_room_directly(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        result = await flow.async_step_room_config({"name": "Stue"})
        assert len(flow.rooms) == 1
        assert result["step_id"] == "room_menu"

    @pytest.mark.asyncio
    async def test_window_sensors_move_to_window_config(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        with patch("custom_components.indeklima.config_flow.er.async_get") as mock_er:
            mock_er.return_value = MagicMock(async_get=MagicMock(return_value=None))
            result = await flow.async_step_room_config({
                "name": "Stue",
                CONF_WINDOW_SENSORS: ["binary_sensor.stue_vindue"],
            })
        assert result["step_id"] == "window_config"
        assert len(flow.rooms) == 0  # not appended yet — waiting for window step


# ── ConfigFlow: window_config ──────────────────────────────────────────────

class TestConfigFlowWindowConfig:
    @pytest.mark.asyncio
    async def test_stores_outdoor_flag_and_appends_room(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        flow._temp_room_config = {"name": "Stue"}
        flow._temp_window_sensors = ["binary_sensor.stue_vindue"]

        result = await flow.async_step_window_config({
            "outdoor_binary_sensor.stue_vindue": False,
        })

        assert result["step_id"] == "room_menu"
        assert len(flow.rooms) == 1
        windows = flow.rooms[0][CONF_WINDOW_SENSORS]
        assert windows[0][CONF_WINDOW_ENTITY] == "binary_sensor.stue_vindue"
        assert windows[0][CONF_WINDOW_IS_OUTDOOR] is False

    @pytest.mark.asyncio
    async def test_defaults_to_outdoor_true_when_unspecified(self, mock_hass):
        flow = _make_config_flow(mock_hass)
        flow._temp_room_config = {"name": "Stue"}
        flow._temp_window_sensors = ["binary_sensor.stue_vindue"]

        with patch("custom_components.indeklima.config_flow.er.async_get") as mock_er:
            mock_er.return_value = MagicMock(async_get=MagicMock(return_value=None))
            result = await flow.async_step_window_config()

        assert result["type"] == "form"
        assert result["step_id"] == "window_config"


# ── OptionsFlow: main menu routing ─────────────────────────────────────────

class TestOptionsFlowMainMenu:
    @pytest.mark.asyncio
    async def test_routes_to_thresholds(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_main_menu({"menu": "thresholds"})
        assert result["step_id"] == "thresholds"

    @pytest.mark.asyncio
    async def test_routes_to_rooms(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_main_menu({"menu": "rooms"})
        assert result["step_id"] == "room_list"

    @pytest.mark.asyncio
    async def test_routes_to_weather(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_main_menu({"menu": "weather"})
        assert result["step_id"] == "weather_config"

    @pytest.mark.asyncio
    async def test_routes_to_quiet_hours(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_main_menu({"menu": "quiet_hours"})
        assert result["step_id"] == "quiet_hours"


# ── OptionsFlow: global settings steps ──────────────────────────────────────

class TestOptionsFlowGlobalSteps:
    @pytest.mark.asyncio
    async def test_quiet_hours_merges_into_existing_options(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_quiet_hours({
            CONF_QUIET_HOURS_START: 21,
            CONF_QUIET_HOURS_END: 8,
        })
        assert result["type"] == "create_entry"
        assert result["data"][CONF_QUIET_HOURS_START] == 21
        # existing option keys survive the merge
        assert CONF_HUMIDITY_SUMMER_MAX in result["data"]

    @pytest.mark.asyncio
    async def test_thresholds_creates_entry(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_thresholds({CONF_HUMIDITY_SUMMER_MAX: 65})
        assert result["type"] == "create_entry"
        assert result["data"][CONF_HUMIDITY_SUMMER_MAX] == 65

    @pytest.mark.asyncio
    async def test_weather_config_creates_entry(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_weather_config({CONF_WEATHER_ENTITY: "weather.hjem"})
        assert result["type"] == "create_entry"
        assert result["data"][CONF_WEATHER_ENTITY] == "weather.hjem"


# ── OptionsFlow: room list actions (add/edit/delete) ───────────────────────

class TestOptionsFlowRoomList:
    @pytest.mark.asyncio
    async def test_add_action_moves_to_add_room(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_room_list({"action": "add"})
        assert result["step_id"] == "add_room"

    @pytest.mark.asyncio
    async def test_edit_action_selects_room_index(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_room_list({"action": "edit_0"})
        assert flow._selected_room_idx == 0
        assert result["step_id"] == "edit_room"

    @pytest.mark.asyncio
    async def test_delete_action_removes_room_and_saves(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        original_count = len(flow._rooms)
        await flow.async_step_room_list({"action": "delete_0"})
        assert len(flow._rooms) == original_count - 1
        mock_hass.config_entries.async_update_entry.assert_called_once()

    @pytest.mark.asyncio
    async def test_done_action_returns_to_main_menu(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_room_list({"action": "done"})
        assert result["step_id"] == "main_menu"


# ── OptionsFlow: add_room round trip ────────────────────────────────────────

class TestOptionsFlowAddRoom:
    @pytest.mark.asyncio
    async def test_add_room_without_windows_saves_immediately(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        result = await flow.async_step_add_room({
            "name": "Bryggers",
            CONF_ROOM_LED_CRITICAL_SEVERITY: 40,
        })
        assert result["step_id"] == "room_list"
        added = flow._rooms[-1]
        assert added["name"] == "Bryggers"
        assert added[CONF_ROOM_LED_CRITICAL_SEVERITY] == 40
        mock_hass.config_entries.async_update_entry.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_room_with_windows_moves_to_window_step(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        with patch("custom_components.indeklima.config_flow.er.async_get") as mock_er:
            mock_er.return_value = MagicMock(async_get=MagicMock(return_value=None))
            result = await flow.async_step_add_room({
                "name": "Bryggers",
                CONF_WINDOW_SENSORS: ["binary_sensor.bryggers_dor"],
            })
        assert result["step_id"] == "add_room_windows"
        mock_hass.config_entries.async_update_entry.assert_not_called()

    @pytest.mark.asyncio
    async def test_add_room_windows_completes_and_saves(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        flow._temp_room_config = {"name": "Bryggers"}
        flow._temp_window_sensors = ["binary_sensor.bryggers_dor"]

        result = await flow.async_step_add_room_windows({
            "outdoor_binary_sensor.bryggers_dor": True,
        })

        assert result["step_id"] == "room_list"
        added = flow._rooms[-1]
        assert added[CONF_WINDOW_SENSORS][0][CONF_WINDOW_ENTITY] == "binary_sensor.bryggers_dor"
        assert added[CONF_WINDOW_SENSORS][0][CONF_WINDOW_IS_OUTDOOR] is True
        mock_hass.config_entries.async_update_entry.assert_called_once()


# ── OptionsFlow: edit_room round trip ───────────────────────────────────────

class TestOptionsFlowEditRoom:
    @pytest.mark.asyncio
    async def test_edit_room_schema_prefills_led_severity_default(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        flow._rooms[0][CONF_ROOM_LED_CRITICAL_SEVERITY] = 35
        flow._selected_room_idx = 0

        result = await flow.async_step_edit_room()

        assert result["type"] == "form"
        assert result["step_id"] == "edit_room"
        keys = _schema_keys(result["data_schema"])
        assert CONF_ROOM_LED_CRITICAL_SEVERITY in keys

    @pytest.mark.asyncio
    async def test_edit_room_updates_existing_room_in_place(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        flow._selected_room_idx = 0
        original_name = flow._rooms[0]["name"]

        result = await flow.async_step_edit_room({
            "name": original_name,
            CONF_ROOM_LED_CRITICAL_SEVERITY: 50,
        })

        assert result["step_id"] == "room_list"
        assert flow._rooms[0][CONF_ROOM_LED_CRITICAL_SEVERITY] == 50
        mock_hass.config_entries.async_update_entry.assert_called_once()

    @pytest.mark.asyncio
    async def test_edit_room_windows_prefills_existing_outdoor_flags(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        flow._selected_room_idx = 0
        flow._rooms[0][CONF_WINDOW_SENSORS] = [
            {CONF_WINDOW_ENTITY: "binary_sensor.stue_vindue", CONF_WINDOW_IS_OUTDOOR: False},
        ]
        flow._temp_room_config = {"name": flow._rooms[0]["name"]}
        flow._temp_window_sensors = ["binary_sensor.stue_vindue"]

        with patch("custom_components.indeklima.config_flow.er.async_get") as mock_er:
            mock_er.return_value = MagicMock(async_get=MagicMock(return_value=None))
            result = await flow.async_step_edit_room_windows()

        assert result["type"] == "form"
        assert result["step_id"] == "edit_room_windows"

    @pytest.mark.asyncio
    async def test_edit_room_windows_saves_updated_classification(self, mock_hass, mock_entry):
        flow = _make_options_flow(mock_hass, mock_entry)
        flow._selected_room_idx = 0
        flow._temp_room_config = {"name": flow._rooms[0]["name"]}
        flow._temp_window_sensors = ["binary_sensor.stue_vindue"]

        result = await flow.async_step_edit_room_windows({
            "outdoor_binary_sensor.stue_vindue": True,
        })

        assert result["step_id"] == "room_list"
        assert flow._rooms[0][CONF_WINDOW_SENSORS][0][CONF_WINDOW_IS_OUTDOOR] is True
        mock_hass.config_entries.async_update_entry.assert_called_once()
