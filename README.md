# 🏠 Indeklima - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Version](https://img.shields.io/badge/version-2.3.1-blue.svg)](https://github.com/kingpainter/indeklima)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Advanced indoor climate monitoring for Home Assistant with multi-room support, intelligent severity scoring, trend analysis, and ventilation recommendations.

**Current Version:** 2.3.1  
**Quality Scale:** Silver Tier ⭐️

---

## ✨ Features

### ✅ Implemented (v2.3.1)

#### 🪟 Window & Door Tracking
- **Indoor/Outdoor Classification** - Distinguish between outdoor windows and internal doors
- **Smart Window Detection** - Outdoor windows used for ventilation recommendations
- **Air Circulation Tracking** - Internal doors used for air circulation calculation
- **Flexible Configuration** - Easy to specify which openings lead outdoors

#### 🌬️ Air Circulation System
- **Air Circulation Sensor** - Monitor air circulation between rooms (Good/Moderate/Poor)
- **Severity Bonus** - 5% reduction in severity score with good air circulation
- **Real-time Monitoring** - See which internal doors are open
- **Room-by-room Status** - Each room shows number of open doors and windows

#### 🌡️ Climate Monitoring
- **Multi-room monitoring** - Track humidity, temperature, CO2, VOC, and formaldehyde
- **Intelligent severity scoring** - Automatic indoor climate quality calculation (0-100)
- **Multiple sensors per room** - Use multiple sensors of same type - average calculated automatically
- **Season-based thresholds** - Different limits for summer and winter

#### 📈 Trend Analysis
- **30-minute trends** - Rising/Falling/Stable for humidity, CO2, and severity
- **Historical tracking** - Automatic history with 6 data points
- **Smart alerts** - Get notified when trends are negative

#### 🌬️ Ventilation Recommendations (v2.1)
- **Smart recommendations** - Yes/No/Optional based on indoor climate and weather
- **Weather integration** - Takes outdoor temperature and humidity into account
- **Room-specific** - Shows precisely which rooms need ventilation
- **Reasoning** - Explains why you should or shouldn't ventilate

#### 🏠 Configuration & Management
- **Per-room configuration** - Add, edit, and delete rooms individually
- **Full options flow** - Manage everything after installation via UI
- **Device organization** - Modern hub + room device structure
- **Multi-language** - Danish and English support

#### 🤖 Automation Ready
- **Automation Blueprint** - Ready-made notification automation with cooldown (v2.1)
- **Dehumidifier support** - Ready for future automatic control
- **Fan/Ventilator support** - Ready for future automatic control
- **Smart cooldown** - Avoid too many notifications with last_notified tracking

#### 🔧 Technical Excellence (v2.3.1)
- **English Constants** - All code uses English, translations via JSON files
- **Per-Room Metric Sensors** - Separate temperature, humidity, CO2 sensors per room
- **Better Device Classes** - Proper HA device classes for perfect UI integration
- **Backward Compatible** - Status sensor attributes preserved for existing dashboards

### 🚧 Planned (v2.4+)
- 📱 Automatic device control (dehumidifiers, fans)
- 🎯 Diagnostics platform (Gold tier)
- 🔗 Integration with ventilation systems
- 🧠 Machine learning patterns
- ⚡ Energy optimization

---

## 📦 Installation

