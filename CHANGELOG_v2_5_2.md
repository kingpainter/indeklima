# Changelog - Indeklima v2.5.2

## Version 2.5.2 - Version Sync & Affugter på rum-kort

**Release Date:** June 2026
**Type:** PATCH — Backend version sync + Frontend fix, backward compatible
**Previous Version:** 2.5.1

---

## 🔧 Fixes

### Version synkronisering
Alle backend-filer opdateret til v2.5.2 (var fejlagtigt på 2.5.0):
- `const.py` — `__version__ = "2.5.2"`
- `manifest.json` — `"version": "2.5.2"`
- `websocket.py` — version header opdateret
- `__init__.py` — version header opdateret

### Affugter-sektion tilføjet til `indeklima-room-card`
Room-kortet manglede affugter-anbefaling. Tilføjet en kompakt `dehum-row` under footer-chips med farve-kodet label og ikon — konsistent med hub/tablet/detail-kortene.

---

## 🧪 Tests

### `test_websocket.py` opdateret
- Mock-data i `_make_coordinator()` tilføjet `mold_risk`, `dehumidifier_recommendation` og `mold_sensors_count` på alle rum
- Global `mold_risk` og `dehumidifier_recommendation` tilføjet til top-level coordinator mock
- 6 nye test-cases:
  - `test_mold_risk_in_result` — global mold_risk eksponeres i WS-svar
  - `test_dehumidifier_recommendation_in_result` — global dehumidifier_recommendation eksponeres
  - `test_room_has_mold_risk_field` — per-rum mold_risk i get_climate_data
  - `test_room_has_dehumidifier_recommendation_field` — per-rum dehumidifier i get_climate_data
  - `test_room_data_has_mold_risk` — mold_risk i get_room_data
  - `test_room_data_has_dehumidifier_recommendation` — dehumidifier_recommendation i get_room_data

---

## 📁 Ændrede filer

| Fil | Ændring |
|---|---|
| `custom_components/indeklima/const.py` | Version 2.5.2 |
| `custom_components/indeklima/manifest.json` | Version 2.5.2 |
| `custom_components/indeklima/websocket.py` | Version header |
| `custom_components/indeklima/__init__.py` | Version header |
| `custom_components/indeklima/frontend/indeklima-cards.js` | v2.5.2 — affugter på room-card, CSS dehum-row |
| `tests/test_websocket.py` | Mock-data + 6 nye tests |

---

## ✅ Backward Compatibility

Ingen API-ændringer. Alle eksisterende automations, dashboards og konfigurationer virker uændret.
