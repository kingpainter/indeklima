# Changelog

All notable changes to Indeklima integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.3.1] - 2025-01-18

### Fixed - CRITICAL ENCODING FIXES
- 🔧 **Complete Encoding Cleanup** - Removed ALL encoding issues
  - All Python code now uses ONLY English + ASCII
  - All Danish text moved to translation files (strings.json, da.json)
  - Fixed æ, ø, å character handling in all files
  - Removed emojis from Python code
  - Clean UTF-8 encoding throughout

### Changed
- ✅ All constants now in English (STATUS_GOOD, TREND_STABLE, etc.)
- ✅ State translations via strings.json/da.json
- ✅ `normalize_room_id()` function properly handles Danish characters
- ✅ No double-encoding issues
- ✅ Config flow labels use translation keys

### Documentation
- 📚 All .md files converted to English
- 📚 Added BLUEPRINT_MIGRATION.md
- 📚 Updated UPGRADE guide for v2.3.1
- 📚 Added ENGLISH_CONSTANTS.md explanation

### Migration
- **No breaking changes** - Direct upgrade from v2.2.0 or v2.3.0
- If you had encoding issues in v2.3.0, this fixes them all
- Recommend clean install if you experienced duplicate devices
- **Blueprint requires update** - See BLUEPRINT_MIGRATION.md

---

## [2.3.0] - 2025-01-12

### Added - PER-ROOM METRIC SENSORS
- 📊 **Separate Temperature Sensor** per room
  - `sensor.indeklima_[room]_temperature`
  - Device class: `temperature`
  - Unit: °C
  - Attributes: `sensors_used`

- 📊 **Separate Humidity Sensor** per room
  - `sensor.indeklima_[room]_humidity`
  - Device class: `humidity`
  - Unit: %
  - Attributes: `sensors_used`

- 📊 **Separate CO2 Sensor** per room
  - `sensor.indeklima_[room]_co2`
  - Device class: `carbon_dioxide`
  - Unit: ppm
  - Attributes: `sensors_used`

### Changed
- ✅ Better device classes for all sensors
- ✅ Improved entity naming consistency
- ✅ Room ID normalization function

### Backward Compatibility
- ✅ Status sensor attributes PRESERVED (humidity, temperature, co2, etc.)
- ✅ Existing dashboards work without changes
- ✅ No breaking changes!

---

## [2.2.0] - 2025-01-12

### Added - WINDOW & DOOR CLASSIFICATION
- 🪟 **Indoor/Outdoor Classification** 
  - Distinguish between outdoor windows and internal doors
  - Outdoor windows used for ventilation recommendations
  - Internal doors used for air circulation calculation
  - Flexible configuration via UI

### Added - AIR CIRCULATION SYSTEM
- 🌬️ **Air Circulation Sensor** (`sensor.indeklima_hub_air_circulation`)
  - States: Good/Moderate/Poor
  - Based on number of open internal doors
  - Good: 3+ doors open
  - Moderate: 1-2 doors open
  - Poor: No doors open

- 🎯 **Severity Bonus for Air Circulation**
  - 5% reduction in severity score when internal doors open
  - Better air distribution between rooms
  - Lower risk of local problems

### Added - ROOM ATTRIBUTES
- 📊 `outdoor_windows_open` - Count of open outdoor windows per room
- 📊 `internal_doors_open` - Count of open internal doors per room
- 📊 `air_circulation_bonus` - Boolean indicator if room has open internal doors

### Fixed
- 🔧 **Window State Logic** 
  - CRITICAL FIX: Binary sensor "on" now correctly means OPEN
  - Previous version had inverted logic
  - Affects window tracking and ventilation recommendations

### Changed
- ✅ Window sensor configuration now uses dict format
  - Old: Simple entity_id string
  - New: Dict with `entity_id` and `is_outdoor` keys
  - Backward compatible with old format

---

## [2.1.0] - 2025-01-11

### Added - VENTILATION RECOMMENDATIONS
- 🌬️ **Ventilation Recommendation Sensor** (`sensor.indeklima_hub_ventilation_recommendation`)
  - States: Yes/No/Optional
  - Analyzes indoor climate and weather conditions
  - Provides reasoning for recommendation
  - Lists specific rooms needing ventilation

### Added - AUTOMATION SUPPORT
- 📱 **Automation Blueprint** (`room_notification.yaml`)
  - Per-room notifications
  - Smart cooldown to avoid spam
  - Time-based activation
  - Severity threshold configuration
  - Includes ventilation tips

- 🔔 **Last Notified Tracking**
  - `last_notified` attribute on room status sensors
  - Enables cooldown logic in automations
  - Prevents notification spam

### Added - WEATHER INTEGRATION
- 🌤️ Optional weather entity configuration
  - Used for better ventilation recommendations
  - Checks outdoor temperature and humidity
  - Falls back to HA default if not configured

