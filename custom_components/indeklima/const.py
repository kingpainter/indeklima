"""Constants for Indeklima integration.

Version: 2.9.0
"""
from typing import Final
import re
import unicodedata

__version__ = "2.9.0"

DOMAIN: Final = "indeklima"

# ── Configuration keys ────────────────────────────────────────────────────────
CONF_ROOMS: Final = "rooms"
CONF_HUMIDITY_SENSORS: Final = "humidity_sensors"
CONF_TEMPERATURE_SENSORS: Final = "temperature_sensors"
CONF_CO2_SENSORS: Final = "co2_sensors"
CONF_VOC_SENSORS: Final = "voc_sensors"
CONF_FORMALDEHYDE_SENSORS: Final = "formaldehyde_sensors"
CONF_PRESSURE_SENSORS: Final = "pressure_sensors"
CONF_MOLD_SENSORS: Final = "mold_sensors"
CONF_WINDOW_SENSORS: Final = "window_sensors"
CONF_WINDOW_ENTITY: Final = "entity_id"
CONF_WINDOW_IS_OUTDOOR: Final = "is_outdoor"
CONF_DEHUMIDIFIER: Final = "dehumidifier"
CONF_DEHUMIDIFIER_LED: Final = "dehumidifier_led"
CONF_DEHUMIDIFIER_BUTTON: Final = "dehumidifier_button"
CONF_FAN: Final = "fan"
CONF_WEATHER_ENTITY: Final = "weather_entity"
CONF_NOTIFICATION_TARGETS: Final = "notification_targets"
CONF_HUMIDITY_SUMMER_MAX: Final = "humidity_summer_max"
CONF_HUMIDITY_WINTER_MAX: Final = "humidity_winter_max"
CONF_CO2_MAX: Final = "co2_max"
CONF_VOC_MAX: Final = "voc_max"
CONF_FORMALDEHYDE_MAX: Final = "formaldehyde_max"
CONF_MOLD_RISK_HUMIDITY: Final = "mold_risk_humidity"
CONF_MOLD_RISK_TEMP_MIN: Final = "mold_risk_temp_min"
CONF_MOLD_RISK_TEMP_MAX: Final = "mold_risk_temp_max"

# Quiet hours (hub-level default, entry.options)
CONF_QUIET_HOURS_START: Final = "quiet_hours_start"
CONF_QUIET_HOURS_END: Final = "quiet_hours_end"

# Quiet hours override (per room, stored on the room dict)
CONF_ROOM_QUIET_HOURS_START: Final = "quiet_hours_start"
CONF_ROOM_QUIET_HOURS_END: Final = "quiet_hours_end"

# Dehumidifier auto-off duration (per room, stored on the room dict)
CONF_DEHUMIDIFIER_ON_DURATION: Final = "dehumidifier_on_duration"

# Per-room LED critical-alarm severity threshold override (optional; falls back
# to DEFAULT_LED_CRITICAL_SEVERITY). LED-only -- does NOT affect the room's
# official severity/status classification used elsewhere (status sensor etc.)
CONF_ROOM_LED_CRITICAL_SEVERITY: Final = "led_critical_severity"

# ── Defaults ──────────────────────────────────────────────────────────────────
DEFAULT_HUMIDITY_SUMMER_MAX: Final = 60   # %
DEFAULT_HUMIDITY_WINTER_MAX: Final = 55   # %
DEFAULT_CO2_MAX: Final = 1000             # ppm
DEFAULT_VOC_MAX: Final = 3.0             # mg/m³
DEFAULT_FORMALDEHYDE_MAX: Final = 0.15   # mg/m³
DEFAULT_MOLD_RISK_HUMIDITY: Final = 70   # %
DEFAULT_MOLD_RISK_TEMP_MIN: Final = 5    # °C
DEFAULT_MOLD_RISK_TEMP_MAX: Final = 35   # °C
DEFAULT_QUIET_HOURS_START: Final = 23    # 23:00, matches previous hardcoded behaviour
DEFAULT_QUIET_HOURS_END: Final = 6       # 06:00, matches previous hardcoded behaviour
DEFAULT_DEHUMIDIFIER_ON_DURATION: Final = 45  # minutes

# LED critical-alarm behaviour
DEFAULT_LED_CRITICAL_SEVERITY: Final = 60  # matches the global STATUS_CRITICAL threshold by default
DEHUM_LED_BLINK_INTERVAL: Final = 3        # seconds between blink toggles while in alarm
DEHUM_LED_RECOVERY_CYCLES: Final = 2       # consecutive non-critical update cycles required before the alarm clears (avoids flicker around the threshold)

SCAN_INTERVAL: Final = 30        # seconds
TREND_WINDOW: Final = 1800       # seconds (30 min)
NOTIFICATION_COOLDOWN: Final = 7200  # seconds (2 hours)
CIRCULATION_BONUS: Final = 0.95  # 5% severity reduction

# ── Status constants ──────────────────────────────────────────────────────────
STATUS_GOOD: Final = "good"
STATUS_WARNING: Final = "warning"
STATUS_CRITICAL: Final = "critical"

SEASON_SUMMER: Final = "summer"
SEASON_WINTER: Final = "winter"

TREND_RISING: Final = "rising"
TREND_FALLING: Final = "falling"
TREND_STABLE: Final = "stable"

VENTILATION_YES: Final = "yes"
VENTILATION_NO: Final = "no"
VENTILATION_OPTIONAL: Final = "optional"

