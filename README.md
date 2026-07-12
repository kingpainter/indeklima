# Indeklima

**Multi-room indoor climate monitoring for Home Assistant** — temperature, humidity, CO₂, VOC, formaldehyde and barometric pressure, with mold risk assessment, dehumidifier recommendations, and a polished custom frontend.

![Version](https://img.shields.io/badge/version-2.9.3-blue)
![Quality Scale](https://img.shields.io/badge/quality_scale-gold-gold)
![HACS](https://img.shields.io/badge/HACS-custom-orange)

---

## About the project

Indeklima is a custom Home Assistant integration built to monitor indoor climate across multiple rooms at once — and to help keep it healthy. The integration collects data from your existing sensors (temperature, humidity, CO₂, VOC, formaldehyde, pressure), calculates an overall severity score per room and globally, and gives concrete recommendations for ventilation and dehumidification.

Since version 2.6.0, Indeklima can also **control a physical dehumidifier directly** — turning it on/off via a button or automatically based on humidity and mold risk, with LED feedback and configurable quiet hours. Since version 2.7.0, the dehumidifier LED switches to **red alarm**, regardless of manual/auto mode, whenever the room's overall indoor climate status is critical. Since version 2.8.0, the alarm **blinks** instead of staying solid, holds for a couple of cycles after recovery (to avoid flicker), the threshold can be overridden per room, and a "critical since" timestamp is stored on each room's status sensor. Since version 2.9.0, dehumidifier mode, the "critical since" timestamp, and LED alarm status are all mirrored in the panel and Lovelace cards. Version 2.9.1 fixed a bug where outdoor weather data was silently skipped whenever any window in the house was open.

## Features

- **Multi-room monitoring** — configure as many rooms as you like, each with its own sensors
- **Severity score (0–100)** per room and globally, based on humidity, CO₂, VOC and formaldehyde
- **Mold risk calculation** (`low` / `moderate` / `high` / `critical`) — uses a dedicated mold sensor if available, otherwise falls back to the room's humidity sensor
- **Dehumidifier recommendation** per room and globally, based on mold risk, humidity trend and ventilation status
- **Built-in dehumidifier control** (v2.6.0+): physical button toggle, automatic on/off, LED feedback (manual/automatic/off/**blinking red alarm when indoor climate is critical**, v2.7.0–2.8.0), auto-off timer, configurable quiet hours (global + per room), **per-room alarm threshold and "critical since" timestamp** (v2.8.0+), with dehumidifier mode, critical-since timestamp, and LED alarm state all mirrored in the UI (v2.9.0+)
- **Ventilation recommendation** based on indoor climate and outdoor weather data
- **Air circulation status** based on open internal doors
- **Trends** (rising/falling/stable) for humidity, CO₂ and severity over a 30-minute rolling window
- **Window/door detection** distinguishing between outdoor and internal openings
- **Danish-first UI** — English code and logs, Danish UI and notifications (translatable via `translations/`)
- **Custom Lovelace panel** with sidebar, room overview, sparklines and interactive cards
- **Gold Tier HA Quality Scale** — diagnostics, repair flow, system health, full test coverage

## Installation

### Via HACS (recommended)

1. Add this repository as a custom repository in HACS (category: Integration)
2. Install "Indeklima" from HACS
3. Restart Home Assistant
4. Go to **Settings → Devices & services → Add integration** and search for "Indeklima"

### Manual installation

1. Copy `custom_components/indeklima` to your `config/custom_components/` folder
2. Restart Home Assistant
3. Add the integration as described above

## Configuration

All configuration is done via the UI — no YAML required.

### Setting up a room

For each room you can select:

- Humidity, temperature, CO₂, VOC, formaldehyde and pressure sensors (multiple sensors of the same type are supported — their average is used)
- A dedicated mold sensor (optional — otherwise falls back to the room's humidity sensor)
- Window/door sensors, marked as outdoor or internal
- A dehumidifier (`switch` or `humidifier` entity)
- A dehumidifier LED (`light` entity) for visual manual/auto/off feedback
- A dehumidifier button (any entity — supports both real button entities and click-count sensors)
- The dehumidifier's auto-off duration (default 45 minutes)
- A quiet-hours override for that specific room

### Global settings (Settings → Indeklima → Configure)

- **Thresholds**: max humidity summer/winter, max CO₂, VOC and formaldehyde
- **Weather integration**: optional `weather` entity for ventilation recommendations
- **Quiet hours**: global time window in which dehumidifiers won't turn on automatically (unless mold risk is high/critical)

## Entities

**Hub level** (~19 sensors): averages for each measured quantity, overall severity score and status, open window count, air circulation, trends, ventilation and dehumidifier recommendations, mold risk.

**Per room**: status, temperature, humidity, CO₂, pressure (if configured), mold risk and dehumidifier recommendation (with a `mode` attribute showing manual/auto/off).

## Documentation

- [`CHANGELOG.md`](CHANGELOG.md) — summary changelog across all versions
- [`CHANGELOG_v{version}.md`](.) — detailed per-version changelog
- [`HA_COMPLIANCE.md`](HA_COMPLIANCE.md) — detailed review of Quality Scale requirements
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) — troubleshooting guide
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contributing to the project

## License

See [`LICENSE`](LICENSE).
