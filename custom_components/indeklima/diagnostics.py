"""Diagnostics support for Indeklima.

Provides config entry diagnostics downloadable from:
Settings → Devices & Services → Indeklima → (⋮) → Download diagnostics

Also provides per-device diagnostics from the device info page.

No sensitive data is exposed — Indeklima uses only local HA sensor entity IDs
which are not secret, but we still redact any hypothetical credential fields
for future-proofing.
"""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, __version__, normalize_room_id

# Fields to redact — Indeklima has no passwords/tokens, but we include
# these keys as a precaution in case they are ever added to config.
TO_REDACT: list[str] = [
    "password",
    "api_key",
    "token",
    "access_token",
]


def _get_coordinator(hass: HomeAssistant, entry: ConfigEntry):
    """Return the coordinator for a config entry."""
    return hass.data.get(DOMAIN, {}).get(entry.entry_id)


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for the Indeklima config entry.

    Includes:
    - Integration version and configuration
    - All configured rooms and their sensor entity IDs
    - Current coordinator data (all room readings, averages, trends, ventilation)
    - Sensor availability status for each configured entity
    """
    coordinator = _get_coordinator(hass, entry)

    # Build sensor availability map — check each configured sensor entity
    sensor_availability: dict[str, dict] = {}
    rooms_config = entry.data.get("rooms", [])
    sensor_keys = [
        "humidity_sensors",
        "temperature_sensors",
        "co2_sensors",
        "voc_sensors",
        "formaldehyde_sensors",
        "pressure_sensors",
    ]

    for room in rooms_config:
        room_name = room.get("name", "unknown")
        sensor_availability[room_name] = {}

        for key in sensor_keys:
            sensors = room.get(key, [])
            if sensors:
                availability = []
                for entity_id in sensors:
                    state = hass.states.get(entity_id)
                    availability.append({
                        "entity_id": entity_id,
                        "available": state is not None and state.state not in ("unknown", "unavailable"),
                        "state": state.state if state else "not_found",
                    })
                sensor_availability[room_name][key] = availability

        # Window/door sensors
        window_sensors = room.get("window_sensors", [])
        if window_sensors:
            window_availability = []
            for window in window_sensors:
                if isinstance(window, dict):
                    entity_id = window.get("entity_id")
                    is_outdoor = window.get("is_outdoor", True)
                elif isinstance(window, str):
                    entity_id = window
                    is_outdoor = True
                else:
                    continue
                state = hass.states.get(entity_id)
                window_availability.append({
                    "entity_id": entity_id,
                    "is_outdoor": is_outdoor,
                    "available": state is not None and state.state not in ("unknown", "unavailable"),
                    "state": state.state if state else "not_found",
                })
            sensor_availability[room_name]["window_sensors"] = window_availability

    # Coordinator live data
    coordinator_data: dict[str, Any] = {}
    if coordinator and coordinator.data:
        coordinator_data = {
            "severity": coordinator.data.get("severity"),
            "status": coordinator.data.get("status"),
            "air_circulation": coordinator.data.get("air_circulation"),
            "open_windows": coordinator.data.get("open_windows", []),
            "open_internal_doors": coordinator.data.get("open_internal_doors", []),
            "averages": coordinator.data.get("averages", {}),
            "trends": coordinator.data.get("trends", {}),
            "ventilation_status": coordinator.data.get("ventilation", {}).get("status"),
            "rooms_summary": {
                room_name: {
                    "status": room_data.get("status"),
                    "severity": room_data.get("severity"),
                    "temperature": room_data.get("temperature"),
                    "humidity": room_data.get("humidity"),
                    "co2": room_data.get("co2"),
                    "pressure": room_data.get("pressure"),
                    "outdoor_windows_open": room_data.get("outdoor_windows_open", 0),
                    "internal_doors_open": room_data.get("internal_doors_open", 0),
                }
                for room_name, room_data in coordinator.data.get("rooms", {}).items()
            },
        }
        coordinator_last_update = str(coordinator.last_update_success)
    else:
        coordinator_last_update = "never"

    # Options (thresholds)
    options_info = {
        "humidity_summer_max": entry.options.get("humidity_summer_max", 60),
        "humidity_winter_max": entry.options.get("humidity_winter_max", 55),
        "co2_max": entry.options.get("co2_max", 1000),
        "voc_max": entry.options.get("voc_max", 3.0),
        "formaldehyde_max": entry.options.get("formaldehyde_max", 0.15),
        "weather_entity_configured": bool(entry.options.get("weather_entity")),
    }

    return {
        "integration_version": __version__,
        "entry_id": entry.entry_id,
        "coordinator_last_update_success": coordinator_last_update,
        "configuration": async_redact_data(
            {
                "room_count": len(rooms_config),
                "rooms": [r.get("name") for r in rooms_config],
                "options": options_info,
            },
            TO_REDACT,
        ),
        "sensor_availability": sensor_availability,
        "live_data": coordinator_data,
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: dr.DeviceEntry,
) -> dict[str, Any]:
    """Return diagnostics for a specific Indeklima device (hub or room).

    The hub device returns global averages and hub-level data.
    Room devices return room-specific sensor readings and availability.
    """
    coordinator = _get_coordinator(hass, entry)

    # Determine if this is the hub device or a room device
    # Identifiers format: (DOMAIN, "{entry_id}_hub") or (DOMAIN, "{entry_id}_room_{room_id}")
    device_identifier = next(
        (ident[1] for ident in device.identifiers if ident[0] == DOMAIN),
        None,
    )

    is_hub = device_identifier and device_identifier.endswith("_hub")

    if is_hub:
        # Hub device diagnostics
        hub_data: dict[str, Any] = {
            "device_type": "hub",
            "integration_version": __version__,
            "sw_version": device.sw_version,
        }

        if coordinator and coordinator.data:
            data = coordinator.data
            hub_data["live_data"] = {
                "severity_score": data.get("severity"),
                "overall_status": data.get("status"),
                "air_circulation": data.get("air_circulation"),
                "open_windows_count": len(data.get("open_windows", [])),
                "open_windows_rooms": data.get("open_windows", []),
                "open_internal_doors_rooms": data.get("open_internal_doors", []),
                "averages": data.get("averages", {}),
                "trends": data.get("trends", {}),
                "ventilation": data.get("ventilation", {}),
                "room_count": len(data.get("rooms", {})),
                "rooms_by_status": {
                    "critical": [n for n, r in data.get("rooms", {}).items() if r.get("status") == "critical"],
                    "warning":  [n for n, r in data.get("rooms", {}).items() if r.get("status") == "warning"],
                    "good":     [n for n, r in data.get("rooms", {}).items() if r.get("status") == "good"],
                },
            }
        return hub_data

    # Room device diagnostics
    # Extract room_id from identifier: "{entry_id}_room_{room_id}"
    room_id = None
    if device_identifier:
        prefix = f"{entry.entry_id}_room_"
        if device_identifier.startswith(prefix):
            room_id = device_identifier[len(prefix):]

    # Find room config by matching normalized name
    rooms_config = entry.data.get("rooms", [])
    room_config = None
    room_name = None

    for room in rooms_config:
        if normalize_room_id(room.get("name", "")) == room_id:
            room_config = room
            room_name = room.get("name")
            break

    if not room_config:
        return {
            "device_type": "room",
            "error": f"Room config not found for device identifier: {device_identifier}",
            "integration_version": __version__,
        }

    # Sensor availability for this room
    sensor_keys = [
        "humidity_sensors",
        "temperature_sensors",
        "co2_sensors",
        "voc_sensors",
        "formaldehyde_sensors",
        "pressure_sensors",
    ]
    sensors_info: dict[str, Any] = {}

    for key in sensor_keys:
        entities = room_config.get(key, [])
        if entities:
            sensors_info[key] = [
                {
                    "entity_id": eid,
                    "available": (
                        hass.states.get(eid) is not None
                        and hass.states.get(eid).state not in ("unknown", "unavailable")
                    ),
                    "current_value": (
                        hass.states.get(eid).state
                        if hass.states.get(eid) and hass.states.get(eid).state not in ("unknown", "unavailable")
                        else None
                    ),
                }
                for eid in entities
            ]

    window_sensors = room_config.get("window_sensors", [])
    if window_sensors:
        sensors_info["window_sensors"] = []
        for window in window_sensors:
            if isinstance(window, dict):
                entity_id = window.get("entity_id")
                is_outdoor = window.get("is_outdoor", True)
            elif isinstance(window, str):
                entity_id = window
                is_outdoor = True
            else:
                continue
            state = hass.states.get(entity_id)
            sensors_info["window_sensors"].append({
                "entity_id": entity_id,
                "is_outdoor": is_outdoor,
                "available": state is not None and state.state not in ("unknown", "unavailable"),
                "current_state": state.state if state else "not_found",
            })

    # Live room data from coordinator
    live_room_data: dict[str, Any] = {}
    if coordinator and coordinator.data:
        room_data = coordinator.data.get("rooms", {}).get(room_name, {})
        live_room_data = {
            "status": room_data.get("status"),
            "severity_score": room_data.get("severity"),
            "temperature": room_data.get("temperature"),
            "humidity": room_data.get("humidity"),
            "co2": room_data.get("co2"),
            "pressure": room_data.get("pressure"),
            "outdoor_windows_open": room_data.get("outdoor_windows_open", 0),
            "internal_doors_open": room_data.get("internal_doors_open", 0),
            "air_circulation_bonus_active": room_data.get("air_circulation_bonus", False),
        }

    return {
        "device_type": "room",
        "room_name": room_name,
        "room_id": room_id,
        "integration_version": __version__,
        "sw_version": device.sw_version,
        "configured_sensors": sensors_info,
        "live_data": live_room_data,
    }