### Via HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in top right
4. Select "Custom repositories"
5. Add: `https://github.com/kingpainter/indeklima`
6. Category: "Integration"
7. Click "Add"
8. Find "Indeklima" and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Download latest release from [GitHub Releases](https://github.com/kingpainter/indeklima/releases)
2. Unpack the zip file
3. Copy `custom_components/indeklima` to your Home Assistant `custom_components` folder
4. Restart Home Assistant

---

## ⚙️ Configuration

### Initial Setup

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Indeklima"
4. Follow setup wizard:
   - Give integration a name
   - Add rooms one by one
   - Select sensors per room
   - Configure which windows/doors lead outdoors
   - Select optional devices (dehumidifier, fan)

### Per-Room Configuration

For each room you can select:

- **Humidity sensors** (0-many) - Average calculated automatically
- **Temperature sensors** (0-many)
- **CO2 sensors** (0-many)
- **VOC sensors** (0-many)
- **Formaldehyde sensors** (0-many)
- **Window/Door sensors** (0-many) - Mark which ones lead outdoors
- **Dehumidifier** (optional) - Ready for future automation
- **Fan/Ventilator** (optional) - Ready for future automation
- **Notification targets** (0-many) - Who gets notified about this room?

### Window/Door Classification

After selecting window sensors, you must specify which lead outdoors:

- ✅ **Checked** = Outdoor window/door (used for ventilation)
- ❌ **Unchecked** = Internal door (used for air circulation)

**Examples:**
- Living room window → ✅ Outdoor (leads to fresh air)
- Balcony door → ✅ Outdoor (leads to outdoors)
- Bathroom door → ❌ Internal (between rooms)
- Walk-in closet door → ❌ Internal (between rooms)

---

## 📊 Sensors

### Hub Sensors (Indeklima Hub device)

Global sensors that aggregate data from all rooms:

| Sensor | Description | Unit |
|--------|-------------|------|
| `sensor.indeklima_hub_severity_score` | Overall indoor climate score | 0-100 |
| `sensor.indeklima_hub_status` | Good/Warning/Critical | - |
| `sensor.indeklima_hub_average_humidity` | Average across rooms | % |
| `sensor.indeklima_hub_average_temperature` | Average across rooms | °C |
| `sensor.indeklima_hub_average_co2` | Average across rooms | ppm |
| `sensor.indeklima_hub_average_voc` | Average across rooms | ppb |
| `sensor.indeklima_hub_average_formaldehyde` | Average across rooms | µg/m³ |
| `sensor.indeklima_hub_open_windows` | Number of open OUTDOOR windows | count |
| `sensor.indeklima_hub_air_circulation` | **NEW v2.2!** Good/Moderate/Poor | - |
| `sensor.indeklima_hub_humidity_trend` | Rising/Falling/Stable (30 min) | - |
| `sensor.indeklima_hub_co2_trend` | Rising/Falling/Stable (30 min) | - |
| `sensor.indeklima_hub_severity_trend` | Rising/Falling/Stable (30 min) | - |
| `sensor.indeklima_hub_ventilation_recommendation` | **v2.1** Yes/No/Optional | - |

### Room Sensors

For each room, a device is created with multiple sensors:

#### Status Sensor (Always)
**Example:** `sensor.indeklima_living_room_status`

**State:** Good/Warning/Critical

**Attributes:**
```yaml
humidity: 55.5                    # Average if multiple sensors
humidity_sensors_count: 2         # Number of sensors used
temperature: 21.3
temperature_sensors_count: 1
co2: 850
co2_sensors_count: 1
voc: 120
voc_sensors_count: 1
formaldehyde: 45
formaldehyde_sensors_count: 1
outdoor_windows_open: 0           # NEW v2.2!
internal_doors_open: 1            # NEW v2.2!
air_circulation_bonus: true       # NEW v2.2! - True if internal doors open
last_notified: "2025-01-18T14:30:00+00:00"  # v2.1 - For cooldown
```

#### Per-Room Metric Sensors (v2.3.0+)

If room has sensors configured:

**Temperature:** `sensor.indeklima_living_room_temperature`
- State: Average temperature (°C)
- Device class: `temperature`
- Attributes: `sensors_used: 2`

**Humidity:** `sensor.indeklima_living_room_humidity`
- State: Average humidity (%)
- Device class: `humidity`
- Attributes: `sensors_used: 2`

**CO2:** `sensor.indeklima_living_room_co2`
- State: Average CO2 (ppm)
- Device class: `carbon_dioxide`
- Attributes: `sensors_used: 1`

---

## 🌬️ Air Circulation (NEW in v2.2!)

### Sensor: `sensor.indeklima_hub_air_circulation`

This sensor monitors air circulation between rooms based on open internal doors.

**States:**
- **Good** - 3+ internal doors open (good air circulation between rooms)
- **Moderate** - 1-2 internal doors open (moderate circulation)
- **Poor** - No internal doors open (poor circulation)

**Attributes:**
```yaml
internal_doors_open: 2
rooms_with_open_doors: "Living Room, Bathroom"
```

**Impact:**
- Good air circulation gives **5% severity bonus**
- Better distribution of heat and humidity between rooms
- Lower risk of local problems

### Dashboard Example

```yaml
type: custom:mushroom-template-card
primary: |
  {% set circ = states('sensor.indeklima_hub_air_circulation') %}
  {% if circ == 'good' %}
    🌬️ Good air circulation
  {% elif circ == 'moderate' %}
    🌀 Moderate air circulation
  {% else %}
    🚪 Poor air circulation
  {% endif %}
secondary: |
  {{ state_attr('sensor.indeklima_hub_air_circulation', 'internal_doors_open') }} doors open
  
  {% set rooms = state_attr('sensor.indeklima_hub_air_circulation', 'rooms_with_open_doors') %}
  {% if rooms != 'None' %}
  Rooms: {{ rooms }}
  {% endif %}
icon: |
  {% set circ = states('sensor.indeklima_hub_air_circulation') %}
  {% if circ == 'good' %}mdi:fan
  {% elif circ == 'moderate' %}mdi:fan-speed-2
  {% else %}mdi:fan-off{% endif %}
icon_color: |
  {% set circ = states('sensor.indeklima_hub_air_circulation') %}
  {% if circ == 'good' %}green
  {% elif circ == 'moderate' %}orange
  {% else %}red{% endif %}
```

---

## 🌬️ Ventilation Recommendations (v2.1)

### Sensor: `sensor.indeklima_hub_ventilation_recommendation`

Smart sensor that analyzes indoor climate and weather conditions to give intelligent ventilation recommendations.

**States:**
- **Yes** - You should ventilate now (good conditions, indoor problems)
- **No** - Wait to ventilate (poor outdoor conditions)
- **Optional** - Up to you (windows already open or borderline case)

**Attributes:**
```yaml
reason: "High humidity, High CO2"
rooms: "Living Room, Kitchen"
outdoor_temperature: 12.5
outdoor_humidity: 65
```

### Decision Logic

1. **Check if windows are open** (outdoor only!)
   - If yes → Status: "Optional" (already ventilating)

2. **Analyze indoor climate**
   - Humidity > max → Problem
   - CO2 > max → Problem
   - VOC > max → Problem

3. **Check weather conditions** (if configured)
   - Temperature < 5°C → "Optional" (too cold)
   - Humidity > max → "No" (too humid outside)
   - Otherwise → "Yes" (good conditions)

### Dashboard Example

```yaml
type: custom:mushroom-template-card
primary: |
  {% set status = states('sensor.indeklima_hub_ventilation_recommendation') %}
  {% if status == 'yes' %}
    🌬️ Ventilate now!
  {% elif status == 'optional' %}
    🤔 Consider ventilating
  {% else %}
    ⏳ Wait to ventilate
  {% endif %}
secondary: |
  {{ state_attr('sensor.indeklima_hub_ventilation_recommendation', 'reason') }}
  
  {% set rooms = state_attr('sensor.indeklima_hub_ventilation_recommendation', 'rooms') %}
  {% if rooms and rooms != 'None specific' %}
  **Rooms:** {{ rooms }}
  {% endif %}
icon: |
  {% set status = states('sensor.indeklima_hub_ventilation_recommendation') %}
  {% if status == 'yes' %}mdi:window-open-variant
  {% elif status == 'optional' %}mdi:window-open
  {% else %}mdi:window-closed{% endif %}
icon_color: |
  {% set status = states('sensor.indeklima_hub_ventilation_recommendation') %}
  {% if status == 'yes' %}green
  {% elif status == 'optional' %}orange
  {% else %}red{% endif %}
```

---

## 🔔 Notifications (v2.1+)

### Automation Blueprint

Indeklima includes a ready-made automation blueprint for per-room notifications:

**Features:**
- ✅ Per-room notifications
- ✅ Smart cooldown (avoid spam)
- ✅ Time control (only during business hours)
- ✅ Severity threshold (only on Warning/Critical)
- ✅ Includes ventilation tips

**Installation:**
1. Copy `blueprints/automation/indeklima/room_notification.yaml` to `config/blueprints/automation/indeklima/`
2. Restart Home Assistant or reload blueprints

**Usage:**
1. Go to Settings → Automations & Scenes → Blueprints
2. Find "Indeklima - Room Notification (v2.3.1)"
3. Click "Create Automation"
4. Configure room and settings

**Note:** v2.3.1 requires updated blueprint! See [BLUEPRINT_MIGRATION.md](BLUEPRINT_MIGRATION.md)

---

## 🎨 Dashboard Examples

### Complete Indoor Climate Overview

```yaml
type: vertical-stack
cards:
  # Header
  - type: custom:mushroom-title-card
    title: 🏠 Indoor Climate Status
    subtitle: v2.3.1
  
  # Overall Status
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.indeklima_hub_severity_score
        name: Severity Score
        icon: mdi:alert-decagram
        icon_color: |
          {% set score = states('sensor.indeklima_hub_severity_score') | float %}
          {% if score < 30 %}green
          {% elif score < 60 %}orange
          {% else %}red{% endif %}
      
      - type: custom:mushroom-entity-card
        entity: sensor.indeklima_hub_status
        name: Status
        icon: mdi:home-thermometer
  
  # Air Circulation (NEW v2.2!)
  - type: custom:mushroom-template-card
    primary: |
      {% set circ = states('sensor.indeklima_hub_air_circulation') %}
      {% if circ == 'good' %}🌬️ Good air circulation
      {% elif circ == 'moderate' %}🌀 Moderate air circulation
      {% else %}🚪 Poor air circulation{% endif %}
    secondary: |
      {{ state_attr('sensor.indeklima_hub_air_circulation', 'internal_doors_open') }} internal doors open
    icon: mdi:fan
    icon_color: |
      {% set circ = states('sensor.indeklima_hub_air_circulation') %}
      {% if circ == 'good' %}green
      {% elif circ == 'moderate' %}orange
      {% else %}red{% endif %}
  
  # Windows Status
  - type: entities
    title: 🪟 Windows & Doors
    entities:
      - entity: sensor.indeklima_hub_open_windows
        name: Outdoor Windows Open
        icon: mdi:window-open
      - type: attribute
        entity: sensor.indeklima_hub_open_windows
        attribute: rooms
        name: Rooms with open windows
  
  # Averages
  - type: entities
    title: 📊 Averages
    entities:
      - sensor.indeklima_hub_average_humidity
      - sensor.indeklima_hub_average_temperature
      - sensor.indeklima_hub_average_co2
  
  # Trends
  - type: entities
    title: 📈 Trends (30 min)
    entities:
      - sensor.indeklima_hub_humidity_trend
      - sensor.indeklima_hub_co2_trend
      - sensor.indeklima_hub_severity_trend
  
  # Ventilation Recommendation
  - type: custom:mushroom-template-card
    primary: |
      {% set status = states('sensor.indeklima_hub_ventilation_recommendation') %}
      {% if status == 'yes' %}🌬️ Ventilate now!
      {% elif status == 'optional' %}🤔 Consider ventilating
      {% else %}⏳ Wait to ventilate{% endif %}
    secondary: |
      {{ state_attr('sensor.indeklima_hub_ventilation_recommendation', 'reason') }}
    icon: mdi:window-open-variant
    icon_color: |
      {% set status = states('sensor.indeklima_hub_ventilation_recommendation') %}
      {% if status == 'yes' %}green
      {% elif status == 'optional' %}orange
      {% else %}red{% endif %}
```

### Per-Room Cards (v2.3.0+)

```yaml
type: entities
title: 🏠 Living Room Climate
entities:
  - entity: sensor.indeklima_living_room_status
    name: Status
  - entity: sensor.indeklima_living_room_temperature
    name: Temperature
  - entity: sensor.indeklima_living_room_humidity
    name: Humidity
  - entity: sensor.indeklima_living_room_co2
    name: CO2
```

---

## ⚙️ Settings

### Threshold Values

Adjust threshold values as needed:

| Parameter | Summer | Winter | Default |
|-----------|--------|--------|---------|
| **Max Humidity** | 40-80% | 30-70% | 60% / 55% |
| **Max CO2** | 800-2000 ppm | - | 1000 ppm |
| **Max VOC** | 1.0-10.0 mg/m³ | - | 3.0 mg/m³ |
| **Max Formaldehyde** | 0.05-0.5 mg/m³ | - | 0.15 mg/m³ |

**Access:**
Settings → Integrations → Indeklima → Configure → ⚙️ Thresholds

### Weather Integration

Configure weather sensor for better ventilation recommendations:

1. Settings → Integrations → Indeklima → Configure
2. Select "🌤️ Weather integration"
3. Choose your preferred weather sensor
4. Or leave empty for HA default

---

## 🔧 Troubleshooting

### Sensors Show "Unknown"

**Problem:** Sensor shows "unknown" or "unavailable"

**Solution:**
1. Check that sensor entities exist and are available
2. Check that sensor returns numeric value
3. See Home Assistant logs: Settings → System → Logs
4. Filter on "indeklima"

### Window/Door Status Wrong

**Problem:** Windows show as closed when they're open

**Solution:**
1. Check that your binary_sensor uses standard "on/off" states
2. "on" = open, "off" = closed
3. Go to Developer Tools → States
4. Find your window sensor and verify state

### Air Circulation Always Shows "Poor"

**Problem:** Even though doors are open, shows "Poor"

**Solution:**
1. Verify that internal doors are configured correctly
2. Go to Integration → Configure → Manage rooms
3. Edit room → Window/Door configuration
4. Make sure internal doors are NOT marked as "leads outdoors"

### Ventilation Recommendation Doesn't Work

**Problem:** Sensor always shows "No" or "unknown"

**Solution:**
1. Check that at least one room has sensors configured
2. Configure weather sensor for better recommendations
3. Verify threshold values are set correctly

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for full version history.

### v2.3.1 (2025-01-18) - CURRENT
- 🔧 **Complete Encoding Cleanup** - All English constants
- ✅ Fixed Danish character handling (æ, ø, å)
- ✅ State translations via strings.json/da.json
- ✅ Blueprint fixed for v2.3.1

### v2.3.0 (2025-01-12)
- 📊 Per-room metric sensors (temperature, humidity, CO2)
- ✅ Better device classes
- ✅ Backward compatible attributes

### v2.2.0 (2025-01-12)
- 🪟 Indoor/Outdoor window classification
- 🌬️ Air circulation sensor
- 🎯 Severity bonus for good air circulation
- ✅ Fixed window state logic

### v2.1.0 (2025-01-11)
- 🌬️ Ventilation recommendations
- 📱 Automation Blueprint
- 🔔 Last notified tracking

### v2.0.0 (2025-01-04)
- 🏠 Device organization
- ✨ Modern entity naming
- 📈 Trend analysis

### v1.0.0 (2025-01-02)
- 🎉 Initial release

---
## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### 🐛 Report Bugs
Found a bug? [Create a bug report](../../issues/new?labels=bug&template=bug_report.md)

### 💡 Suggest Features  
Have an idea? [Share it in Discussions](../../discussions/new?category=ideas)

### ❓ Ask Questions
Need help? [Ask in Q&A](../../discussions/new?category=q-a)

### 🔧 Contribute Code
Want to contribute code? Read our [Contributing Guide](CONTRIBUTING.md)

### 🌟 Good First Issues
New to the project? Check out issues labeled [`good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

### 📖 Documentation
Help improve the docs! All documentation improvements are welcome.

---

**Every contribution matters!** Whether it's:
- 🐛 Fixing a typo
- 📝 Improving documentation  
- 🌍 Adding a translation
- ✨ Adding a feature
- 🤝 Helping others in Discussions

We appreciate them all! 🙏

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Home Assistant community
- HACS team
- All contributors

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/kingpainter/indeklima/issues)
- **Discussions:** [GitHub Discussions](https://github.com/kingpainter/indeklima/discussions)
- **Documentation:** [GitHub Wiki](https://github.com/kingpainter/indeklima/wiki)

---

**Made with ❤️ by KingPainter**
