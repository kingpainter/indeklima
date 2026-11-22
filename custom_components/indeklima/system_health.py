"""System health support for Indeklima.

Visible under:
Settings → System → Repairs → ⋮ → System information → Indeklima

Shows integration status at a glance without digging through logs.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components import system_health
from homeassistant.core import HomeAssistant, callback

from .const import DOMAIN, __version__


@callback
def async_register(
    hass: HomeAssistant,
    register: system_health.SystemHealthRegistration,
) -> None:
    """Register Indeklima system health callbacks."""
    register.async_register_info(async_system_health_info)


async def async_system_health_info(hass: HomeAssistant) -> dict[str, Any]:
    """Return system health info for the Indeklima integration.

    Keys are translated via strings.json "system_health" → "info" section.
    Values can be strings, numbers, or coroutines (shown as spinner in UI).
    """
    # Loaded entries that have a coordinator; the first one is reported
    loaded = [
        entry
        for entry in hass.config_entries.async_loaded_entries(DOMAIN)
        if getattr(entry, "runtime_data", None) is not None
    ]
    entry_count = len(loaded)
    coordinator = loaded[0].runtime_data if loaded else None

    if coordinator is None:
        return {
            "integration_version": __version__,
            "config_entries": 0,
            "coordinator_status": "not_loaded",
        }

    data = coordinator.data or {}

    # Count total configured sensors across all rooms
    total_sensors = 0
    unavailable_sensors = 0
    sensor_keys = [
        "humidity_sensors",
        "temperature_sensors",
        "co2_sensors",
        "voc_sensors",
        "formaldehyde_sensors",
        "pressure_sensors",
    ]

    for room in coordinator.rooms:
        for key in sensor_keys:
            for entity_id in room.get(key, []):
                total_sensors += 1
                state = hass.states.get(entity_id)
                if not state or state.state in ("unknown", "unavailable"):
                    unavailable_sensors += 1

    rooms = data.get("rooms", {})
    critical_rooms = [n for n, r in rooms.items() if r.get("status") == "critical"]
    warning_rooms  = [n for n, r in rooms.items() if r.get("status") == "warning"]

    return {
        "integration_version": __version__,
        "config_entries":      entry_count,
        "coordinator_status":  "ok" if coordinator.last_update_success else "update_failed",
        "rooms_monitored":     len(coordinator.rooms),
        "overall_status":      data.get("status", "unknown"),
        "severity_score":      f"{data.get('severity', 0):.1f} / 100",
        "sensors_configured":  total_sensors,
        "sensors_unavailable": unavailable_sensors,
        "rooms_critical":      len(critical_rooms),
        "rooms_warning":       len(warning_rooms),
        "ventilation_status":  data.get("ventilation", {}).get("status", "unknown"),
        "air_circulation":     data.get("air_circulation", "unknown"),
        "weather_configured":  "yes" if coordinator.weather_entity else "no",
    }
