"""Indeklima integration for Home Assistant.

Version: 2.2.0
"""
from __future__ import annotations

import logging
from datetime import timedelta, datetime
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import device_registry as dr

from .const import (
    DOMAIN,
    CONF_ROOMS,
    CONF_HUMIDITY_SENSORS,
    CONF_TEMPERATURE_SENSORS,
    CONF_CO2_SENSORS,
    CONF_VOC_SENSORS,
    CONF_FORMALDEHYDE_SENSORS,
    CONF_WINDOW_SENSORS,
    CONF_WINDOW_ENTITY,
    CONF_WINDOW_IS_OUTDOOR,
    CONF_WEATHER_ENTITY,
    CONF_HUMIDITY_SUMMER_MAX,
    CONF_HUMIDITY_WINTER_MAX,
    CONF_CO2_MAX,
    CONF_VOC_MAX,
    CONF_FORMALDEHYDE_MAX,
    DEFAULT_HUMIDITY_SUMMER_MAX,
    DEFAULT_HUMIDITY_WINTER_MAX,
    DEFAULT_CO2_MAX,
    DEFAULT_VOC_MAX,
    DEFAULT_FORMALDEHYDE_MAX,
    SCAN_INTERVAL,
    TREND_WINDOW,
    STATUS_GOOD,
    STATUS_WARNING,
    STATUS_CRITICAL,
    SEASON_SUMMER,
    SEASON_WINTER,
    TREND_RISING,
    TREND_FALLING,
    TREND_STABLE,
    VENTILATION_YES,
    VENTILATION_NO,
    VENTILATION_OPTIONAL,
    CIRCULATION_GOOD,
    CIRCULATION_MODERATE,
    CIRCULATION_POOR,
    CIRCULATION_BONUS,
    __version__,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Indeklima from a config entry."""
    coordinator = IndeklimaDataCoordinator(hass, entry)
    
    await coordinator.async_config_entry_first_refresh()
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Register devices
    device_registry = dr.async_get(hass)
    
    # Register hub device
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{entry.entry_id}_hub")},
        name="Indeklima Hub",
        manufacturer="Indeklima",
        model="Climate Monitor v2",
        sw_version=__version__,
    )
    
    # Register room devices
    for room in coordinator.rooms:
        room_name = room.get("name")
        room_id = room_name.lower().replace(" ", "_").replace("æ", "ae").replace("ø", "oe").replace("å", "aa")
        
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, f"{entry.entry_id}_room_{room_id}")},
            name=f"Indeklima {room_name}",
            manufacturer="Indeklima",
            model="Room Monitor",
            sw_version=__version__,
            via_device=(DOMAIN, f"{entry.entry_id}_hub"),
        )
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    _LOGGER.info("Indeklima integration v%s setup completed", __version__)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class IndeklimaDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Indeklima data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.rooms = entry.data.get(CONF_ROOMS, [])
        
        # Get thresholds from options
        self.humidity_summer_max = entry.options.get(
            CONF_HUMIDITY_SUMMER_MAX, DEFAULT_HUMIDITY_SUMMER_MAX
        )
        self.humidity_winter_max = entry.options.get(
            CONF_HUMIDITY_WINTER_MAX, DEFAULT_HUMIDITY_WINTER_MAX
        )
        self.co2_max = entry.options.get(CONF_CO2_MAX, DEFAULT_CO2_MAX)
        self.voc_max = entry.options.get(CONF_VOC_MAX, DEFAULT_VOC_MAX)
        self.formaldehyde_max = entry.options.get(
            CONF_FORMALDEHYDE_MAX, DEFAULT_FORMALDEHYDE_MAX
        )
        
        # Weather entity
        self.weather_entity = entry.options.get(CONF_WEATHER_ENTITY)
        
        # History for trends
        self.history: dict[str, list[tuple[datetime, float]]] = {
            "humidity": [],
            "co2": [],
            "severity": [],
        }
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    def _get_season(self) -> str:
        """Determine current season."""
        month = datetime.now().month
        if 5 <= month <= 9:
            return SEASON_SUMMER
        return SEASON_WINTER

    def _get_humidity_max(self) -> float:
        """Get max humidity based on season."""
        season = self._get_season()
        if season == SEASON_SUMMER:
            return self.humidity_summer_max
        return self.humidity_winter_max

    def _get_sensor_values(self, entity_ids: list[str]) -> list[float]:
        """Get numeric values from multiple sensors."""
        values = []
        for entity_id in entity_ids:
            state = self.hass.states.get(entity_id)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    values.append(float(state.state))
                except (ValueError, TypeError):
                    pass
        return values

    def _calculate_severity(self, room_data: dict) -> float:
        """Calculate severity score for a room (0-100, lower is better)."""
        severity = 0.0
        humidity_max = self._get_humidity_max()
        
        # Humidity severity (0-30 points)
        if "humidity" in room_data:
            humidity = room_data["humidity"]
            if humidity > humidity_max:
                excess = humidity - humidity_max
                severity += min(30, excess * 3)
        
        # CO2 severity (0-30 points)
        if "co2" in room_data:
            co2 = room_data["co2"]
            if co2 > self.co2_max:
                excess = co2 - self.co2_max
                severity += min(30, (excess / 1000) * 30)
        
        # VOC severity (0-20 points)
        if "voc" in room_data:
            voc = room_data["voc"]
            if voc > self.voc_max:
                excess = voc - self.voc_max
                severity += min(20, excess * 5)
        
        # Formaldehyde severity (0-20 points)
        if "formaldehyde" in room_data:
            formaldehyde = room_data["formaldehyde"]
            if formaldehyde > self.formaldehyde_max:
                excess = formaldehyde - self.formaldehyde_max
                severity += min(20, excess * 50)
        
        return min(100, severity)

    def _get_status_from_severity(self, severity: float) -> str:
        """Convert severity score to status."""
        if severity < 30:
            return STATUS_GOOD
        elif severity < 60:
            return STATUS_WARNING
        return STATUS_CRITICAL

    def _calculate_trend(self, key: str, current_value: float) -> str:
        """Calculate trend for a metric."""
        now = datetime.now()
        
        # Add current value to history
        self.history[key].append((now, current_value))
        
        # Remove old entries (older than TREND_WINDOW)
        cutoff = now - timedelta(seconds=TREND_WINDOW)
        self.history[key] = [
            (ts, val) for ts, val in self.history[key] if ts > cutoff
        ]
        
        # Need at least 2 data points
        if len(self.history[key]) < 2:
            return TREND_STABLE
        
        # Calculate linear regression slope
        timestamps = [(ts - now).total_seconds() for ts, _ in self.history[key]]
        values = [val for _, val in self.history[key]]
        
        n = len(timestamps)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_xx = sum(x * x for x in timestamps)
        
        denominator = n * sum_xx - sum_x * sum_x
        if denominator == 0:
            return TREND_STABLE
        
        slope = (n * sum_xy - sum_x * sum_y) / denominator
        
        # Determine trend based on slope
        threshold = 0.1  # Adjust sensitivity
        if slope > threshold:
            return TREND_RISING
        elif slope < -threshold:
            return TREND_FALLING
        return TREND_STABLE

    def _get_weather_data(self) -> dict[str, float]:
        """Get weather data for ventilation recommendation."""
        weather_data = {}
        
        if self.weather_entity:
            state = self.hass.states.get(self.weather_entity)
            if state:
                try:
                    weather_data["temperature"] = float(state.attributes.get("temperature", 0))
                    weather_data["humidity"] = float(state.attributes.get("humidity", 0))
                except (ValueError, TypeError):
                    pass
        
        return weather_data

    def _calculate_ventilation_recommendation(self, data: dict) -> dict:
        """Calculate ventilation recommendation."""
        recommendation = {
            "status": VENTILATION_NO,
            "reason": [],
            "rooms": [],
            "outdoor_temp": None,
            "outdoor_humidity": None,
        }
        
        # Check if any outdoor windows are open
        if data.get("open_windows"):
            recommendation["status"] = VENTILATION_OPTIONAL
            recommendation["reason"].append("Vinduer allerede åbne")
            return recommendation
        
        # Analyze indoor climate issues
        issues = []
        problem_rooms = []
        
        humidity_max = self._get_humidity_max()
        
        for room_name, room_data in data.get("rooms", {}).items():
            room_issues = []
            
            if "humidity" in room_data and room_data["humidity"] > humidity_max:
                room_issues.append("Høj fugtighed")
            
            if "co2" in room_data and room_data["co2"] > self.co2_max:
                room_issues.append("Høj CO2")
            
            if "voc" in room_data and room_data["voc"] > self.voc_max:
                room_issues.append("Høj VOC")
            
            if room_issues:
                issues.extend(room_issues)
                problem_rooms.append(room_name)
        
        if not issues:
            recommendation["status"] = VENTILATION_NO
            recommendation["reason"].append("Indeklima er OK")
            return recommendation
        
        # Get weather data
        weather = self._get_weather_data()
        
        if weather:
            recommendation["outdoor_temp"] = weather.get("temperature")
            recommendation["outdoor_humidity"] = weather.get("humidity")
            
            # Check if conditions are good for ventilation
            temp = weather.get("temperature", 20)
            humidity = weather.get("humidity", 50)
            
            if temp < 5:
                recommendation["status"] = VENTILATION_OPTIONAL
                recommendation["reason"].extend(issues)
                recommendation["reason"].append("For koldt ude")
            elif humidity > humidity_max:
                recommendation["status"] = VENTILATION_NO
                recommendation["reason"].extend(issues)
                recommendation["reason"].append("For fugtigt ude")
            else:
                recommendation["status"] = VENTILATION_YES
                recommendation["reason"].extend(issues)
        else:
            # No weather data - recommend based on indoor only
            recommendation["status"] = VENTILATION_YES
            recommendation["reason"].extend(issues)
        
        recommendation["rooms"] = problem_rooms
        return recommendation

    def _calculate_air_circulation(self, total_internal_doors: int) -> str:
        """Calculate air circulation status based on open internal doors."""
        if total_internal_doors >= 3:
            return CIRCULATION_GOOD
        elif total_internal_doors >= 1:
            return CIRCULATION_MODERATE
        return CIRCULATION_POOR

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from sensors."""
        data = {
            "rooms": {},
            "averages": {},
            "severity": 0,
            "status": STATUS_GOOD,
            "open_windows": [],
            "open_internal_doors": [],
            "air_circulation": CIRCULATION_POOR,
            "trends": {},
            "ventilation": {},
        }
        
        all_humidity = []
        all_temperature = []
        all_co2 = []
        all_voc = []
        all_formaldehyde = []
        all_severity = []
        
        total_outdoor_windows_open = 0
        total_internal_doors_open = 0
        
        # Process each room
        for room in self.rooms:
            room_name = room.get("name")
            room_data = {}
            
            # Humidity sensors
            if humidity_sensors := room.get(CONF_HUMIDITY_SENSORS):
                values = self._get_sensor_values(humidity_sensors)
                if values:
                    avg = sum(values) / len(values)
                    room_data["humidity"] = avg
                    room_data["humidity_sensors_count"] = len(values)
                    all_humidity.append(avg)
            
            # Temperature sensors
            if temp_sensors := room.get(CONF_TEMPERATURE_SENSORS):
                values = self._get_sensor_values(temp_sensors)
                if values:
                    avg = sum(values) / len(values)
                    room_data["temperature"] = avg
                    room_data["temperature_sensors_count"] = len(values)
                    all_temperature.append(avg)
            
            # CO2 sensors
            if co2_sensors := room.get(CONF_CO2_SENSORS):
                values = self._get_sensor_values(co2_sensors)
                if values:
                    avg = sum(values) / len(values)
                    room_data["co2"] = avg
                    room_data["co2_sensors_count"] = len(values)
                    all_co2.append(avg)
            
            # VOC sensors
            if voc_sensors := room.get(CONF_VOC_SENSORS):
                values = self._get_sensor_values(voc_sensors)
                if values:
                    avg = sum(values) / len(values)
                    room_data["voc"] = avg
                    room_data["voc_sensors_count"] = len(values)
                    all_voc.append(avg)
            
            # Formaldehyde sensors
            if formaldehyde_sensors := room.get(CONF_FORMALDEHYDE_SENSORS):
                values = self._get_sensor_values(formaldehyde_sensors)
                if values:
                    avg = sum(values) / len(values)
                    room_data["formaldehyde"] = avg
                    room_data["formaldehyde_sensors_count"] = len(values)
                    all_formaldehyde.append(avg)
            
            # Window/door sensors - FIXED LOGIC
            if window_sensors := room.get(CONF_WINDOW_SENSORS, []):
                room_outdoor_open = 0
                room_internal_open = 0
                
                for window in window_sensors:
                    # Handle both old string format and new dict format
                    if isinstance(window, str):
                        entity_id = window
                        is_outdoor = True  # Backward compatibility
                    elif isinstance(window, dict):
                        entity_id = window.get(CONF_WINDOW_ENTITY)
                        is_outdoor = window.get(CONF_WINDOW_IS_OUTDOOR, True)
                    else:
                        continue
                    
                    state = self.hass.states.get(entity_id)
                    if state and state.state == "on":  # ✅ FIXED: on = open
                        if is_outdoor:
                            room_outdoor_open += 1
                            total_outdoor_windows_open += 1
                            if room_name not in data["open_windows"]:
                                data["open_windows"].append(room_name)
                        else:
                            room_internal_open += 1
                            total_internal_doors_open += 1
                            if room_name not in data["open_internal_doors"]:
                                data["open_internal_doors"].append(room_name)
                
                room_data["outdoor_windows_open"] = room_outdoor_open
                room_data["internal_doors_open"] = room_internal_open
            
            # Calculate room severity
            severity = self._calculate_severity(room_data)
            room_data["severity"] = severity
            room_data["status"] = self._get_status_from_severity(severity)
            all_severity.append(severity)
            
            data["rooms"][room_name] = room_data
        
        # Calculate global averages
        if all_humidity:
            data["averages"]["humidity"] = sum(all_humidity) / len(all_humidity)
        if all_temperature:
            data["averages"]["temperature"] = sum(all_temperature) / len(all_temperature)
        if all_co2:
            data["averages"]["co2"] = sum(all_co2) / len(all_co2)
        if all_voc:
            data["averages"]["voc"] = sum(all_voc) / len(all_voc)
        if all_formaldehyde:
            data["averages"]["formaldehyde"] = sum(all_formaldehyde) / len(all_formaldehyde)
        
        # Calculate global severity
        if all_severity:
            global_severity = sum(all_severity) / len(all_severity)
            
            # Apply air circulation bonus
            if total_internal_doors_open > 0:
                global_severity *= CIRCULATION_BONUS  # 5% reduction
            
            data["severity"] = round(global_severity, 1)
            data["status"] = self._get_status_from_severity(global_severity)
        
        # Calculate air circulation
        data["air_circulation"] = self._calculate_air_circulation(total_internal_doors_open)
        
        # Calculate trends
        if all_humidity:
            data["trends"]["humidity"] = self._calculate_trend(
                "humidity", sum(all_humidity) / len(all_humidity)
            )
        if all_co2:
            data["trends"]["co2"] = self._calculate_trend(
                "co2", sum(all_co2) / len(all_co2)
            )
        if all_severity:
            data["trends"]["severity"] = self._calculate_trend(
                "severity", data["severity"]
            )
        
        # Calculate ventilation recommendation
        data["ventilation"] = self._calculate_ventilation_recommendation(data)
        
        return data