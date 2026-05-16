"""Tests for repairs.py."""
from __future__ import annotations

from unittest.mock import MagicMock, patch, call
import pytest

from custom_components.indeklima.repairs import (
    ISSUE_SENSOR_UNAVAILABLE,
    ISSUE_COORDINATOR_FAILED,
    raise_sensor_unavailable_issue,
    raise_coordinator_failed_issue,
    clear_coordinator_failed_issue,
    clear_sensor_unavailable_issue,
    async_create_fix_flow,
    SensorUnavailableRepairFlow,
    CoordinatorFailedRepairFlow,
    _get_create_issue,
    _get_delete_issue,
    _get_issue_severity,
)
from homeassistant.components.repairs import ConfirmRepairFlow
from .conftest import mock_hass


class TestIssueIds:
    def test_issue_id_constants(self):
        assert ISSUE_SENSOR_UNAVAILABLE == "sensor_unavailable"
        assert ISSUE_COORDINATOR_FAILED == "coordinator_update_failed"


class TestCompatibilityShims:
    def test_get_create_issue_returns_callable_or_none(self):
        result = _get_create_issue()
        assert result is None or callable(result)

    def test_get_delete_issue_returns_callable_or_none(self):
        result = _get_delete_issue()
        assert result is None or callable(result)

    def test_get_issue_severity_returns_class_or_none(self):
        result = _get_issue_severity()
        assert result is None or hasattr(result, "WARNING")


class TestRaiseSensorUnavailableIssue:
    def test_calls_create_issue_when_available(self, mock_hass):
        mock_fn = MagicMock()
        mock_severity = MagicMock()
        mock_severity.WARNING = "warning"
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=mock_fn,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=mock_severity,
        ):
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )
        mock_fn.assert_called_once()

    def test_issue_id_contains_entity(self, mock_hass):
        mock_fn = MagicMock()
        mock_severity = MagicMock()
        mock_severity.WARNING = "warning"
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=mock_fn,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=mock_severity,
        ):
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )
        issue_id = mock_fn.call_args[0][2]
        assert "sensor.stue_humidity" in issue_id

    def test_issue_id_starts_with_sensor_unavailable(self, mock_hass):
        mock_fn = MagicMock()
        mock_severity = MagicMock()
        mock_severity.WARNING = "warning"
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=mock_fn,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=mock_severity,
        ):
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )
        issue_id = mock_fn.call_args[0][2]
        assert issue_id.startswith(ISSUE_SENSOR_UNAVAILABLE)

    def test_translation_placeholders(self, mock_hass):
        mock_fn = MagicMock()
        mock_severity = MagicMock()
        mock_severity.WARNING = "warning"
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=mock_fn,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=mock_severity,
        ):
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )
        kwargs = mock_fn.call_args[1]
        assert kwargs["translation_placeholders"]["room_name"] == "Stue"
        assert kwargs["translation_placeholders"]["entity_id"] == "sensor.stue_humidity"

    def test_does_nothing_when_api_unavailable(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=None,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=None,
        ):
            # Should not raise
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )


class TestRaiseCoordinatorFailedIssue:
    def test_calls_create_issue(self, mock_hass):
        mock_fn = MagicMock()
        mock_severity = MagicMock()
        mock_severity.ERROR = "error"
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=mock_fn,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=mock_severity,
        ):
            raise_coordinator_failed_issue(mock_hass, "entry_1", "timeout error")
        mock_fn.assert_called_once()

    def test_error_message_capped_at_200(self, mock_hass):
        mock_fn = MagicMock()
        mock_severity = MagicMock()
        mock_severity.ERROR = "error"
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=mock_fn,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=mock_severity,
        ):
            raise_coordinator_failed_issue(mock_hass, "entry_1", "x" * 500)
        placeholders = mock_fn.call_args[1]["translation_placeholders"]
        assert len(placeholders["error"]) <= 200

    def test_issue_id_starts_with_coordinator_failed(self, mock_hass):
        mock_fn = MagicMock()
        mock_severity = MagicMock()
        mock_severity.ERROR = "error"
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=mock_fn,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=mock_severity,
        ):
            raise_coordinator_failed_issue(mock_hass, "entry_1", "err")
        issue_id = mock_fn.call_args[0][2]
        assert issue_id.startswith(ISSUE_COORDINATOR_FAILED)

    def test_does_nothing_when_api_unavailable(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs._get_create_issue",
            return_value=None,
        ), patch(
            "custom_components.indeklima.repairs._get_issue_severity",
            return_value=None,
        ):
            raise_coordinator_failed_issue(mock_hass, "entry_1", "err")


class TestClearIssues:
    def test_clear_coordinator_failed(self, mock_hass):
        mock_fn = MagicMock()
        with patch(
            "custom_components.indeklima.repairs._get_delete_issue",
            return_value=mock_fn,
        ):
            clear_coordinator_failed_issue(mock_hass, "entry_1")
        mock_fn.assert_called_once_with(
            mock_hass,
            "indeklima",
            f"{ISSUE_COORDINATOR_FAILED}_entry_1",
        )

    def test_clear_sensor_unavailable(self, mock_hass):
        mock_fn = MagicMock()
        with patch(
            "custom_components.indeklima.repairs._get_delete_issue",
            return_value=mock_fn,
        ):
            clear_sensor_unavailable_issue(
                mock_hass, "entry_1", "sensor.stue_humidity"
            )
        mock_fn.assert_called_once()
        issue_id = mock_fn.call_args[0][2]
        assert "sensor.stue_humidity" in issue_id

    def test_clear_does_nothing_when_api_unavailable(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs._get_delete_issue",
            return_value=None,
        ):
            clear_coordinator_failed_issue(mock_hass, "entry_1")
            clear_sensor_unavailable_issue(mock_hass, "entry_1", "sensor.test")


class TestAsyncCreateFixFlow:
    @pytest.mark.asyncio
    async def test_sensor_unavailable_returns_correct_flow(self, mock_hass):
        flow = await async_create_fix_flow(
            mock_hass,
            f"{ISSUE_SENSOR_UNAVAILABLE}_entry_1_sensor.test",
            {},
        )
        assert isinstance(flow, SensorUnavailableRepairFlow)

    @pytest.mark.asyncio
    async def test_coordinator_failed_returns_correct_flow(self, mock_hass):
        flow = await async_create_fix_flow(
            mock_hass,
            f"{ISSUE_COORDINATOR_FAILED}_entry_1",
            {},
        )
        assert isinstance(flow, CoordinatorFailedRepairFlow)

    @pytest.mark.asyncio
    async def test_unknown_issue_returns_confirm_flow(self, mock_hass):
        flow = await async_create_fix_flow(mock_hass, "unknown_issue_xyz", {})
        assert isinstance(flow, ConfirmRepairFlow)

    @pytest.mark.asyncio
    async def test_sensor_flow_is_confirm_repair_flow(self, mock_hass):
        flow = await async_create_fix_flow(
            mock_hass, f"{ISSUE_SENSOR_UNAVAILABLE}_x", {}
        )
        assert isinstance(flow, ConfirmRepairFlow)

    @pytest.mark.asyncio
    async def test_coordinator_flow_is_confirm_repair_flow(self, mock_hass):
        flow = await async_create_fix_flow(
            mock_hass, f"{ISSUE_COORDINATOR_FAILED}_x", {}
        )
        assert isinstance(flow, ConfirmRepairFlow)
