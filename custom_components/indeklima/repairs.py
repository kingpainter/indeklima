"""Repair flows for Indeklima integration.

Surfaces actionable repair issues in the HA Repairs dashboard when sensors
are unavailable or the coordinator fails to update.

Accessible via: Settings → System → Repairs
"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.components.repairs import ConfirmRepairFlow, RepairsFlow
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


# ── Issue IDs ─────────────────────────────────────────────────────────────────

ISSUE_SENSOR_UNAVAILABLE = "sensor_unavailable"
ISSUE_COORDINATOR_FAILED = "coordinator_update_failed"


# ── Issue raising helpers ─────────────────────────────────────────────────────

def raise_sensor_unavailable_issue(
    hass: HomeAssistant,
    entry_id: str,
    room_name: str,
    entity_id: str,
) -> None:
    """Raise a repair issue for an unavailable sensor."""
    from homeassistant.components.repairs import async_create_issue
    from homeassistant.helpers.issue_registry import IssueSeverity

    async_create_issue(
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
    from homeassistant.components.repairs import async_create_issue
    from homeassistant.helpers.issue_registry import IssueSeverity

    async_create_issue(
        hass,
        DOMAIN,
        f"{ISSUE_COORDINATOR_FAILED}_{entry_id}",
        is_fixable=True,
        severity=IssueSeverity.ERROR,
        translation_key=ISSUE_COORDINATOR_FAILED,
        translation_placeholders={
            "error": error_msg[:200],  # cap length for UI
        },
    )
    _LOGGER.error(
        "Raised repair issue: coordinator update failed — %s", error_msg
    )


def clear_coordinator_failed_issue(hass: HomeAssistant, entry_id: str) -> None:
    """Clear the coordinator-failed repair issue after a successful update."""
    from homeassistant.components.repairs import async_delete_issue

    async_delete_issue(hass, DOMAIN, f"{ISSUE_COORDINATOR_FAILED}_{entry_id}")


def clear_sensor_unavailable_issue(
    hass: HomeAssistant, entry_id: str, entity_id: str
) -> None:
    """Clear a sensor-unavailable repair issue once the sensor comes back."""
    from homeassistant.components.repairs import async_delete_issue

    async_delete_issue(
        hass, DOMAIN, f"{ISSUE_SENSOR_UNAVAILABLE}_{entry_id}_{entity_id}"
    )


# ── Repair flow classes ───────────────────────────────────────────────────────

class SensorUnavailableRepairFlow(ConfirmRepairFlow):
    """Repair flow shown when a configured sensor entity is unavailable.

    The user is asked to confirm they have checked the sensor. The issue is
    then dismissed — the integration will re-raise it on the next update
    cycle if the sensor is still unavailable.
    """


class CoordinatorFailedRepairFlow(ConfirmRepairFlow):
    """Repair flow shown when the coordinator fails to update.

    Asks the user to reload the integration. The issue is dismissed on
    confirmation; if the problem persists the coordinator will re-raise it.
    """


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

    # Fallback — should not happen
    return ConfirmRepairFlow()
