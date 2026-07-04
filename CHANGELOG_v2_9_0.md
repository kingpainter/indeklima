# Changelog v2.9.0

**Dato:** 2026-07-04

## Nyt — pre-commit UI/UX-gennemgang implementeret

Bygger de 3 UI/UX-forslag fra pre-commit gennemgangen af v2.8.0-arbejdet, plus retter et hul der gjorde dem nødvendige.

### Rettet (kritisk forudsætning)
- `websocket.py` manglede `dehumidifier_mode` og `kritisk_siden` i begge WebSocket-payloads (`ws_get_climate_data` og `ws_get_room_data`) — de var derfor usynlige for panel og kort, selvom coordinator beregnede dem korrekt.
- `led_alarm_active` fandtes kun internt i coordinatorens `_dehumidifier_state`, ikke i selve `room_data` — kunne derfor slet ikke eksponeres til frontend. Tilføjet til `room_data` i `_process_room()` og videre til begge WebSocket-payloads.

### Nyt i UI (panel + alle 4 Lovelace-kort)
- **Tilstand på affugter** — viser nu "Manuel"/"Automatisk"/"Fra" ved siden af affugter-anbefalingen, alle steder affugteren vises (kompakt rum-kort, rum-detaljer, hus-overblik)
- **"Kritisk siden HH:MM"** — vises som en rød advarselslinje når et rums status er kritisk, baseret på det nye `kritisk_siden`-tidsstempel
- **LED-alarm-spejling** — en rød 🔴-indikator vises i UI'et når et rums LED-alarm er aktiv, så man kan se det uden fysisk at være i rummet. Vises som ikon i rum-navnet (kompakt visning), som en pulserende banner (detaljevisning), og som en badge i footer-chips (rum-kort)

## Filer ændret
- `__init__.py`: `led_alarm_active` tilføjet til `room_data`
- `websocket.py`: 3 nye felter i begge payloads
- `frontend/indeklima-panel.js`: nye helper-metoder `_dehumModeLabel()`, `_fmtTimeSince()`, samt visning i kompakt rum-kort og rum-detaljevisning
- `frontend/indeklima-cards.js`: samme mønster i `indeklima-room-card` og `indeklima-room-detail-card`

## Bevidst afgrænset
- `indeklima-hub-card` og `indeklima-tablet-card` (husoverblik) er **ikke** opdateret med de nye per-rum-detaljer (tilstand/kritisk siden/LED-alarm) — det ville gøre de kompakte oversigts-visninger for overfyldte. De viser stadig kun skimmel + affugter-anbefaling på husniveau, som før.

## Verificeret
- `.header-icon`-selectoren i `indeklima-panel.js` (kendt skrøbeligt punkt) er intakt — alle ændringer er lavet som målrettede, minimale edits, ikke fuld filoverskrivning.
