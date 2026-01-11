# Indeklima v2.0 Upgrade Guide

## 🎉 Hvad Er Nyt i v2.0?

### ✅ Implementeret (FASE 1-4)

#### Version Styring
- ✅ Alle filer har version nummer
- ✅ manifest.json opdateret til v2.0.0
- ✅ CHANGELOG.md med fuld historik
- ✅ Semantic versioning (MAJOR.MINOR.PATCH)

#### Forbedret Config Flow (FASE 1 & 2)
- ✅ **Per-rum konfiguration** - Tilføj rum ét ad gangen
- ✅ **Rum menu** - Oversigt over alle rum under setup
- ✅ **Options flow** - Rediger efter installation:
  - ✅ Rediger eksisterende rum
  - ✅ Slet enkelte rum
  - ✅ Tilføj nye rum når som helst
- ✅ **Affugter support** - Vælg affugter per rum (klar til fremtidig automation)
- ✅ **Fan/Ventilator support** - Vælg ventilator per rum (klar til fremtidig automation)
- ✅ **Vejr sensor valg** - Brug custom vejr data eller HA default
- ✅ **Per-rum notifikationer** - Vælg hvem der får besked om hvert rum

#### Device Organization (FASE 3)
- ✅ **Hub device** - "Indeklima Hub" med globale sensorer
- ✅ **Room devices** - Separat device per rum
- ✅ **Modern entity naming** - `has_entity_name = True`
- ✅ **Device info** - Manufacturer, Model, SW Version
- ✅ **Device classes** - Korrekte device classes for sensorer

#### Smart Features (FASE 4)
- ✅ **Trend analyse** - 30-minutters trends for fugtighed, CO2 og severity
- ✅ **Multiple sensors** - Flere sensorer per rum med automatisk gennemsnit
- ✅ **Window tracking** - Hold styr på åbne vinduer
- ✅ **Severity scoring** - Intelligent beregning af indeklima kvalitet

#### Translations & Compliance
- ✅ **Modern translations** - strings.json + da.json backup
- ✅ **HA_COMPLIANCE.md** - Detaljeret dokumentation
- ✅ **Silver tier** - Opfylder alle Silver tier krav

---

## 🚧 Ikke Implementeret (Kommer i v2.1+)

### FASE 5 & 6 - Planlagt
- 🔲 **Ventilationsanbefalinger** - Smart sensor der analyserer vejr vs. indeklima
- 🔲 **Automation blueprint** - Færdig notifikations-automation
- 🔲 **Automatisk device kontrol** - Affugtere og fans
- 🔲 **Diagnostics platform** - Gold tier requirement

Se [PLANNED_FEATURES.md](PLANNED_FEATURES.md) for detaljer om kommende features.

---

## 📦 Installation af v2.0

### Ny Installation
1. Kopier alle filer til `/config/custom_components/indeklima/`
2. Genstart Home Assistant
3. Gå til Indstillinger → Enheder & Tjenester
4. Klik + Tilføj Integration → Søg "Indeklima"
5. Følg den nye guided setup!

### Opdatering fra v1.0
⚠️ **VIGTIGT**: v2.0 er en **breaking change**

**Anbefalet metode:**
1. Eksporter din nuværende konfiguration (noter alle rum og sensorer)
2. Slet den gamle Indeklima integration
3. Installer v2.0
4. Konfigurer rum igen (nu meget nemmere!)

**Alternativt (avancerede brugere):**
1. Backup `.storage/core.config_entries`
2. Opdater filerne
3. Genstart og test

---

## 🎯 Brug af v2.0 Features

### Device Organization

Efter installation vil du se:

**Indeklima Hub** (Hub device)
- `sensor.indeklima_hub_severity_score`
- `sensor.indeklima_hub_status`
- `sensor.indeklima_hub_gennemsnitlig_fugtighed`
- `sensor.indeklima_hub_gennemsnitlig_temperatur`
- `sensor.indeklima_hub_gennemsnitlig_co2`
- `sensor.indeklima_hub_aabne_vinduer`
- `sensor.indeklima_hub_fugtigheds_trend`
- `sensor.indeklima_hub_co2_trend`
- `sensor.indeklima_hub_severity_trend`

**Indeklima [Rum Navn]** (Per rum)
- `sensor.indeklima_[rum]_status` med attributes:
  - fugtighed + fugtighed_sensorer
  - temperatur + temperatur_sensorer
  - co2 + co2_sensorer
  - voc + voc_sensorer
  - formaldehyd + formaldehyd_sensorer

