# Changelog

All notable changes to Indeklima will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### FASE 5 & 6 - Planned
- 🌬️ **Ventilationsanbefalinger** - Smart sensor der analyserer indeklima og vejr
  - Intelligente anbefalinger: Ja/Nej/Valgfrit
  - Tager højde for udendørs temperatur og fugtighed
  - Viser hvilke rum der trænger til udluftning
  - Begrundelse for anbefalingen
- 🔔 **Automation Blueprint** - Færdig notifikations-automation
  - Per-rum notifikationer
  - Smart cooldown system
  - Tidsstyring (kun indenfor åbningstider)
  - Severity threshold valg
  - Inkluderer ventilations tips
- 📲 Diagnostics platform (Gold tier)
- 📲 Automatisk affugter kontrol
- 📲 Fan automation
- 📲 Integration med ventilationssystemer
- 📲 Netatmo thermostat integration

## [2.0.0] - 2025-01-04

### Added - FASE 3 & 4
- 🏠 **Device Organization** - Moderne device struktur
  - Hub device med globale sensorer
  - Separat device per rum
  - Korrekt device linking via `via_device`
- ✨ **Modern Entity Naming** - Følger HA 2024+ guidelines
  - `has_entity_name = True`
  - Automatisk præfiks fra device navn
  - Kortere, renere entity navne
- 🏷️ **Device Info** - Komplet metadata
  - Manufacturer: Indeklima
  - Model: Climate Monitor v2 / Room Monitor  
  - SW Version: Automatisk fra const.py
  - Configuration URL
- 🎯 **Proper Device Classes** - Korrekt visning i HA
  - SensorDeviceClass.HUMIDITY
  - SensorDeviceClass.TEMPERATURE
  - Automatisk enheder og ikoner
- 🌍 **Modern Translations** - strings.json + backup
- 🥈 **Quality Scale: Silver** - Opfylder alle Silver tier krav
- 📚 **HA_COMPLIANCE.md** - Detaljeret compliance dokumentation
- ⚙️ **Fuld Options Flow** - Komplet rum-håndtering efter installation
  - ✏️ Rediger eksisterende rum
  - 🗑️ Slet enkelte rum
  - ➕ Tilføj nye rum
  - 🌤️ Vejr sensor konfiguration
  - Automatisk reload af integration ved ændringer
- 📈 **Trend Analysis** - 30-minutters historik
  - Humidity trend (Stigende/Faldende/Stabil)
  - CO2 trend
  - Severity trend

### Added - FASE 1 & 2
- 🏠 **Per-room configuration** - Configure each room individually instead of all at once
- ✏️ **Room reconfiguration** - Edit existing rooms without deleting everything
- 🗑️ **Single room deletion** - Remove individual rooms
- 💨 **Dehumidifier support** - Add and control dehumidifiers per room
- 🌤️ **Weather integration** - Choose weather data source or use HA default
- 🌀 **Fan/Ventilation support** - Control fans and ventilation systems
- 📊 **Room-based organization** - Each room appears as separate device in HA
- 🔔 **Per-room notifications** - Configure different notification recipients per room
- 🌡️ **Temperature support** - Added temperature sensor support
- 🔢 **Multiple sensors per room** - Use multiple sensors of same type, get average
- 🌍 **Multi-language support** - Danish and English translations

### Changed
- 🔄 **Major architecture refactor** - Improved scalability and maintainability
- 📱 **Better UI organization** - Cleaner device and entity structure
- ⚡ **Performance improvements** - More efficient data processing

### Fixed
- 🛠 **Config flow errors** - Resolved indentation and import issues
- 🔧 **Sensor reliability** - Better error handling for unavailable sensors
- 🐛 **Empty device fields** - Fan and dehumidifier fields now properly optional

## [1.0.0] - 2025-01-02

### Added
- 🎉 **Initial release** as custom integration
- 📊 Multi-room climate monitoring
- 💯 Intelligent severity scoring
- 🪟 Window tracking
- 🌞 Season-based thresholds
- 🔔 Smart notifications with cooldown
- 🎨 HACS compatibility

---

## Version Numbering

- **Major (X.0.0)**: Breaking changes, requires manual intervention
- **Minor (0.X.0)**: New features, backward compatible
- **Patch (0.0.X)**: Bug fixes, improvements

[Unreleased]: https://github.com/kingpainter/indeklima/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/kingpainter/indeklima/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/kingpainter/indeklima/releases/tag/v1.0.0