---

## [2.0.0] - 2025-01-04

### Added - DEVICE ORGANIZATION
- 🏠 **Hub Device** (`Indeklima Hub`)
  - Central device for global sensors
  - All hub sensors attached to this device
  - Modern Home Assistant device structure

- 🏠 **Room Devices** (`Indeklima [Room Name]`)
  - One device per room
  - Linked to hub via `via_device`
  - All room sensors attached to room device
  - Clean organization in HA interface

### Changed - ENTITY NAMING
- ✨ **Modern Entity Naming** (`has_entity_name = True`)
  - Hub sensors: `sensor.indeklima_hub_[sensor_type]`
  - Room sensors: `sensor.indeklima_[room]_status`
  - Device name automatically prepended
  - Follows HA 2024+ guidelines

### Added - TREND ANALYSIS
- 📈 **Trend Sensors** (30-minute window)
  - `sensor.indeklima_hub_humidity_trend`
  - `sensor.indeklima_hub_co2_trend`
  - `sensor.indeklima_hub_severity_trend`
  - States: Rising/Falling/Stable
  - Linear regression calculation
  - 6 data points history

### Changed - OPTIONS FLOW
- ⚙️ **Enhanced Options Flow**
  - Main menu with multiple sections
  - Per-room management (add/edit/delete)
  - Threshold configuration
  - Weather integration setup
  - Full UI-based configuration

### Migration
- ⚠️ **Breaking Changes from v1.x**
  - Entity IDs have changed
  - Dashboards need updating
  - Automations need updating
  - Clean install recommended

---

## [1.0.0] - 2025-01-02

### Added - INITIAL RELEASE
- 🎉 **Basic Multi-Room Support**
  - Configure multiple rooms
  - Multiple sensors per room type
  - Automatic averaging

- 📊 **Severity Scoring**
  - 0-100 scale (lower is better)
  - Based on humidity, CO2, VOC, formaldehyde
  - Season-based thresholds (summer/winter)

- 🌡️ **Sensor Support**
  - Humidity sensors
  - Temperature sensors
  - CO2 sensors
  - VOC sensors
  - Formaldehyde sensors
  - Window/door sensors

- 📈 **Global Sensors**
  - Average humidity across rooms
  - Average temperature across rooms
  - Average CO2 across rooms
  - Overall severity score
  - Overall status (Good/Warning/Critical)
  - Open windows count

- ⚙️ **Configuration**
  - UI-based config flow
  - Per-room sensor selection
  - Threshold configuration
  - Optional device support (dehumidifier, fan)

- 🏅 **Home Assistant Compliance**
  - Config flow
  - Async implementation
  - Type hints
  - Error handling
  - Logging
  - Bronze tier quality scale

---

## Upgrade Guides

- **v2.2.0 → v2.3.1:** See [UPGRADE_v2_3_1.md](UPGRADE_v2_3_1.md)
- **v1.x → v2.x:** Clean install recommended (breaking changes)

---

## Version History

| Version | Date | Type | Key Changes |
|---------|------|------|-------------|
| **2.3.1** | 2025-01-18 | Fix | English constants, encoding cleanup |
| **2.3.0** | 2025-01-12 | Feature | Per-room metric sensors |
| **2.2.0** | 2025-01-12 | Feature | Window classification, air circulation |
| **2.1.0** | 2025-01-11 | Feature | Ventilation recommendations, blueprints |
| **2.0.0** | 2025-01-04 | Major | Device organization, modern naming |
| **1.0.0** | 2025-01-02 | Initial | First public release |

---

## Roadmap

### v2.4.0 (Planned - Q1 2025)
- [ ] VOC and Formaldehyde per-room sensors
- [ ] Diagnostics platform (Gold tier requirement)
- [ ] Repair flow for sensor errors
- [ ] Unit tests (>95% coverage)
- [ ] Improved debugging tools

### v2.5.0 (Planned - Q2 2025)
- [ ] Service calls for device control
- [ ] Automation triggers
- [ ] Extended documentation
- [ ] Multi-language support expansion

### v3.0.0 (Vision - Q3-Q4 2025)
- [ ] Machine learning patterns
- [ ] Predictive maintenance
- [ ] Energy optimization
- [ ] Multi-home support
- [ ] Advanced ventilation control

---

## Links

- **GitHub:** https://github.com/kingpainter/indeklima
- **Issues:** https://github.com/kingpainter/indeklima/issues
- **Discussions:** https://github.com/kingpainter/indeklima/discussions
- **Documentation:** [README.md](README.md)
- **Compliance:** [HA_COMPLIANCE.md](HA_COMPLIANCE.md)

---

**Made with ❤️ by KingPainter**