### Redigering af Rum
1. Gå til Indeklima integrationen
2. Klik "Konfigurer"
3. Vælg "🏠 Administrer rum"
4. Vælg det rum du vil redigere
5. Opdater sensorer/enheder
6. Gem - integration reloader automatisk!

### Tilføjelse af Affugter/Fan
1. Administrer rum → Rediger rum
2. Vælg "Affugter" eller "Fan/Ventilator" dropdown
3. Find din enhed
4. Gem

**Note:** Disse enheder er **forberedt til fremtidig automation** men kontrolleres ikke automatisk i v2.0. Se [PLANNED_FEATURES.md](PLANNED_FEATURES.md) for kommende funktionalitet.

### Per-rum Notifikationer
1. Administrer rum → Rediger rum
2. Vælg "Notifikationer sendes til"
3. Vælg én eller flere notify services
4. Lav din egen automation der bruger denne konfiguration

**Eksempel:**
```yaml
automation:
  - alias: "Indeklima Advarsel - Stue"
    trigger:
      - platform: state
        entity_id: sensor.indeklima_stue_status
        to: "Advarsel"
    action:
      - service: notify.mobile_app_flemming
        data:
          message: "Stue indeklima er dårligt!"
```

### Vejr Integration
1. Indstillinger → "🌤️ Vejr integration"
2. Vælg din foretrukne vejr sensor
3. Eller lad feltet være tomt for HA standard

**Note:** Vejr data er forberedt til fremtidige ventilationsanbefalinger.

### Trend Analyse

Alle trend sensorer opdateres baseret på 30 minutters historik:

- `sensor.indeklima_hub_fugtigheds_trend` - Stigende/Faldende/Stabil
- `sensor.indeklima_hub_co2_trend`
- `sensor.indeklima_hub_severity_trend`

**Brug i dashboard:**
```yaml
type: entities
title: 📈 Trends (30 min)
entities:
  - sensor.indeklima_hub_fugtigheds_trend
  - sensor.indeklima_hub_co2_trend
  - sensor.indeklima_hub_severity_trend
```

---

## 🆕 Nye Entity Names

v2.0 bruger moderne entity naming (`has_entity_name = True`):

### Før (v1.0):
```
sensor.indeklima_severity_score
sensor.indeklima_status
sensor.indeklima_gennemsnitlig_fugtighed
sensor.indeklima_stue_status
```

### Efter (v2.0):
```
sensor.indeklima_hub_severity_score
sensor.indeklima_hub_status
sensor.indeklima_hub_gennemsnitlig_fugtighed
sensor.indeklima_stue_status
```

**Hvis du opdaterer fra v1.0:**
- Dine dashboards skal opdateres med nye entity IDs
- Dine automations skal opdateres
- Tag backup før opdatering!

---

## 🐛 Kendte Problemer

### v2.0.0 
Ingen kendte kritiske fejl.

### Begrænsninger
- Ventilationsanbefalinger er endnu ikke implementeret
- Automatisk device control mangler
- Automation blueprints mangler

**Workarounds:**
- Brug simple automations i stedet for blueprints
- Manuel device kontrol indtil automation er klar
- Se [PLANNED_FEATURES.md](PLANNED_FEATURES.md) for workarounds

---

## 🔄 Migration Checklist

Hvis du opgraderer fra v1.0:

- [ ] Backup din Home Assistant konfiguration
- [ ] Noter alle rum og deres sensorer ned
- [ ] Tag screenshots af dine dashboards
- [ ] Eksporter dine Indeklima automations
- [ ] Slet gamle Indeklima integration
- [ ] Installer v2.0
- [ ] Konfigurer rum igen via UI
- [ ] Opdater dashboard entity IDs
- [ ] Opdater automation entity IDs
- [ ] Test alt virker

---

## 📞 Support

**Problemer?**
1. Tjek logs: Indstillinger → System → Logs
2. Søg efter `indeklima` fejl
3. Opret issue på GitHub med:
   - Logs
   - Beskrivelse af problem
   - Steps to reproduce

**Feature requests?**
- Åbn GitHub issue
- Beskriv use case
- Vi prioriterer efter brugerønsker!

---

## 🗺️ Roadmap

### v2.1 (Q1 2025)
- 🌬️ Ventilationsanbefalinger
- 🔔 Automation blueprint
- 📲 Diagnostics platform

### v2.2 (Q2 2025)
- 🤖 Automatisk device kontrol
- ⚡ Service calls
- 🔗 Ventilationssystem integration

### v3.0 (Q3-Q4 2025)
- 🧠 Machine learning
- 📊 Predictive maintenance
- ⚡ Energy optimization
- 🏘️ Multi-home support

---

**Velkommen til Indeklima v2.0! 🎉**