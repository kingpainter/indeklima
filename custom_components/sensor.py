"""Sensor platform for Indeklima integration.

Version: 2.1.0
"""
from __future__ import annotations

import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from . import IndeklimaDataCoordinator
from .const import DOMAIN, SENSOR_TYPES, __version__

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Indeklima sensor based on a config entry."""
    coordinator: IndeklimaDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = []
    
    # Add global sensors (attached to hub device)
    for sensor_type, config in SENSOR_TYPES.items():
        entities.append(
            IndeklimaGlobalSensor(
                coordinator,
                entry,
                sensor_type,
                config,
            )
        )
    
    # Add room sensors (attached to room devices)
    for room in coordinator.rooms:
        room_name = room.get("name")
        entities.append(
            IndeklimaRoomSensor(
                coordinator,
                entry,
                room_name,
            )
        )
    
    async_add_entities(entities)


class IndeklimaGlobalSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Indeklima global sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IndeklimaDataCoordinator,
        entry: ConfigEntry,
        sensor_type: str,
        config: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._config = config
        self._entry = entry
        
        # Entity naming per HA guidelines
        self._attr_unique_id = f"{entry.entry_id}_{sensor_type}"
        self._attr_name = config["name"]
        self._attr_icon = config["icon"]
        self._attr_native_unit_of_measurement = config.get("unit")
        
        # Set device class if available
        if device_class := config.get("device_class"):
            self._attr_device_class = SensorDeviceClass(device_class)
        
        # Link to hub device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_hub")},
        )

    @property
    def native_value(self) -> float | str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        if self._sensor_type == "severity":
            return self.coordinator.data.get("severity")
        elif self._sensor_type == "severity_status":
            return self.coordinator.data.get("status")
        elif self._sensor_type == "open_windows":
            return len(self.coordinator.data.get("open_windows", []))
        elif self._sensor_type == "ventilation_recommendation":
            ventilation = self.coordinator.data.get("ventilation", {})
            return ventilation.get("status", "Nej")
        elif self._sensor_type.startswith("trend_"):
            # Get trend value
            trend_key = self._sensor_type.replace("trend_", "")
            return self.coordinator.data.get("trends", {}).get(trend_key, "Stabil")
        elif self._sensor_type.endswith("_avg"):
            # Get average value
            key = self._sensor_type.replace("_avg", "")
            return self.coordinator.data.get("averages", {}).get(key)
        
        return None
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        if self._sensor_type == "open_windows":
            rooms = self.coordinator.data.get("open_windows", [])
            return {
                "rum": ", ".join(rooms) if rooms else "Ingen",
                "count": len(rooms),
            }
        elif self._sensor_type == "ventilation_recommendation":
            ventilation = self.coordinator.data.get("ventilation", {})
            attrs = {
                "begrundelse": ", ".join(ventilation.get("reason", [])),
                "rum": ", ".join(ventilation.get("rooms", [])) if ventilation.get("rooms") else "Ingen specifikke",
            }
            if ventilation.get("outdoor_temp") is not None:
                attrs["ude_temperatur"] = round(ventilation["outdoor_temp"], 1)
            if ventilation.get("outdoor_humidity") is not None:
                attrs["ude_fugtighed"] = round(ventilation["outdoor_humidity"], 1)
            return attrs
        return {}


class IndeklimaRoomSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Indeklima room sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: IndeklimaDataCoordinator,
        entry: ConfigEntry,
        room_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._room_name = room_name
        self._entry = entry
        self._last_notified: datetime | None = None
        
        # Create room ID (normalized for device identifier)
        room_id = room_name.lower().replace(" ", "_").replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
        
        # Entity naming per HA guidelines
        self._attr_unique_id = f"{entry.entry_id}_room_{room_id}_status"
        self._attr_name = "Status"  # Will show as "Indeklima Stue Status"
        
        # Link to room device
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry.entry_id}_room_{room_id}")},
        )

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        room_data = self.coordinator.data.get("rooms", {}).get(self._room_name, {})
        return room_data.get("status", "Unknown")
    
    @property
    def icon(self) -> str:
        """Return the icon based on status."""
        status = self.native_value
        if status == "Dårlig":
            return "mdi:alert-circle"
        elif status == "Advarsel":
            return "mdi:alert"
        return "mdi:check-circle"
    
    @property
    def extra_state_attributes(self) -> dict:
        """Return room-specific attributes."""
        if not self.coordinator.data:
            return {}
        
        room_data = self.coordinator.data.get("rooms", {}).get(self._room_name, {})
        
        attrs = {}
        
        # Add sensor values
        if "humidity" in room_data:
            attrs["fugtighed"] = round(room_data["humidity"], 1)
            if "humidity_sensors_count" in room_data:
                attrs["fugtighed_sensorer"] = room_data["humidity_sensors_count"]
        
        if "temperature" in room_data:
            attrs["temperatur"] = round(room_data["temperature"], 1)
            if "temperature_sensors_count" in room_data:
                attrs["temperatur_sensorer"] = room_data["temperature_sensors_count"]
        
        if "co2" in room_data:
            attrs["co2"] = round(room_data["co2"], 0)
            if "co2_sensors_count" in room_data:
                attrs["co2_sensorer"] = room_data["co2_sensors_count"]
        
        if "voc" in room_data:
            attrs["voc"] = round(room_data["voc"], 0)
            if "voc_sensors_count" in room_data:
                attrs["voc_sensorer"] = room_data["voc_sensors_count"]
        
        if "formaldehyde" in room_data:
            attrs["formaldehyd"] = round(room_data["formaldehyde"], 0)
            if "formaldehyde_sensors_count" in room_data:
                attrs["formaldehyd_sensorer"] = room_data["formaldehyde_sensors_count"]
        
        # Add last_notified timestamp for cooldown logic
        if self._last_notified:
            attrs["last_notified"] = self._last_notified.isoformat()
        
        return attrs
    
    def set_last_notified(self, timestamp: datetime | None = None) -> None:
        """Set the last notified timestamp."""
        self._last_notified = timestamp or dt_util.utcnow()
        self.async_write_ha_state()