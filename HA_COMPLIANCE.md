# Home Assistant Compliance — Indeklima

**Version:** 2.5.14  
**Quality Scale:** Gold Tier 🥇  
**Last Updated:** June 2026

---

## ✅ Integration Quality Scale — Gold Tier

Based on: https://developers.home-assistant.io/docs/integration_quality_scale_index/

### Bronze ✅
- ✅ Config flow — komplet UI-baseret opsætning, ingen YAML
- ✅ Async — alle funktioner er async, ingen blokerende kald
- ✅ Entity naming — `has_entity_name = True` gennemgående
- ✅ Device info — alle entiteter har `DeviceInfo`
- ✅ Unique IDs — alle entiteter har `unique_id`
- ✅ Documentation — README.md, CHANGELOG.md, TROUBLESHOOTING.md
- ✅ Code style — type hints, docstrings, engelske konstanter

### Silver ✅
- ✅ Device registry — Hub + rum-enheder, `via_device` linking
- ✅ Entity categorization — korrekt `SensorDeviceClass` per sensor
- ✅ Options flow — grænseværdier, rum, weather entity
- ✅ Translations — `strings.json` (EN) + `translations/da.json` (DA)
- ✅ Error handling — `ConfigEntryNotReady`, `UpdateFailed`, try/catch, logging
- ✅ Coordinator pattern — `DataUpdateCoordinator`, 30s interval
- ✅ Quality scale declared — `quality_scale: gold` i `manifest.json`

### Gold ✅
- ✅ Diagnostics — `diagnostics.py`
- ✅ System health — `system_health.py`
- ✅ Repair flow — `repairs.py` for sensor/coordinator-fejl
- ✅ Setup failure handling — `ConfigEntryNotReady` + `UpdateFailed`
- ✅ `entry.runtime_data` — moderne HA-mønster
- ✅ Unit tests — testsuite i `tests/`

---

## 📋 Entity Guidelines

```python
_attr_has_entity_name = True
_attr_name = "Status"
# → sensor.indeklima_hub_status, sensor.indeklima_stue_humidity
```

---

## 🗃️ Device Registry

```
Indeklima Hub
├── Severity Score, Status
├── Average: Humidity / Temperature / CO2 / Pressure
├── Open Windows, Air Circulation
├── Trends: Humidity / CO2 / Severity
├── Ventilation Recommendation
└── Mold Risk Average

Indeklima <Rum>  (via Hub)
├── Status, Temperature, Humidity, CO2, Pressure
└── Mold Risk
```

---

## 🔄 Data Flow

```
Physical Sensors → HA States
    → IndeklimaDataCoordinator._async_do_update()
        ├── _get_sensor_values()       [raises repair issues if unavailable]
        ├── _calculate_severity()
        ├── _calculate_mold_risk()
        ├── _calculate_trend()
        ├── _calculate_air_circulation()
        ├── _calculate_ventilation_recommendation()
        └── _calculate_dehumidifier_recommendation()
    → coordinator.data
    → CoordinatorEntity sensors update
    → WebSocket API (get_climate_data / get_room_data)
    → Sidebar Panel (2 tabs) + Lovelace Cards
```

---

## 🏗️ Moderne HA-mønstre

### `entry.runtime_data`
```python
entry.runtime_data = coordinator      # __init__.py
coordinator = entry.runtime_data      # sensor.py
```

### `ConfigEntryNotReady`
```python
try:
    await coordinator.async_config_entry_first_refresh()
except Exception as err:
    raise ConfigEntryNotReady(...) from err
```

### `UpdateFailed`
```python
async def _async_update_data(self):
    try:
        result = await self._async_do_update()
        clear_coordinator_failed_issue(...)
        return result
    except Exception as err:
        raise_coordinator_failed_issue(...)
        raise UpdateFailed(...) from err
```

### Repair flow
```python
async def async_create_fix_flow(hass, issue_id, data) -> RepairsFlow:
    if issue_id.startswith(ISSUE_SENSOR_UNAVAILABLE):
        return SensorUnavailableRepairFlow()
    if issue_id.startswith(ISSUE_COORDINATOR_FAILED):
        return CoordinatorFailedRepairFlow()
```

---

## 🌍 Oversættelser

- `strings.json` — Engelsk (primær)
- `translations/da.json` — Dansk
- Al kode bruger engelske konstanter; oversættelser kun i JSON

---

## 🧪 Tests

```
tests/
├── conftest.py          # Fixtures og helpers
├── test_const.py        # version, konstanter, normalize_room_id
├── test_init.py         # coordinator: season, severity, status, trends, circulation
├── test_repairs.py      # issue raising/clearing, fix flow factory
├── test_websocket.py    # WS handlers, room sorting, mold_risk, dehumidifier
├── test_diagnostics.py  # config entry + device diagnostics
└── test_system_health.py
```

```bash
pytest --cov=custom_components/indeklima --cov-report=term-missing
```

---

## 📦 Manifest

```json
{
  "domain": "indeklima",
  "name": "Indeklima",
  "version": "2.5.14",
  "config_flow": true,
  "integration_type": "hub",
  "iot_class": "local_polling",
  "quality_scale": "gold",
  "codeowners": ["@kingpainter"]
}
```

---

## 📈 Alvorligheds-scoring

| Metrik | Max point |
|---|---|
| Fugtighed | 30 |
| CO₂ | 30 |
| VOC | 20 |
| Formaldehyd | 20 |
| Lufttryk | 0 — informativt |
| Skimmelrisiko | 0 — informativt |
| Luftcirkulations-bonus | −5% |

| Score | Status |
|---|---|
| 0–29 | ✅ God |
| 30–59 | ⚠️ Advarsel |
| 60–100 | 🔴 Kritisk |

---

## 📚 Referencer

- [Integration Quality Scale](https://developers.home-assistant.io/docs/integration_quality_scale_index/)
- [Entity Guidelines](https://developers.home-assistant.io/docs/core/entity/)
- [Repairs](https://developers.home-assistant.io/docs/repairs/)
- [Diagnostics](https://developers.home-assistant.io/docs/diagnostics/)
- [Data Coordinator](https://developers.home-assistant.io/docs/integration_fetching_data/)
