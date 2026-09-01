# Changelog v2.9.9

**Date:** 2026-08-09
**Focus:** `indeklima-tablet-card` — VOC/formaldehyd i Gennemsnit, ny venstre-side, fill-layout, og en kritisk websocket.py-bugfix

---

## Baggrund

Sessionen startede som en simpel opgave (tilpas `indeklima-tablet-card` til en ny 11" Samsung Galaxy Tab A11+, og tilføj to nye "piller" — VOC og Formaldehyd — under Gennemsnit), men blev undervejs kompliceret af to reelle infrastrukturproblemer der først skulle findes og rettes, før layoutarbejdet gav mening at teste:

1. **Fil-synkroniseringsproblem**: `indeklima-cards.js` blev flere gange tilbagerullet til en ældre version midt i sessionen (sandsynligvis pga. OneDrive-synkronisering eller en editor med autosave på GitHub-mappen), hvilket fik flere runders arbejde til at forsvinde. Løst ved at bekræfte filens indhold og `modified`-tidsstempel efter hver ændring, og til sidst ved at få eksplicit lov til at skrive direkte til både GitHub-mappen og live-serveren for at eliminere det manuelle kopieringstrin som fejlkilde.
2. **Cache-bug i `panel.py`**: `async_register_panel()` beregner cache-busting-tidsstemplet (`?v=...&m=<mtime>`) for Lovelace-ressource-URL'en **kun én gang, ved integrations-opstart** — ikke hver gang JS-filen gemmes. Det betyder at selv en 100% korrekt opdateret fil på disken forblev usynlig for browseren, indtil integrationen blev genindlæst (Indstillinger → Enheder & Tjenester → Indeklima → Genindlæs), fordi Lovelace-dashboardet blev ved med at hente den samme gamle URL. Dette forklarede en stor del af dagens "det virker stadig ikke"-forvirring.

## Ændret — `websocket.py` (kritisk bugfix)

- `ws_get_climate_data`'s `averages`-payload var **hardcodet whitelistet** til kun at videresende `humidity`, `temperature`, `co2` og `pressure` — selvom coordinatoren (`__init__.py`) allerede beregnede `voc` og `formaldehyde` korrekt, når mindst ét rum havde de relevante sensorer konfigureret. Frontend'en kunne derfor aldrig vise VOC/formaldehyd, uanset hvor korrekt kort-koden var, fordi felterne blev filtreret væk i broen mellem backend og frontend.
- Tilføjet `"voc": averages.get("voc")` og `"formaldehyde": averages.get("formaldehyde")` til payloadet.
- Dette er præcis den type fejl projektets egne regler advarer om: *"websocket.py er den kritiske bro: ethvert nyt coordinator-felt skal eksplicit tilføjes alle relevante payload-steder i websocket.py, ellers er det usynligt for frontend'en."*

## Ændret — `indeklima-cards.js` (`IndeklimaTabletCard` — designet i flere runder ud fra skærmbillede-feedback)

**Gennemsnit-sektionen:**
- Tilføjet VOC-celle (`avgs.voc`, 1 decimal, mg/m³, lilla accentkant) og Formaldehyd-celle (`avgs.formaldehyde`, 2 decimaler pga. den lave grænseværdi på 0,15 mg/m³, rød/pink accentkant) — begge betinget vist (`!= null`) ligesom de eksisterende celler.
- Gitteret er 2 kolonner (ikke 3) — ved 6 mulige celler giver det 3 rækker, ét ekstra lag end de 4 celler under Status (2 rækker), så cellehøjden mellem de to sektioner blev afstemt via en 4:3 flex-fordeling (`.green-top`/`.green-bottom`) i stedet for 50/50, for at kompensere for at Status-sektionen har en ekstra fast overhead (streg + label) som Gennemsnit ikke har.

**Venstre kolonne (score-blok):**
- Ringen, badgen og info-teksten ("X rum" / "Y åbne vinduer") er nu stablet lodret (ring øverst, badge derunder, info i et separat "flottere" kort med baggrund) i stedet for en vandret række — efter eksplicit ønske om at ringen skal "fylde mere" og matche bredden af feltet nedenunder.
- Ringens diameter er ændret fra en fast pixelværdi til `width:100%` med `aspect-ratio:1/1`, så den automatisk følger kolonnens bredde fremover, uden at kræve manuel genjustering hver gang kolonnebredden ændres.
- Tendenser- og Vinduer/døre-sektionerne er pakket i en fælles `.col1-fill`-container der fordeler den resterende højde mellem sig (`justify-content:space-evenly`).

**Midterkolonne (rumliste):**
- `.rooms-list` og hver `.room-row` er `flex:1`, så rækkerne altid strækker sig til at fylde hele den tilgængelige højde, uanset hvor mange rum der er konfigureret — ingen tomt felt forneden længere.

**Alle tre kolonner — bredde-fix:**
- `grid-template-columns` ændret fra en hardcodet `175px 1fr 175px` til `minmax(0,200px) 1fr minmax(0,200px)`. Den oprindelige faste bredde kunne aldrig blive smallere end sig selv, uanset den faktiske skærmbredde — hvilket var den egentlige, tilbagevendende årsag til at højre kolonne blev skåret af i kanten på visse skærmstørrelser. `minmax(0, …)` lader kolonnen krympe når pladsen mangler, i stedet for at skubbe indhold uden for skærmen. De 200px er samtidig 25px mere end det oprindelige design (175px), taget fra midterkolonnen, for at give cellerne lidt mere albuerum — venstre og højre kolonne forbliver altid lige brede.

## Ikke ændret

- `indeklima-hub-card` og `indeklima-room-detail-card` er urørte denne session.
- Selve databeregningen i `__init__.py` (coordinatoren) var allerede korrekt for VOC/formaldehyd — det var kun broen (`websocket.py`) der manglede.

## Lærte regler

- **Version-bump alene løser ikke cache-problemer i denne integration** — Lovelace-ressource-URL'en genberegnes kun ved `async_register_panel()`, dvs. ved integrations-genindlæsning eller HA-genstart. En ren fil-opdatering på disken er ikke nok til at ændringer bliver synlige.
- **Whitelistede payload-dicts i websocket.py er en tilbagevendende fælde** — når et nyt coordinator-felt tilføjes (som VOC/formaldehyd i en tidligere session), skal `ws_get_climate_data` og `ws_get_room_data` tjekkes eksplicit for om feltet rent faktisk bliver videresendt, ikke kun antaget.
- **Fast pixel-bredde (`Npx`) på grid/flex-tracks bør som udgangspunkt være `minmax(0, Npx)`** i denne kortdesign, medmindre man er 100% sikker på den mindste skærmbredde kortet nogensinde vil blive vist på — ellers er beskæring i kanten kun et spørgsmål om tid.

---

## Opfølgende session (samme dag) — Deep dive + ikon-oprydning i `indeklima-panel.js`

**Kontekst:** Flemming bad om et fuldt deep-dive af backend, frontend, UX og funktionalitet, med en samlet rapport. Under gennemgangen af `indeklima-panel.js` blev det opdaget at et stort antal ikoner i selve render-funktionerne (`_renderOverview`, `_renderRooms`, `_renderRoomDetail`) alle var blevet erstattet af den samme forkerte streng: `\uD83D\uDCCA-` (bar-chart-emoji + bindestreg), eller i nogle tilfælde bare en bar bindestreg. Dette ramte:

- Temperatur-, fugt- og CO₂-ikonerne i alle tre visninger (overblik, rumliste, rum-detalje)
- Vindue-tælleren og vindue/dør-chips
- Opdater-knappen og "Opdaterer…"-statusbadgen
- Begge faneblade (Overblik/Rum)
- Luk-knappen på rum-detalje-visningen
- Fold ud/ind-pilen på udluftnings-cellen (begge tilstande viste samme tegn)
- CO₂-labelen ("CO₂" var blevet til "CO-" — subscript-2 var væk)

Samtidig var et par danske bogstaver (Å, ø, é) i nærliggende kommentarer og UI-tekst også blevet til en bindestreg — samme type korruption, bredere end kun emoji. Ingen af disse ting er nævnt i tidligere session-logs, så det er sandsynligvis sket i en session der ikke blev logget, eller ved en fejlslået søg/erstat-operation.

**Vigtigt at bemærke:** Selve ikon-hjælpefunktionerne (`_ventIcon`, `_circIcon`, `_moldIcon`, `_dehumIcon` osv.) var **helt intakte** — kun de emoji der var hardkodet direkte inde i render-metoderne var ramt. `indeklima-cards.js` (Lovelace-kortene) var slet ikke berørt.

**Rettelser i `indeklima-panel.js`:**
- Alle `\uD83D\uDCCA-`-forekomster erstattet med det korrekte ikon ud fra konteksten: 🌡️ (temperatur), 💧 (fugt), 🪧 (CO₂ — en boble-lignende ikon, matcher `\uD83E\uDEA7` som allerede blev brugt korrekt andre steder i samme fil), 🪟 (udendørs vindue), 🚪 (intern dør), 🔄 (opdater), ⏳ (vejrdata ikke tilgængelig).
- Faneblade fik hver deres eget ikon (📊 Overblik, 🏠 Rum) i stedet for det samme forkerte ikon på begge.
- Luk-knappen fik et rigtigt kryds (✕) i stedet for en bindestreg.
- Fold ud/ind-pilen skelner nu mellem tilstandene (▲ udfoldet, ▼ sammenfoldet).
- "CO-" rettet til "CO₂" (med korrekt Unicode-subscript) alle steder.
- De korrupte danske bogstaver rettet: "Udend-rs" → "Udendørs", "i -n boks" → "i én boks", "-bne vinduer" → "Åbne vinduer" (både i en kommentar og i selve UI-teksten).
- Fjernet den forældede kommentar `// overview | rooms | ventilation | mold` i klassens constructor — kun `overview` og `rooms` findes som faneblade i dag.
- Version-fallback i headeren ændret fra det hardcodede `"2.5.2"` (en rest fra en meget tidligere version) til et neutralt `"—"`, så den ikke kræver vedligeholdelse ved fremtidige releases.

**Rettelse i `indeklima-cards.js`:**
- `IndeklimaRoomDetailCard`'s `metricCell()`-kald brugte rå emoji-unicode-escapes (`\uD83C\uDF21\uFE0F` osv.), mens de tre andre kort (`IndeklimaRoomCard`, `IndeklimaHubCard`, `IndeklimaTabletCard`) alle bruger HTML-entities (`&#127777;&#65039;` osv.) for samme ikoner. Ensrettet til HTML-entity-stilen for konsistens på tværs af korttyperne. Ingen visuel ændring — kun kode-stil.

**Verificering:** Begge filer valideret med `node --check` efter alle rettelser — ingen syntaksfejl. Flemming bekræftede visuelt at panelet nu ser korrekt ud.

**Lærte regler:**
- Ved en fuld kodegennemgang er det værd at grep'e efter mistænkeligt ensartede/gentagne strenge (som det samme emoji + bindestreg optrædende dusinvis af steder med forskellig tiltaenkt betydning) — det er et stærkt signal om en fejlslået bulk-operation, ikke tilsigtet design.
- Korruption af denne art rammer sjældent kun emoji-escapes; tjek altid for beslægtet skade på almindelige multi-byte tegn (her: danske Å/ø/é) i samme fil, da de kan være ramt af samme underliggende fejl.
