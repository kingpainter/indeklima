# Indeklima

**Multi-rum indeklima-overvågning til Home Assistant** — temperatur, fugtighed, CO₂, VOC, formaldehyd og lufttryk, med skimmelrisiko, affugter-anbefaling og et dansk brugerflade.

![Version](https://img.shields.io/badge/version-2.6.0-blue)
![Quality Scale](https://img.shields.io/badge/quality_scale-gold-gold)
![HACS](https://img.shields.io/badge/HACS-custom-orange)

---

## Om projektet

Indeklima er en custom Home Assistant-integration bygget til at overvåge indeklimaet i flere rum samtidig — og til at hjælpe med at holde det sundt. Integrationen indsamler data fra jeres eksisterende sensorer (temperatur, fugtighed, CO₂, VOC, formaldehyd, lufttryk), beregner en samlet severity-score pr. rum og globalt, og giver konkrete anbefalinger om udluftning og affugtning.

Fra version 2.6.0 kan Indeklima også **styre en fysisk affugter direkte** — tænd/sluk via knap eller automatisk baseret på fugtighed og skimmelrisiko, med LED-feedback og konfigurerbar stilletid.

## Funktioner

- **Multi-rum overvågning** — konfigurér lige så mange rum I vil, hver med sine egne sensorer
- **Severity-score (0-100)** pr. rum og globalt, baseret på fugtighed, CO₂, VOC og formaldehyd
- **Skimmelrisiko-beregning** (`low` / `moderate` / `high` / `critical`) — bruger dedikeret mold-sensor hvis tilgængelig, ellers rummets fugtsensor
- **Affugter-anbefaling** pr. rum og globalt, baseret på skimmelrisiko, fugtighedstendens og udluftningsstatus
- **Indbygget affugter-styring** (v2.6.0+): fysisk knap-toggle, automatisk tænd/sluk, LED-feedback (manuel/automatisk/fra), auto-sluk-timer, konfigurerbar stilletid (globalt + pr. rum)
- **Udluftningsanbefaling** baseret på indeklima og udendørs vejrdata
- **Luftcirkulationsstatus** ud fra åbne interne døre
- **Trends** (stigende/faldende/stabil) for fugtighed, CO₂ og severity over et 30-minutters rullende vindue
- **Vindue-/dørdetektion** med skelnen mellem udendørs og interne åbninger
- **Dansk brugerflade** — engelsk kode og logs, dansk UI og notifikationer
- **Custom Lovelace-panel** med sidebar, rum-oversigt, sparklines og interaktive kort
- **Gold Tier HA Quality Scale** — diagnostics, repair flow, system health, fuld testdækning

## Installation

### Via HACS (anbefalet)

1. Tilføj dette repository som et custom repository i HACS (kategori: Integration)
2. Installér "Indeklima" fra HACS
3. Genstart Home Assistant
4. Gå til **Indstillinger → Enheder & tjenester → Tilføj integration** og søg efter "Indeklima"

### Manuel installation

1. Kopiér `custom_components/indeklima` til jeres `config/custom_components/`-mappe
2. Genstart Home Assistant
3. Tilføj integrationen som beskrevet ovenfor

## Konfiguration

Al konfiguration foregår via UI'et — ingen YAML nødvendig.

### Opsætning af et rum

For hvert rum kan I vælge:

- Fugtigheds-, temperatur-, CO₂-, VOC-, formaldehyd- og tryksensorer (flere af samme type understøttes — gennemsnittet bruges)
- En dedikeret mold-sensor (valgfri — falder ellers tilbage til rummets fugtsensor)
- Vindues-/dørsensorer, markeret som udendørs eller interne
- En affugter (`switch` eller `humidifier`-entitet)
- En affugter-LED (`light`-entitet) til visuel manual/auto/fra-feedback
- En affugter-knap (vilkårlig entitet — understøtter både rigtige knap-entiteter og click-count-sensorer)
- Affugterens auto-sluk-varighed (standard 45 minutter)
- Stilletid-override for netop dette rum

### Globale indstillinger (Indstillinger → Indeklima → Konfigurér)

- **Grænseværdier**: maks. fugtighed sommer/vinter, maks. CO₂, VOC og formaldehyd
- **Vejr-integration**: valgfri `weather`-entitet til udluftningsanbefalinger
- **Stilletid**: globalt tidsvindue hvor affugtere ikke tænder automatisk (medmindre skimmelrisikoen er høj/kritisk)

## Entiteter

**Hub-niveau** (ca. 19 sensorer): gennemsnit for hver målt størrelse, samlet severity-score og status, antal åbne vinduer, luftcirkulation, trends, udluftnings- og affugteranbefaling, skimmelrisiko.

**Pr. rum**: status, temperatur, fugtighed, CO₂, lufttryk (hvis konfigureret), skimmelrisiko og affugteranbefaling (med `tilstand`-attribut der viser manual/auto/fra).

## Dokumentation

- [`CHANGELOG_v{version}.md`](.) — per-version ændringslog
- [`HA_COMPLIANCE.md`](HA_COMPLIANCE.md) — detaljeret gennemgang af Quality Scale-krav
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) — fejlfinding
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — bidrag til projektet

## Licens

Se [`LICENSE`](LICENSE).
