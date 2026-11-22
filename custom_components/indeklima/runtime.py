"""Shared access to the active Indeklima coordinator.

The coordinator is stored only on ``entry.runtime_data``. This module is the one
place that looks it up for the websocket API, system health and diagnostics.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN

if TYPE_CHECKING:
    from . import IndeklimaDataCoordinator


@callback
def async_get_active_coordinator(hass: HomeAssistant) -> IndeklimaDataCoordinator | None:
    """Return the coordinator of the first loaded entry, or None if there is none."""
    for entry in hass.config_entries.async_loaded_entries(DOMAIN):
        coordinator = getattr(entry, "runtime_data", None)
        if coordinator is not None:
            return coordinator
    return None
