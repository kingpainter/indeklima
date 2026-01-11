"""The Indeklima integration.

Version: 2.2.0
"""
from __future__ import annotations

import logging
from datetime import timedelta
from collections import deque

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util
from homeassistant.helpers import device_registry as dr

from .const import (
    DOMAIN, 
    SCAN_INTERVAL, 
    TREND_WINDOW, 
    __version__,
    CONF_WINDOW_ENTITY,
    CONF_WINDOW_IS_OUTDOOR,
    CIRCULATION_BONUS,
    CIRCULATION_GOOD,
    CIRCULATION_MODERATE,
    CIRCULATION_POOR,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Indeklima from a config entry."""
    
    # Create coordinator
    coordinator = IndeklimaDataCoordinator(hass, entry)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Register devices
    await _async_setup_devices(hass, entry, coordinator)
    
    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Indeklima integration v%s setup completed", __version__)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok


async def _async_setup_devices(
    hass: HomeAssistant,
    entry: ConfigEntry,
    coordinator: IndeklimaDataCoordinator,
) -> None:
    """Set up devices for the integration."""
    device_registry = dr.async_get(hass)
    
    # Create main hub device
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{entry.entry_id}_hub")},
        name="Indeklima Hub",
        manufacturer="Indeklima",
        model="Climate Monitor v2",
        sw_version=__version__,
        configuration_url="https://github.com/kingpainter/indeklima",
    )
    
    # Create device for each room
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


class IndeklimaDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Indeklima data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )
        self.entry = entry
        self.rooms = entry.data.get("rooms", [])
        
        # Historical data for trends (stores last 30 mins of data)
        self._history_humidity = deque(maxlen=6)  # 6 * 5min = 30min
        self._history_co2 = deque(maxlen=6)
        self._history_severity = deque(maxlen=6)

    async def _async_update_data(self) -> dict:
        """Fetch data from sensors."""
        data = {
            "rooms": {},
            "averages": {},
            "severity": 0,
            "status": "God",
            "open_windows": [],  # Only outdoor windows
            "open_internal_doors": [],  # Internal doors between rooms
            "air_circulation": CIRCULATION_POOR,
            "trends": {},
        }
        
        total_humidity = []
        total_temperature = []
        total_co2 = []
        total_voc = []
        total_formaldehyde = []
        
        # Get thresholds
        humidity_max = self._get_humidity_threshold()
        co2_max = self.entry.options.get("co2_max", 1000)
        voc_max = self.entry.options.get("voc_max", 3.0)
        formaldehyde_max = self.entry.options.get("formaldehyde_max", 0.15)
        
        severity_score = 0
        total_outdoor_windows_open = 0
        total_internal_doors_open = 0
        
        # Process each room
        for room in self.rooms:
            room_name = room.get("name")
            room_data = {}
            
            # Get humidity (average if multiple sensors)
            if humidity_sensors := room.get("humidity_sensors", []):
                humidity_values = []
                for sensor in humidity_sensors:
                    state = self.hass.states.get(sensor)
                    if state and state.state not in ("unknown", "unavailable"):
                        try:
                            humidity_values.append(float(state.state))
                        except (ValueError, TypeError):
                            pass
                
                if humidity_values:
                    humidity = sum(humidity_values) / len(humidity_values)
                    room_data["humidity"] = humidity
                    room_data["humidity_sensors_count"] = len(humidity_values)
                    total_humidity.append(humidity)
                    
                    # Calculate severity
                    if humidity > humidity_max:
                        severity_score += (humidity - humidity_max) * 1.2
            
            # Get temperature (average if multiple sensors)
            if temperature_sensors := room.get("temperature_sensors", []):
                temperature_values = []
                for sensor in temperature_sensors:
                    state = self.hass.states.get(sensor)
                    if state and state.state not in ("unknown", "unavailable"):
                        try:
                            temperature_values.append(float(state.state))
                        except (ValueError, TypeError):
                            pass
                
                if temperature_values:
                    temperature = sum(temperature_values) / len(temperature_values)
                    room_data["temperature"] = temperature
                    room_data["temperature_sensors_count"] = len(temperature_values)
                    total_temperature.append(temperature)
            
            # Get CO2 (average if multiple sensors)
            if co2_sensors := room.get("co2_sensors", []):
                co2_values = []
                for sensor in co2_sensors:
                    state = self.hass.states.get(sensor)
                    if state and state.state not in ("unknown", "unavailable"):
                        try:
                            co2_values.append(float(state.state))
                        except (ValueError, TypeError):
                            pass
                
                if co2_values:
                    co2 = sum(co2_values) / len(co2_values)
                    room_data["co2"] = co2
                    room_data["co2_sensors_count"] = len(co2_values)
                    total_co2.append(co2)
                    
                    # Calculate severity
                    if co2 > co2_max:
                        severity_score += (co2 - co2_max) / 25
            
            # Get VOC (average if multiple sensors)
            if voc_sensors := room.get("voc_sensors", []):
                voc_values = []
                for sensor in voc_sensors:
                    state = self.hass.states.get(sensor)
                    if state and state.state not in ("unknown", "unavailable"):
                        try:
                            voc_values.append(float(state.state))
                        except (ValueError, TypeError):
                            pass
                
                if voc_values:
                    voc = sum(voc_values) / len(voc_values)
                    room_data["voc"] = voc
                    room_data["voc_sensors_count"] = len(voc_values)
                    total_voc.append(voc)
                    
                    # Convert ppb to mg/m³ and check threshold
                    voc_mg = voc * 0.0409
                    if voc_mg > voc_max:
                        severity_score += 10
            
            # Get Formaldehyde (average if multiple sensors)
            if formaldehyde_sensors := room.get("formaldehyde_sensors", []):
                formaldehyde_values = []
                for sensor in formaldehyde_sensors:
                    state = self.hass.states.get(sensor)
                    if state and state.state not in ("unknown", "unavailable"):
                        try:
                            formaldehyde_values.append(float(state.state))
                        except (ValueError, TypeError):
                            pass
                
                if formaldehyde_values:
                    formaldehyde = sum(formaldehyde_values) / len(formaldehyde_values)
                    room_data["formaldehyde"] = formaldehyde
                    room_data["formaldehyde_sensors_count"] = len(formaldehyde_values)
                    total_formaldehyde.append(formaldehyde)
                    
                    # Convert µg/m³ to mg/m³ and check threshold
                    formaldehyde_mg = formaldehyde / 1000
                    if formaldehyde_mg > formaldehyde_max:
                        severity_score += 10
            
            # NEW: Check window/door status with outdoor/indoor classification
            if window_sensors := room.get("window_sensors", []):
                room_outdoor_open = 0
                room_internal_open = 0
                
                for window in window_sensors:
                    # Handle both old format (string) and new format (dict)
                    if isinstance(window, str):
                        # Old format - assume outdoor by default for backward compatibility
                        entity_id = window
                        is_outdoor = True
                    elif isinstance(window, dict):
                        # New format
                        entity_id = window.get(CONF_WINDOW_ENTITY)
                        is_outdoor = window.get(CONF_WINDOW_IS_OUTDOOR, True)
                    else:
                        continue
                    
                    state = self.hass.states.get(entity_id)
                    if state and state.state == "off":  # off = open for contact sensors
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
                
                # Apply air circulation bonus if internal doors are open
                # This reduces severity by 5% as air can circulate better
                if room_internal_open > 0 and severity_score > 0:
                    severity_score *= CIRCULATION_BONUS
            
            # Calculate room status
            room_status = "God"
            if room_data.get("humidity", 0) > humidity_max * 0.9 or \
               room_data.get("co2", 0) > co2_max * 0.9:
                room_status = "Advarsel"
            if room_data.get("humidity", 0) > humidity_max or \
               room_data.get("co2", 0) > co2_max:
                room_status = "Dårlig"
            
            room_data["status"] = room_status
            data["rooms"][room_name] = room_data
        
        # Calculate averages
        if total_humidity:
            avg_humidity = round(sum(total_humidity) / len(total_humidity), 1)
            data["averages"]["humidity"] = avg_humidity
        
        if total_temperature:
            data["averages"]["temperature"] = round(sum(total_temperature) / len(total_temperature), 1)
        
        if total_co2:
            avg_co2 = round(sum(total_co2) / len(total_co2), 0)
            data["averages"]["co2"] = avg_co2
        
        if total_voc:
            data["averages"]["voc"] = round(sum(total_voc) / len(total_voc), 0)
        
        if total_formaldehyde:
            data["averages"]["formaldehyde"] = round(sum(total_formaldehyde) / len(total_formaldehyde), 0)
        
        # Calculate overall air circulation status
        if total_internal_doors_open >= 3:
            data["air_circulation"] = CIRCULATION_GOOD
        elif total_internal_doors_open >= 1:
            data["air_circulation"] = CIRCULATION_MODERATE
        else:
            data["air_circulation"] = CIRCULATION_POOR
        
        # Set severity
        data["severity"] = min(round(severity_score, 0), 100)
        
        # Set status
        if data["severity"] > 70:
            data["status"] = "Kritisk"
        elif data["severity"] > 40:
            data["status"] = "Advarsel"
        else:
            data["status"] = "God"
        
        # Store current values for trend calculation
        if total_humidity:
            self._history_humidity.append((dt_util.utcnow(), avg_humidity))
        if total_co2:
            self._history_co2.append((dt_util.utcnow(), avg_co2))
        self._history_severity.append((dt_util.utcnow(), data["severity"]))
        
        # Calculate trends
        data["trends"]["humidity"] = self._calculate_trend(self._history_humidity)
        data["trends"]["co2"] = self._calculate_trend(self._history_co2)
        data["trends"]["severity"] = self._calculate_trend(self._history_severity)
        
        # Calculate ventilation recommendation
        data["ventilation"] = await self._calculate_ventilation_recommendation(
            data, humidity_max, co2_max
        )
        
        return data
    
    def _calculate_trend(self, history: deque) -> str:
        """Calculate trend from historical data."""
        if len(history) < 2:
            return "Stabil"
        
        # Get current and historical average
        current = history[-1][1]
        
        # Calculate average from history (excluding current)
        historical_values = [v for _, v in list(history)[:-1]]
        if not historical_values:
            return "Stabil"
        
        historical_avg = sum(historical_values) / len(historical_values)
        
        # Calculate percentage change
        if historical_avg == 0:
            return "Stabil"
        
        change_percent = ((current - historical_avg) / historical_avg) * 100
        
        # Determine trend with 5% threshold
        if change_percent > 5:
            return "Stigende"
        elif change_percent < -5:
            return "Faldende"
        else:
            return "Stabil"
    
    def _get_humidity_threshold(self) -> float:
        """Get current humidity threshold based on season."""
        season_sensor = self.hass.states.get("sensor.season")
        if season_sensor and season_sensor.state == "summer":
            return self.entry.options.get("humidity_summer_max", 60)
        return self.entry.options.get("humidity_winter_max", 55)
    
    async def _calculate_ventilation_recommendation(
        self,
        data: dict,
        humidity_max: float,
        co2_max: float,
    ) -> dict:
        """Calculate ventilation recommendation based on conditions."""
        recommendation = {
            "status": "Nej",
            "reason": [],
            "rooms": [],
            "outdoor_temp": None,
            "outdoor_humidity": None,
        }
        
        # Check if OUTDOOR windows are already open (not internal doors)
        if data.get("open_windows"):
            recommendation["status"] = "Valgfrit"
            recommendation["reason"].append("Vinduer til udendørs allerede åbne")
            recommendation["rooms"] = data["open_windows"]
            return recommendation
        
        # Get weather data
        weather_entity = self.entry.options.get("weather_entity")
        if weather_entity:
            weather_state = self.hass.states.get(weather_entity)
        else:
            # Try default weather entity
            weather_state = self.hass.states.get("weather.home")
        
        if weather_state:
            try:
                recommendation["outdoor_temp"] = float(
                    weather_state.attributes.get("temperature", 0)
                )
                recommendation["outdoor_humidity"] = float(
                    weather_state.attributes.get("humidity", 0)
                )
            except (ValueError, TypeError):
                pass
        
        # Check indoor conditions
        indoor_problems = []
        problem_rooms = []
        
        avg_humidity = data.get("averages", {}).get("humidity", 0)
        avg_co2 = data.get("averages", {}).get("co2", 0)
        
        if avg_humidity > humidity_max:
            indoor_problems.append("Høj fugtighed")
        if avg_co2 > co2_max:
            indoor_problems.append("Høj CO2")
        
        # Check individual rooms
        for room_name, room_data in data.get("rooms", {}).items():
            if room_data.get("humidity", 0) > humidity_max:
                problem_rooms.append(room_name)
            elif room_data.get("co2", 0) > co2_max:
                if room_name not in problem_rooms:
                    problem_rooms.append(room_name)
        
        # Decide recommendation
        if not indoor_problems:
            recommendation["status"] = "Nej"
            recommendation["reason"].append("Godt indeklima")
            return recommendation
        
        # We have indoor problems - check outdoor conditions
        outdoor_temp = recommendation["outdoor_temp"]
        outdoor_humidity = recommendation["outdoor_humidity"]
        
        # If we don't have weather data, recommend ventilation based on indoor conditions
        if outdoor_temp is None:
            recommendation["status"] = "Ja"
            recommendation["reason"] = indoor_problems
            recommendation["rooms"] = problem_rooms
            return recommendation
        
        # Check if outdoor conditions are suitable
        too_cold = outdoor_temp < 5  # Below 5°C might be too cold
        too_humid = outdoor_humidity and outdoor_humidity > humidity_max
        
        if too_cold:
            recommendation["status"] = "Valgfrit"
            recommendation["reason"] = indoor_problems + ["Men: For koldt ude"]
            recommendation["rooms"] = problem_rooms
        elif too_humid:
            recommendation["status"] = "Nej"
            recommendation["reason"] = indoor_problems + ["Men: For fugtigt ude"]
        else:
            recommendation["status"] = "Ja"
            recommendation["reason"] = indoor_problems
            recommendation["rooms"] = problem_rooms
        
        return recommendation