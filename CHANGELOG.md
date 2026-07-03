# Changelog

Alle væsentlige ændringer til Indeklima dokumenteres i denne fil.

Formatet er inspireret af [Keep a Changelog](https://keepachangelog.com/).
Detaljerede per-version noter findes i `CHANGELOG_v{major}_{minor}_{patch}.md`.

---

## [2.6.0] — 2026-07-03

### Tilføjet
- **Indbygget affugter-automation** — erstatter ekstern HA-automation:
  - Knap-styring: Indeklima lytter selv på en valgfri knap-entitet pr. rum og toggler affugteren
  - Automatisk tænd/sluk baseret på affugter-anbefalingen (fugtighed + skimmelrisiko)
  - LED-feedback (valgfri `light`-entitet pr. rum): blå = manuel, gul = automatisk, fra = slukket
  - Auto-sluk-timer pr. rum (konfigurerbar varighed, standard 45 min)
  - Konfigurerbar stilletid — globalt tidsvindue (OptionsFlow) + valgfri per-rum override
- `dehumidifier_recommendation`-sensoren har nu en `tilstand`-attribut (manual/auto/off)

### Rettet
- **Kritisk**: `CONF_WINDOW_ENTITY` matchede ikke den faktisk gemte konfigurationsnøgle
  (`"entity"` vs. `"entity_id"`). Dette gjorde at rum-redigering crashede, og at
  vindues-/dørdetektion i praksis aldrig har fungeret. Rettet uden datamigrering.
- `_get_room_schema()` gjort defensiv mod data/kode-mismatch (`.get()` i stedet for
  direkte dict-indeksering)
- `sensor.py`: manglende `None`-guard for `coordinator.data` i hub-sensorernes
  `extra_state_attributes`, som gav `AttributeError` ved opstart
- `strings.json`: rettede en eksisterende JSON-korruption (fejlplaceret `issues`-blok)
  som ville have fejlet `hassfest`-validering i CI

### Tests
- ~20 nye/opdaterede tests for affugter-styring, stilletid og knap-lyttere
- Alle 9 eksisterende tests i `TestCalculateDehumidifierRecommendation` opdateret til
  den nye funktions-signatur

Se [`CHANGELOG_v2_6_0.md`](CHANGELOG_v2_6_0.md) for fuld teknisk detaljering.

---

## Tidligere versioner

Se de individuelle `CHANGELOG_v{version}.md`-filer i repoets rod for detaljer om
versioner før 2.6.0 (2.0.0 → 2.5.14).
