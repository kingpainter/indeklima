# Changelog v2.6.1

**Dato:** 2026-07-04

## Rettet

- **Bug:** `mold_risk`-sensorens `sensorer_brugt`-attribut blev aldrig udfyldt, selv når et rum havde en dedikeret mold-fugtsensor konfigureret. Årsag: `IndeklimaRoomMetricSensor.extra_state_attributes` slog op på nøglen `mold_risk_sensors_count`, mens koordinatoren rent faktisk gemmer tælleren under `mold_sensors_count`. Sensor.py bruger nu den korrekte nøgle for `mold_risk`-metrikken.

## Tests

- Tilføjet fuld test-dækning for integrationens opstarts-/nedlukningslivscyklus (`async_setup_entry`, `async_unload_entry`, `async_reload_entry` i `tests/test_init.py`), herunder den kritiske v2.5.0-adfærd hvor en fejlende første opdatering ikke må blokere opsætning.
- Tilføjet tests for `mold_sensors_count`-attributten i `tests/test_coordinator.py`.
- Ny fil `tests/test_sensor.py` med grundlæggende dækning af `mold_risk`- og `dehumidifier_recommendation`-sensor-entiteterne (fandtes ikke tidligere).

## Ingen funktionsændringer

Denne udgivelse indeholder ingen ændringer i integrationens funktionalitet — kun en attribut-bugfix og udvidet testdækning.