CIRCULATION_GOOD: Final = "good"
CIRCULATION_MODERATE: Final = "moderate"
CIRCULATION_POOR: Final = "poor"

MOLD_RISK_LOW: Final = "low"
MOLD_RISK_MODERATE: Final = "moderate"
MOLD_RISK_HIGH: Final = "high"
MOLD_RISK_CRITICAL: Final = "critical"

DEHUMIDIFIER_YES: Final = "yes"
DEHUMIDIFIER_NO: Final = "no"
DEHUMIDIFIER_OPTIONAL: Final = "optional"

# Dehumidifier control mode (actual switch control, not just recommendation)
DEHUM_MODE_MANUAL: Final = "manual"
DEHUM_MODE_AUTO: Final = "auto"
DEHUM_MODE_OFF: Final = "off"

# ── Sensor type definitions ───────────────────────────────────────────────────
SENSOR_TYPES: Final[dict] = {
    "humidity_avg": {
        "name": "Average Humidity",
        "icon": "mdi:water-percent",
        "unit": "%",
        "device_class": "humidity",
    },
    "temperature_avg": {
        "name": "Average Temperature",
        "icon": "mdi:thermometer",
        "unit": "°C",
        "device_class": "temperature",
    },
    "co2_avg": {
        "name": "Average CO2",
        "icon": "mdi:molecule-co2",
        "unit": "ppm",
        "device_class": "carbon_dioxide",
    },
    "voc_avg": {
        "name": "Average VOC",
        "icon": "mdi:air-filter",
        "unit": "mg/m³",
    },
    "formaldehyde_avg": {
        "name": "Average Formaldehyde",
        "icon": "mdi:chemical-weapon",
        "unit": "mg/m³",
    },
    "pressure_avg": {
        "name": "Average Pressure",
        "icon": "mdi:gauge",
        "unit": "hPa",
        "device_class": "atmospheric_pressure",
    },
    "severity": {
        "name": "Severity Score",
        "icon": "mdi:gauge",
        "unit": None,
    },
    "severity_status": {
        "name": "Status",
        "icon": "mdi:check-circle",
        "unit": None,
    },
    "open_windows": {
        "name": "Open Windows",
        "icon": "mdi:window-open",
        "unit": None,
    },
    "air_circulation": {
        "name": "Air Circulation",
        "icon": "mdi:air-conditioner",
        "unit": None,
    },
    "ventilation_recommendation": {
        "name": "Ventilation Recommendation",
        "icon": "mdi:home-thermometer",
        "unit": None,
    },
    "mold_risk_avg": {
        "name": "Mold Risk",
        "icon": "mdi:mushroom",
        "unit": None,
    },
    "dehumidifier_recommendation": {
        "name": "Dehumidifier Recommendation",
        "icon": "mdi:air-humidifier",
        "unit": None,
    },
    "trend_humidity": {
        "name": "Humidity Trend",
        "icon": "mdi:trending-up",
        "unit": None,
    },
    "trend_co2": {
        "name": "CO2 Trend",
        "icon": "mdi:trending-up",
        "unit": None,
    },
    "trend_severity": {
        "name": "Severity Trend",
        "icon": "mdi:trending-up",
        "unit": None,
    },
}

ROOM_SENSOR_TYPES: Final[dict] = {
    "temperature": {
        "name": "Temperature",
        "icon": "mdi:thermometer",
        "unit": "°C",
        "device_class": "temperature",
    },
    "humidity": {
        "name": "Humidity",
        "icon": "mdi:water-percent",
        "unit": "%",
        "device_class": "humidity",
    },
    "co2": {
        "name": "CO2",
        "icon": "mdi:molecule-co2",
        "unit": "ppm",
        "device_class": "carbon_dioxide",
    },
    "pressure": {
        "name": "Pressure",
        "icon": "mdi:gauge",
        "unit": "hPa",
        "device_class": "atmospheric_pressure",
    },
    "mold_risk": {
        "name": "Mold Risk",
        "icon": "mdi:mushroom",
        "unit": None,
    },
    "dehumidifier_recommendation": {
        "name": "Dehumidifier Recommendation",
        "icon": "mdi:air-humidifier",
        "unit": None,
    },
}

# ── Helper functions ──────────────────────────────────────────────────────────
_DANISH_MAP: Final = {
    "æ": "ae",
    "ø": "oe",
    "å": "aa",
    "Æ": "ae",
    "Ø": "oe",
    "Å": "aa",
}


def normalize_room_id(name: str | None) -> str:
    """Normalize a room name to a safe entity/device ID.

    Handles Danish characters (ae/oe/aa) and converts spaces to underscores.

    Examples:
        'Stue'           -> 'stue'
        'Lukas Værelse'  -> 'lukas_vaerelse'
        'Køkken'         -> 'koekken'
        'Badværelse'      -> 'badvaerelse'
    """
    if not name:
        return "unknown"
    result = name.lower()
    for danish, replacement in _DANISH_MAP.items():
        result = result.replace(danish.lower(), replacement)
    # Replace remaining non-ASCII with their closest ASCII equivalent
    result = unicodedata.normalize("NFKD", result)
    result = result.encode("ascii", "ignore").decode("ascii")
    # Replace whitespace and non-word chars with underscores
    result = re.sub(r"[\s\W]+", "_", result)
    result = result.strip("_")
    return result
