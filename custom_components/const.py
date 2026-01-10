"""Constants for Indeklima integration.

Version: 2.1.0
"""
from typing import Final

__version__ = "2.1.0"

DOMAIN: Final = "indeklima"

# Configuration
CONF_ROOMS: Final = "rooms"
CONF_ROOM_NAME: Final = "name"
CONF_HUMIDITY_SENSORS: Final = "humidity_sensors"
CONF_TEMPERATURE_SENSORS: Final = "temperature_sensors"
CONF_CO2_SENSORS: Final = "co2_sensors"
CONF_VOC_SENSORS: Final = "voc_sensors"
CONF_FORMALDEHYDE_SENSORS: Final = "formaldehyde_sensors"
CONF_WINDOW_SENSORS: Final = "window_sensors"

# New device support
CONF_DEHUMIDIFIER: Final = "dehumidifier"
CONF_FAN: Final = "fan"
CONF_WEATHER_ENTITY: Final = "weather_entity"
CONF_NOTIFICATION_TARGETS: Final = "notification_targets"

# Thresholds
CONF_HUMIDITY_SUMMER_MAX: Final = "humidity_summer_max"
CONF_HUMIDITY_WINTER_MAX: Final = "humidity_winter_max"
CONF_CO2_MAX: Final = "co2_max"
CONF_VOC_MAX: Final = "voc_max"
CONF_FORMALDEHYDE_MAX: Final = "formaldehyde_max"

# Default values
DEFAULT_HUMIDITY_SUMMER_MAX: Final = 60
DEFAULT_HUMIDITY_WINTER_MAX: Final = 55
DEFAULT_CO2_MAX: Final = 1000
DEFAULT_VOC_MAX: Final = 3.0
DEFAULT_FORMALDEHYDE_MAX: Final = 0.15

# Sensor types
SENSOR_TYPES: Final = {
    "humidity_avg": {
        "name": "Gennemsnitlig Fugtighed",
        "unit": "%",
        "icon": "mdi:water-percent",
        "device_class": "humidity",
    },
    "temperature_avg": {
        "name": "Gennemsnitlig Temperatur",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "co2_avg": {
        "name": "Gennemsnitlig CO2",
        "unit": "ppm",
        "icon": "mdi:molecule-co2",
        "device_class": None,
    },
    "voc_avg": {
        "name": "Gennemsnitlig VOC",
        "unit": "ppb",
        "icon": "mdi:air-filter",
        "device_class": None,
    },
    "formaldehyde_avg": {
        "name": "Gennemsnitlig Formaldehyd",
        "unit": "µg/m³",
        "icon": "mdi:chemical-weapon",
        "device_class": None,
    },
    "severity": {
        "name": "Severity Score",
        "unit": "%",
        "icon": "mdi:alert-decagram",
        "device_class": None,
    },
    "severity_status": {
        "name": "Status",
        "unit": None,
        "icon": "mdi:home-thermometer",
        "device_class": None,
    },
    "open_windows": {
        "name": "Åbne Vinduer",
        "unit": "stk",
        "icon": "mdi:window-open",
        "device_class": None,
    },
    "trend_humidity": {
        "name": "Fugtigheds Trend",
        "unit": None,
        "icon": "mdi:trending-up",
        "device_class": None,
    },
    "trend_co2": {
        "name": "CO2 Trend",
        "unit": None,
        "icon": "mdi:trending-up",
        "device_class": None,
    },
    "trend_severity": {
        "name": "Severity Trend",
        "unit": None,
        "icon": "mdi:trending-up",
        "device_class": None,
    },
    "ventilation_recommendation": {
        "name": "Ventilationsanbefaling",
        "unit": None,
        "icon": "mdi:window-open-variant",
        "device_class": None,
    },
}

# Status levels
STATUS_GOOD: Final = "God"
STATUS_WARNING: Final = "Advarsel"
STATUS_CRITICAL: Final = "Dårlig"

# Seasons
SEASON_SUMMER: Final = "summer"
SEASON_WINTER: Final = "winter"

# Update interval
SCAN_INTERVAL: Final = 300
TREND_WINDOW: Final = 1800

# Notification cooldown
NOTIFICATION_COOLDOWN: Final = 7200

# Trend states
TREND_RISING: Final = "Stigende"
TREND_FALLING: Final = "Faldende"
TREND_STABLE: Final = "Stabil"

# Ventilation states
VENTILATION_YES: Final = "Ja"
VENTILATION_NO: Final = "Nej"
VENTILATION_OPTIONAL: Final = "Valgfrit"