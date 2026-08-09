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
