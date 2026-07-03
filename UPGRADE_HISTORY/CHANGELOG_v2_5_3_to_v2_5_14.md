# Changelog — Indeklima v2.5.3 → v2.5.14

## Version 2.5.14 — 2026-06-02

**Type:** PATCH — Frontend UI/UX
**Fokus:** Rum-tab rensning

### Changed
- **`indeklima-panel.js`**: Fjernet "Skimmelrisiko Oversigt" sektion fra rum-tab — information var en direkte gentagelse af hvad rum-kortene allerede viste
- **Rum-kort rsc-panel**: Udvidet fra 1–2 celler til altid 2–3 celler: Skimmel + Udluftning (ny) + Affugter (kun hvis konfigureret)
- **Score synlig i header**: Alvorligheds-score vises som tal foran status-pill på hvert rum-kort

---

## Version 2.5.13 — 2026-06-02

**Type:** MINOR — Frontend tab-sammenlægning
**Fokus:** Reduceret fra 3 tabs til 2

### Changed
- **`indeklima-panel.js`**: Udluftning-tab fjernet som selvstændig tab
- **Overblik-tab** indeholder nu al udluftnings-information:
  - 3-celle status-panel: Udluftning / Cirkulation / Åbne vinduer
  - Klikbar udluftnings-celle: folder årsager + berørte rum ud inline med animation
  - Udendørs vejr som kompakt linje i score-sektionen
- **Åbne vinduer/døre**: Vises kun hvis der faktisk er nogen åbne — ingen tom boks
- **`_renderVentilation()`** metode fjernet
- Panel er nu 2 tabs: 🏠 Overblik · 🚪 Rum

---

## Version 2.5.12 — 2026-06-02

**Type:** PATCH — Frontend doublon-fix
**Fokus:** Fjern gentaget skimmelinfo fra rum-tab

### Fixed
- **`indeklima-panel.js`**: Fjernet `_renderMoldSection()` kald og metode fra rum-tab — skimmelinfo er allerede synlig direkte på hvert rum-kort via rsc-panelet

---

## Version 2.5.11 — 2026-06-02

**Type:** PATCH — UX-forbedringer (5 stk)

### Changed
- **Udluftnings-farve**: "Luft ud nu!" vises nu i teal (`#0ea5e9`) i stedet for grøn. Grøn er reserveret til "Vent" (alt OK)
- **Årsags-chips med rum**: Ventilations-årsager viser nu rum-navn: "Høj fugtighed – Badeværelse" i stedet for blot "Høj fugtighed"
- **Tendenser kollaps**: Når alle tre trends er "stable" vises én enkelt linje "● Alle målinger er stabile" med pulserende grøn prik — i stedet for 3 identiske kort
- **Sidst opdateret**: Versionslinjen viser klokkeslæt for seneste opdatering: `v2.5.11 · Gold Tier · 14:32`
- **`_ventExpanded`**: State til at folde udluftnings-detalje ud/ind tilføjet til constructor

---

## Version 2.5.10 — 2026-06-02

**Type:** PATCH — Frontend tab-sammenlægning (skimmel)

### Changed
- **`indeklima-panel.js`**: Skimmel-tab (🦠) fjernet som selvstændig tab
- Skimmelrisiko-oversigt integreret som sektion i bunden af rum-tab
- Panel tilbage til 3 tabs: 🏠 Overblik · 🚪 Rum · 🌬️ Udluftning

---

## Version 2.5.9 — 2026-06-02

**Type:** MINOR — Frontend: 4. tab + sparklines + rum-filter

### Added
- **Skimmel-tab (🦠)**: Ny 4. tab med global mold/affugter status panel + per-rum kort med fugt, temperatur, sparkline og affugter-anbefaling
- **Sparklines**: `_sparkline(roomName, key)` — SVG mini-grafer baseret på 30-sekunders historik (max 20 punkter). Vises på rum-kort (severity) og i skimmel-tab (fugtighed)
- **Historik-tracking**: `_history` objekt i constructor gemmer datapunkter per rum ved hvert `_load()` kald
- **Rum-filter**: Filter-bar i rum-tab med "Alle rum (N)" og "⚠️ Problemer (N)" knapper. Tom tilstand viser "✅ Alle rum er i orden"
- **Skimmel i ventilation-tab**: Ny sektion 5 "Skimmelrisiko oversigt" i ventilations-tabben
- **Gold Tier label**: Version-linje opdateret fra "Silver Tier" til "Gold Tier"

### Changed
- Rum-kort: Chips (skimmel + affugter) erstattet med `rsc-*` status-panel (kompakt 2-celle grid)

---

## Version 2.5.8 — 2026-06-02

**Type:** PATCH — Frontend cards

### Changed
- **`indeklima-room-detail-card`**: Udluftning + Skimmel slået sammen til 2-kolonne `.detail-status-grid` layout (`ds-cell` / `ds-full`)
- Affugter vises i fuld bredde under 2-kolonne grid (kun hvis `has_dehumidifier`)

---

## Version 2.5.7 — 2026-06-02

**Type:** PATCH — Frontend cards

### Added
- **`indeklima-hub-card`**: Alvorligheds-bar tilføjet under score-ring — gradient-track (grøn→gul→rød) + farvet fill + markør-prik

---

## Version 2.5.6 — 2026-06-02

**Type:** PATCH — Frontend cards

### Changed
- **`indeklima-room-card`**: Chips (mold + dehum) erstattet med `rc-status` panel — kompakt 1–2 celle grid med farvet bundkant. Vinduer/døre vises stadig som chips over panelet

---

## Version 2.5.5 — 2026-06-02

**Type:** PATCH — Frontend cards

### Added
- **`indeklima-hub-card`**: "Indeklima Status" panel tilføjet — `.status-center` med `.sc-cell` viser skimmel / udluftning / cirkulation / affugter (hvis konfigureret) i kompakt grid

---

## Version 2.5.4 — 2026-06-02

**Type:** PATCH — Frontend cards

### Changed
- **`indeklima-hub-card`**: Rum-layout omskrevet til vertikalt layout per rum
  - Problemrum: fulde kort øverst
  - Grønne rum: kompakte chips i `.ok-rooms-wrap` ("5 rum uden problemer")

---

## Version 2.5.3 — 2026-06-02

**Type:** PATCH — Frontend cards

### Changed
- **`indeklima-room-card`**: Affugter-UI vises kun hvis `has_dehumidifier === true` (tidligere altid vist)

### Backend
- **`__init__.py`**: `has_dehumidifier = bool(room.get(CONF_DEHUMIDIFIER))` beregnes per rum
- **`websocket.py`**: `has_dehumidifier` eksponeres på begge WS-endpoints (`get_climate_data` og `get_room_data`)
