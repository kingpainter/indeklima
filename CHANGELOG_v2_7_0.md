# Changelog v2.7.0

**Dato:** 2026-07-04

## Nyt

- **Affugter-LED: rød alarm ved kritisk indeklima.** LED'en skifter til rød så snart et rums samlede severity-status bliver `critical` — uanset om affugteren i øjeblikket kører manuelt (blå), automatisk (gul) eller er slukket (fra). Rød har højeste prioritet og overskriver altid mode-farven.
  - Tærsklen er rummets **severity-status** (bredere end skimmelrisiko alene — inkluderer også CO₂, VOC og formaldehyd), ikke kun fugt/skimmel.
  - Farven genberegnes ved **hver opdateringscyklus** (hvert 30. sekund), ikke kun ved start/stop af affugteren — så LED'en reagerer med det samme, både når indeklimaet forværres, og når det retter sig igen (falder tilbage til blå/gul/fra afhængigt af affugterens aktuelle tilstand).
  - Selve affugterens styrings-tilstand (`dehumidifier_mode`: manual/auto/off) påvirkes ikke af alarmen — det er udelukkende en visuel LED-overlay.
  - Ingen unødvendige lyskommandoer: der sendes kun en ny service-kald til LED'en når farven faktisk ændrer sig.

## Bevidst fravalgt (afklaret med bruger)

- Auto-affugteren stopper **ikke** tidligt når anbefalingen skifter til NEJ — den fulde 45-minutters timer bevares for at undgå kort-cykling af den fysiske affugter.

## Tests

- Ny testklasse `TestDehumidifierLedCriticalAlert` i `tests/test_coordinator.py`: rød ved kritisk status (uanset mode), tilbagefald til blå/gul/fra ved recovery, ingen redundante service-kald, ingen LED-håndtering for rum uden konfigureret LED-entitet.
