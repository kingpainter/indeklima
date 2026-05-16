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
)
from homeassistant.components.repairs import ConfirmRepairFlow
from .conftest import mock_hass


class TestIssueIds:
    def test_issue_id_constants(self):
        assert ISSUE_SENSOR_UNAVAILABLE == "sensor_unavailable"
        assert ISSUE_COORDINATOR_FAILED == "coordinator_update_failed"


class TestRaiseSensorUnavailableIssue:
    def test_calls_async_create_issue(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs.async_create_issue"
        ) as mock_create:
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )
            mock_create.assert_called_once()

    def test_issue_id_contains_entity(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs.async_create_issue"
        ) as mock_create:
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )
            issue_id = mock_create.call_args[0][2]
            assert "sensor.stue_humidity" in issue_id

    def test_issue_id_contains_sensor_unavailable(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs.async_create_issue"
        ) as mock_create:
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )
            issue_id = mock_create.call_args[0][2]
            assert issue_id.startswith(ISSUE_SENSOR_UNAVAILABLE)

    def test_translation_placeholders(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs.async_create_issue"
        ) as mock_create:
            raise_sensor_unavailable_issue(
                mock_hass, "entry_1", "Stue", "sensor.stue_humidity"
            )
            kwargs = mock_create.call_args[1]
            assert kwargs["translation_placeholders"]["room_name"] == "Stue"
            assert kwargs["translation_placeholders"]["entity_id"] == "sensor.stue_humidity"


class TestRaiseCoordinatorFailedIssue:
    def test_calls_async_create_issue(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs.async_create_issue"
        ) as mock_create:
            raise_coordinator_failed_issue(mock_hass, "entry_1", "timeout error")
            mock_create.assert_called_once()

    def test_error_message_capped(self, mock_hass):
        long_error = "x" * 500
        with patch(
            "custom_components.indeklima.repairs.async_create_issue"
        ) as mock_create:
            raise_coordinator_failed_issue(mock_hass, "entry_1", long_error)
            placeholders = mock_create.call_args[1]["translation_placeholders"]
            assert len(placeholders["error"]) <= 200

    def test_issue_id_contains_coordinator_failed(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs.async_create_issue"
        ) as mock_create:
            raise_coordinator_failed_issue(mock_hass, "entry_1", "err")
            issue_id = mock_create.call_args[0][2]
            assert issue_id.startswith(ISSUE_COORDINATOR_FAILED)


class TestClearIssues:
    def test_clear_coordinator_failed(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs.async_delete_issue"
        ) as mock_delete:
            clear_coordinator_failed_issue(mock_hass, "entry_1")
            mock_delete.assert_called_once_with(
                mock_hass,
                "indeklima",
                f"{ISSUE_COORDINATOR_FAILED}_entry_1",
            )

    def test_clear_sensor_unavailable(self, mock_hass):
        with patch(
            "custom_components.indeklima.repairs.async_delete_issue"
        ) as mock_delete:
            clear_sensor_unavailable_issue(
                mock_hass, "entry_1", "sensor.stue_humidity"
            )
            mock_delete.assert_called_once()
            issue_id = mock_delete.call_args[0][2]
            assert "sensor.stue_humidity" in issue_id


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
    async def test_unknown_issue_returns_fallback(self, mock_hass):
        flow = await async_create_fix_flow(mock_hass, "unknown_issue_xyz", {})
        assert isinstance(flow, ConfirmRepairFlow)
