"""Repair flows for Indeklima integration."""
from __future__ import annotations

import logging

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# ── Issue IDs ─────────────────────────────────────────────────────────────────

ISSUE_SENSOR_UNAVAILABLE = "sensor_unavailable"
ISSUE_COORDINATOR_FAILED = "coordinator_update_failed"


# ── Compatibility shim for HA repairs API ─────────────────────────────────────
# async_create_issue / async_delete_issue moved between HA versions.
# Try the modern location first, fall back gracefully.

def _get_create_issue():
    try:
        from homeassistant.components.repairs import async_create_issue
        return async_create_issue
    except ImportError:
        pass
    try:
        from homeassistant.helpers.issue_registry import async_create_issue
        return async_create_issue
    except ImportError:
        return None


def _get_delete_issue():
    try:
        from homeassistant.components.repairs import async_delete_issue
        return async_delete_issue
    except ImportError:
        pass
    try:
        from homeassistant.helpers.issue_registry import async_delete_issue
        return async_delete_issue
    except ImportError:
        return None


def _get_issue_severity():
    try:
        from homeassistant.helpers.issue_registry import IssueSeverity
        return IssueSeverity
    except ImportError:
        return None


# ── Issue raising helpers ─────────────────────────────────────────────────────

def raise_sensor_unavailable_issue(
    hass: HomeAssistant,
    entry_id: str,
    room_name: str,
    entity_id: str,
) -> None:
    """Raise a repair issue for an unavailable sensor."""
    create_issue = _get_create_issue()
    IssueSeverity = _get_issue_severity()
    if create_issue is None or IssueSeverity is None:
        _LOGGER.debug("repairs API not available, skipping issue creation")
        return
    create_issue(
        hass,
        DOMAIN,
        f"{ISSUE_SENSOR_UNAVAILABLE}_{entry_id}_{entity_id}",
        is_fixable=True,
        severity=IssueSeverity.WARNING,
        translation_key=ISSUE_SENSOR_UNAVAILABLE,
        translation_placeholders={
            "room_name": room_name,
            "entity_id": entity_id,
        },
    )
    _LOGGER.warning(
        "Raised repair issue: sensor unavailable — %s in %s", entity_id, room_name
    )


def raise_coordinator_failed_issue(
    hass: HomeAssistant,
    entry_id: str,
    error_msg: str,
) -> None:
    """Raise a repair issue when the coordinator update fails."""
    create_issue = _get_create_issue()
    IssueSeverity = _get_issue_severity()
    if create_issue is None or IssueSeverity is None:
        _LOGGER.debug("repairs API not available, skipping issue creation")
        return
    create_issue(
        hass,
        DOMAIN,
        f"{ISSUE_COORDINATOR_FAILED}_{entry_id}",
        is_fixable=True,
        severity=IssueSeverity.ERROR,
        translation_key=ISSUE_COORDINATOR_FAILED,
        translation_placeholders={
            "error": error_msg[:200],
        },
    )
    _LOGGER.error(
        "Raised repair issue: coordinator update failed — %s", error_msg
    )


def clear_coordinator_failed_issue(hass: HomeAssistant, entry_id: str) -> None:
    """Clear the coordinator-failed repair issue after a successful update."""
    delete_issue = _get_delete_issue()
    if delete_issue is None:
        return
    delete_issue(hass, DOMAIN, f"{ISSUE_COORDINATOR_FAILED}_{entry_id}")


def clear_sensor_unavailable_issue(
    hass: HomeAssistant, entry_id: str, entity_id: str
) -> None:
    """Clear a sensor-unavailable repair issue once the sensor comes back."""
    delete_issue = _get_delete_issue()
    if delete_issue is None:
        return
    delete_issue(
        hass, DOMAIN, f"{ISSUE_SENSOR_UNAVAILABLE}_{entry_id}_{entity_id}"
    )


# ── Repair flow classes ───────────────────────────────────────────────────────

class SensorUnavailableRepairFlow(ConfirmRepairFlow):
    """Repair flow for unavailable sensor."""


class CoordinatorFailedRepairFlow(ConfirmRepairFlow):
    """Repair flow for coordinator update failure."""


# ── Factory ───────────────────────────────────────────────────────────────────

async def async_create_fix_flow(
    hass: HomeAssistant,
    issue_id: str,
    data: dict[str, str | int | float | None] | None,
) -> RepairsFlow:
    """Create the correct repair flow for a given issue_id."""
    if issue_id.startswith(ISSUE_SENSOR_UNAVAILABLE):
        return SensorUnavailableRepairFlow()
    if issue_id.startswith(ISSUE_COORDINATOR_FAILED):
        return CoordinatorFailedRepairFlow()
    return ConfirmRepairFlow()
