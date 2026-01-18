"""Constants for Indeklima integration.

Version: 2.3.2
"""
from typing import Final

__version__ = "2.3.2"

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

# Window/Door configuration
CONF_WINDOW_ENTITY: Final = "entity_id"
CONF_WINDOW_IS_OUTDOOR: Final = "is_outdoor"

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

# Sensor types (Hub sensors)
SENSOR_TYPES: Final = {
    "humidity_avg": {
        "name": "Average Humidity",
        "unit": "%",
        "icon": "mdi:water-percent",
        "device_class": "humidity",
    },
    "temperature_avg": {
        "name": "Average Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "co2_avg": {
        "name": "Average CO2",
        "unit": "ppm",
        "icon": "mdi:molecule-co2",
        "device_class": None,
    },
    "voc_avg": {
        "name": "Average VOC",
        "unit": "ppb",
        "icon": "mdi:air-filter",
        "device_class": None,
    },
    "formaldehyde_avg": {
        "name": "Average Formaldehyde",
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
        "name": "Open Windows",
        "unit": "count",
        "icon": "mdi:window-open",
        "device_class": None,
    },
    "air_circulation": {
        "name": "Air Circulation",
        "unit": None,
        "icon": "mdi:fan",
        "device_class": None,
    },
    "trend_humidity": {
        "name": "Humidity Trend",
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
        "name": "Ventilation Recommendation",
        "unit": None,
        "icon": "mdi:window-open-variant",
        "device_class": None,
    },
}

# Room sensor types (per-room individual sensors)
ROOM_SENSOR_TYPES: Final = {
    "status": {
        "name": "Status",
        "unit": None,
        "icon": "mdi:home-thermometer",
        "device_class": None,
    },
    "temperature": {
        "name": "Temperature",
        "unit": "°C",
        "icon": "mdi:thermometer",
        "device_class": "temperature",
    },
    "humidity": {
        "name": "Humidity",
        "unit": "%",
        "icon": "mdi:water-percent",
        "device_class": "humidity",
    },
    "co2": {
        "name": "CO2",
        "unit": "ppm",
        "icon": "mdi:molecule-co2",
        "device_class": "carbon_dioxide",
    },
}

# Status levels (English - translated via strings.json)
STATUS_GOOD: Final = "good"
STATUS_WARNING: Final = "warning"
STATUS_CRITICAL: Final = "critical"

# Seasons
SEASON_SUMMER: Final = "summer"
SEASON_WINTER: Final = "winter"

# Update interval
SCAN_INTERVAL: Final = 300
TREND_WINDOW: Final = 1800

# Notification cooldown
NOTIFICATION_COOLDOWN: Final = 7200

# Trend states (English - translated via strings.json)
TREND_RISING: Final = "rising"
TREND_FALLING: Final = "falling"
TREND_STABLE: Final = "stable"

# Ventilation states (English - translated via strings.json)
VENTILATION_YES: Final = "yes"
VENTILATION_NO: Final = "no"
VENTILATION_OPTIONAL: Final = "optional"

# Air circulation states (English - translated via strings.json)
CIRCULATION_GOOD: Final = "good"
CIRCULATION_MODERATE: Final = "moderate"
CIRCULATION_POOR: Final = "poor"

# Severity bonus for air circulation
CIRCULATION_BONUS: Final = 0.95  # 5% reduction in severity


def normalize_room_id(room_name: str) -> str:
    """Normalize room name to create consistent room ID.
    
    This ensures device registry and entity unique_ids match perfectly.
    Handles Danish characters: æ, ø, å
    """
    normalized = room_name.lower().replace(" ", "_")
    
    # Danish character replacements
    danish_chars = {
        "æ": "ae", "ø": "oe", "å": "aa",
        "Æ": "ae", "Ø": "oe", "Å": "aa",
    }
    
    for danish, replacement in danish_chars.items():
        normalized = normalized.replace(danish, replacement)
    
    return normalized
