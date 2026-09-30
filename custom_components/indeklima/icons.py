"""
Icon definitions for Indeklima integration.

Centralizes all emoji icons used across the integration (frontend & backend).
This ensures consistency and makes it easy to customize icons globally.
"""

# Sensor/Status Icons
ICON_TEMPERATURE = "🌡️"
ICON_HUMIDITY = "💧"
ICON_CO2 = "🌫️"
ICON_PRESSURE = "📊"
ICON_PM2_5 = "💨"
ICON_PM10 = "🌪️"

# Ventilation & Air Quality
ICON_VENTILATION_YES = "🌬️"
ICON_VENTILATION_OPTIONAL = "🤔"
ICON_VENTILATION_NO = "⏰"
ICON_AIR_QUALITY_GOOD = "🌿"
ICON_AIR_QUALITY_MODERATE = "💨"
ICON_AIR_QUALITY_POOR = "🚫"
ICON_AIR_QUALITY_CRITICAL = "☠️"

# Mold & Circulation
ICON_MOLD_LOW = "✅"
ICON_MOLD_MODERATE = "⚠️"
ICON_MOLD_HIGH = "🔴"
ICON_MOLD_CRITICAL = "⛔"
ICON_CIRCULATION_GOOD = "💨"
ICON_CIRCULATION_MODERATE = "🌪️"
ICON_CIRCULATION_POOR = "💨"

# Dehumidifier
ICON_DEHUMIDIFIER_YES = "💧"
ICON_DEHUMIDIFIER_OPTIONAL = "💦"
ICON_DEHUMIDIFIER_NO = "✓"

# Windows & Doors
ICON_WINDOW = "🪟"

# Trends
ICON_TREND_RISING = "📈"
ICON_TREND_FALLING = "📉"
ICON_TREND_STABLE = "→"

# Map of sensor types to icons (for dynamic use)
SENSOR_ICONS = {
    "temperature": ICON_TEMPERATURE,
    "humidity": ICON_HUMIDITY,
    "co2": ICON_CO2,
    "pressure": ICON_PRESSURE,
    "pm2_5": ICON_PM2_5,
    "pm10_0": ICON_PM10,
}

VENTILATION_ICONS = {
    "yes": ICON_VENTILATION_YES,
    "optional": ICON_VENTILATION_OPTIONAL,
    "no": ICON_VENTILATION_NO,
}

AIR_QUALITY_ICONS = {
    "good": ICON_AIR_QUALITY_GOOD,
    "moderate": ICON_AIR_QUALITY_MODERATE,
    "poor": ICON_AIR_QUALITY_POOR,
    "critical": ICON_AIR_QUALITY_CRITICAL,
}

MOLD_ICONS = {
    "low": ICON_MOLD_LOW,
    "moderate": ICON_MOLD_MODERATE,
    "high": ICON_MOLD_HIGH,
    "critical": ICON_MOLD_CRITICAL,
}

TREND_ICONS = {
    "rising": ICON_TREND_RISING,
    "falling": ICON_TREND_FALLING,
    "stable": ICON_TREND_STABLE,
}
