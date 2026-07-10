# Changelog v2.9.1

**Dato:** 2026-07-10

## Rettet — vejrdata manglede når vinduer var åbne

### Bug
`_calculate_ventilation_recommendation()` i `__init__.py` hentede kun vejrdata (`outdoor_temp`/`outdoor_humidity`) *efter* tjekket for åbne vinduer. Når mindst ét vindue et sted i huset var registreret som åbent, returnerede funktionen tidligt via `open_windows`-grenen — før vejrdata nogensinde blev hentet. Konsekvens: panelet viste "Vejrdata ikke tilgængeligt endnu", selvom den konfigurerede vejr-entity (`weather.hjem`, Met.no) havde helt gyldige `temperature`/`humidity`-attributter. Kommentaren i koden sagde ellers udtrykkeligt at vejrdata skulle hentes "regardless of whether there are indoor issues or not" — men det gjaldt reelt ikke for open-windows-grenen.

### Fix
Flyttede vejr-hentningen (`self._get_weather_data()` + tildeling af `outdoor_temp`/`outdoor_humidity`) til toppen af `_calculate_ventilation_recommendation()`, før alle early-returns. Fjernede den nu overflødige duplikerede vejr-hentning længere nede i funktionen.

### Sådan blev det fundet
Fejlen blev rapporteret som "vejr data ikke tilgængelig i panelet, selvom HA's standard vejr-integration er konfigureret". Konfiguration og entity registry blev tjekket først (`weather_entity` = `weather.hjem`, platform `met`, aktiveret) — matchede fint. Live-state af `weather.hjem` blev derefter tjekket direkte af Flemming (Udviklerværktøjer → Tilstande): state `sunny`, med gyldige `temperature: 27.5` og `humidity: 32`. Da konfiguration og live-data begge var korrekte, måtte fejlen ligge i selve beregningslogikken — sporet til den tidlige `return` i open-windows-grenen.

### Filer ændret
- `__init__.py`: vejr-hentning flyttet til toppen af `_calculate_ventilation_recommendation()`, duplikat fjernet
- `tests/test_coordinator.py`: ny `TestCalculateVentilationRecommendation`-klasse med 3 regressionstests (åbne vinduer + gyldigt vejr, ingen problemer + gyldigt vejr, vejr utilgængelig)
- `const.py` / `manifest.json`: version 2.9.0 → 2.9.1
