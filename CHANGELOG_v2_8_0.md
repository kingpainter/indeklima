# Changelog v2.8.0

**Dato:** 2026-07-04

## Nyt

Bygger videre på v2.7.0's røde LED-alarm ved kritisk indeklima. Implementerer 4 af 5 forbedringsforslag fra sidste session (forslag 2 — mobil-notifikation ved alarm — er ikke bygget, se "Fravalgt" nedenfor).

- **Blinkende alarm i stedet for konstant rød.** LED'en blinker rød/fra hvert 3. sekund (`DEHUM_LED_BLINK_INTERVAL`), mens rummet er i kritisk alarm. Implementeret som en selv-genplanlæggende `async_call_later`-kæde, så den stopper rent så snart alarmen annulleres.
- **Hysterese på recovery.** Alarmen forbliver aktiv indtil rummet har været ikke-kritisk i **2 sammenhængende opdateringscyklusser** (`DEHUM_LED_RECOVERY_CYCLES`, ~60 sekunder ved 30s scan-interval), så LED'en ikke flimrer frem og tilbage lige omkring tærsklen.
- **"Kritisk siden"-tidsstempel.** Nyt attribut `kritisk_siden` (ISO-tidsstempel) på hvert rums status-sensor, sat øjeblikkeligt (ingen hysterese) når rummets *reelle* severity-status bliver `critical`, og ryddet med det samme det ikke længere er. Fungerer for alle rum uafhængigt af om der er konfigureret en LED eller affugter.
- **Konfigurerbar alarm-tærskel pr. rum.** Nyt valgfrit felt "LED rød-alarm-tærskel" i rum-opsætningen (både ved oprettelse og redigering), 1-100. Falder tilbage til den globale STATUS_CRITICAL-grænse (60) hvis ikke sat. **Vigtigt:** denne tærskel styrer udelukkende LED-alarmen — den ændrer IKKE rummets officielle status-klassifikation (status-sensoren, ventilationsanbefalinger mv. bruger stadig de faste 30/60-grænser).

## Fravalgt

- **Mobil-notifikation ved alarm** (forslag 2 fra sidste session) er bevidst ikke bygget i denne omgang — kræver egen cooldown-logik og et valg af hvilken `notify.*`-target der skal bruges pr. rum. Kan tilføjes separat hvis ønsket.

## Filer ændret

- `const.py`: nye konstanter `CONF_ROOM_LED_CRITICAL_SEVERITY`, `DEFAULT_LED_CRITICAL_SEVERITY`, `DEHUM_LED_BLINK_INTERVAL`, `DEHUM_LED_RECOVERY_CYCLES`
- `__init__.py`: LED-alarm-tilstandsmaskine (blink start/stop, hysterese-tæller), `kritisk_siden`-tracking (uafhængig af LED), blink-timere ryddes ved unload
- `sensor.py`: `kritisk_siden` eksponeret som attribut på rum-status-sensoren
- `config_flow.py`: nyt valgfrit per-rum-felt i både ConfigFlow og OptionsFlow (opret + redigér)
- `strings.json` / `translations/da.json`: labels til det nye felt
- Tests: ny testklasse `TestLedCriticalAlarmMachine` i `tests/test_coordinator.py` (8 tests), ny testklasse i `tests/test_sensor.py` for `kritisk_siden`

## Kendt begrænsning

Der findes ikke en `tests/test_config_flow.py` i projektet i forvejen, så det nye config_flow-felt er **ikke** dækket af automatiske tests — kun manuelt gennemgået mod det eksisterende mønster for `quiet_hours`-felterne. Anbefaling: verificér UI'et manuelt efter deploy (opret/redigér et rum og tjek at feltet "LED rød-alarm-tærskel" vises og gemmes korrekt).
