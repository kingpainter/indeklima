# 🏠 Indeklima - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Version](https://img.shields.io/badge/version-2.2.0-blue.svg)](https://github.com/kingpainter/indeklima)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Avanceret indeklima overvågning for Home Assistant med multi-room support, intelligent severity scoring, trend-analyse og ventilationsanbefalinger.

**Current Version:** 2.2.0  
**Quality Scale:** Silver Tier ⭐️

---

## ✨ Features

### ✅ Implementeret (v2.2.0)

#### 🪟 Window & Door Tracking
- **Indoor/Outdoor Classification** - Skelne mellem udvendige vinduer og interne døre
- **Smart Window Detection** - Udvendige vinduer bruges til ventilationsanbefalinger
- **Air Circulation Tracking** - Interne døre bruges til luftcirkulationsberegning
- **Flexible Configuration** - Let at angive hvilke åbninger der fører til udendørs

#### 🌬️ Air Circulation System
- **Luftcirkulation Sensor** - Overvåg luftcirkulation mellem rum (God/Moderat/Dårlig)
- **Severity Bonus** - 5% reduktion i severity score ved god luftcirkulation
- **Real-time Monitoring** - Se hvilke interne døre der er åbne
- **Room-by-room Status** - Hver rum viser antal åbne døre og vinduer

#### 🌡️ Climate Monitoring
- **Multi-room overvågning** - Overvåg fugtighed, temperatur, CO2, VOC og formaldehyd
- **Intelligent severity scoring** - Automatisk beregning af indeklima kvalitet (0-100)
- **Flere sensorer per rum** - Brug flere sensorer af samme type - gennemsnit beregnes automatisk
- **Sæsonbaserede grænser** - Forskellige tærskler for sommer og vinter

#### 📈 Trend Analysis
- **30-minutters trends** - Stigende/Faldende/Stabil for fugtighed, CO2 og severity
- **Historical tracking** - Automatisk historik med 6 datapunkter
- **Smart alerts** - Få besked når trends er negative

#### 🌬️ Ventilation Recommendations (v2.1)
- **Smart anbefalinger** - Ja/Nej/Valgfrit baseret på indeklima og vejr
- **Weather integration** - Tager højde for udendørs temperatur og fugtighed
- **Room-specific** - Viser præcist hvilke rum der trænger til udluftning
- **Begrundelse** - Forklarer hvorfor du skal eller ikke skal lufte ud

#### 🏠 Configuration & Management
- **Per-rum konfiguration** - Tilføj, rediger og slet rum individuelt
- **Fuld options flow** - Administrer alt efter installation via UI
- **Device organization** - Moderne hub + room device struktur
- **Multi-language** - Dansk og engelsk support

#### 🤖 Automation Ready
- **Automation Blueprint** - Færdig notifikations-automation med cooldown (v2.1)
- **Dehumidifier support** - Klar til fremtidig automatisk kontrol
- **Fan/Ventilator support** - Klar til fremtidig automatisk kontrol
- **Smart cooldown** - Undgå for mange notifikationer med last_notified tracking

### 🚧 Planlagt (v2.3+)
- 📲 Automatisk device kontrol (affugtere, fans)
- 🎯 Diagnostics platform (Gold tier)
- 🔗 Integration med ventilationssystemer
- 🧠 Machine learning patterns
- ⚡ Energy optimization

---

## 📦 Installation

### Via HACS (Anbefalet)

1. Åbn HACS i Home Assistant
2. Gå til "Integrations"
3. Klik på de tre prikker øverst til højre
4. Vælg "Custom repositories"
5. Tilføj: `https://github.com/kingpainter/indeklima`
6. Kategori: "Integration"
7. Klik "Add"
8. Find "Indeklima" og klik "Download"
9. Genstart Home Assistant

### Manuel Installation

1. Download latest release fra [GitHub Releases](https://github.com/kingpainter/indeklima/releases)
2. Pak zip-filen ud
3. Kopier `custom_components/indeklima` til din Home Assistant `custom_components` folder
4. Genstart Home Assistant

---

## ⚙️ Konfiguration

### Initial Setup

1. Gå til **Settings** → **Devices & Services**
2. Klik **+ Add Integration**
3. Søg efter "Indeklima"
4. Følg setup wizard:
   - Giv integration et navn
   - Tilføj rum ét ad gangen
   - Vælg sensorer per rum
   - Konfigurer hvilke vinduer/døre der fører til udendørs
   - Vælg valgfrie enheder (affugter, fan)

### Per-Room Configuration

For hvert rum kan du vælge:

- **Humidity sensors** (0-mange) - Gennemsnit beregnes automatisk
- **Temperature sensors** (0-mange)
- **CO2 sensors** (0-mange)
- **VOC sensors** (0-mange)
- **Formaldehyde sensors** (0-mange)
- **Window/Door sensors** (0-mange) - Marker hvilke der fører til udendørs
- **Dehumidifier** (valgfri) - Klar til fremtidig automation
- **Fan/Ventilator** (valgfri) - Klar til fremtidig automation
- **Notification targets** (0-mange) - Hvem får besked om dette rum?

### Window/Door Classification

Efter valg af window sensors, skal du angive hvilke der fører til udendørs:

- ✅ **Markeret** = Udvendig vindue/dør (bruges til ventilation)
- ❌ **Ikke markeret** = Intern dør (bruges til luftcirkulation)

**Eksempler:**
- Stue vindue → ✅ Udvendig (fører til frisk luft)
- Altan dør → ✅ Udvendig (fører til udendørs)
- Badeværelse dør → ❌ Intern (mellem rum)
- Walk-in dør → ❌ Intern (mellem rum)

---

## 📊 Sensorer

### Hub Sensors (Indeklima Hub device)

Globale sensorer der aggregerer data fra alle rum:

| Sensor | Beskrivelse | Enhed |
|--------|-------------|-------|
| `sensor.indeklima_hub_severity_score` | Samlet indeklima score | 0-100 |
| `sensor.indeklima_hub_status` | God/Advarsel/Dårlig | - |
| `sensor.indeklima_hub_gennemsnitlig_fugtighed` | Gennemsnit på tværs af rum | % |
| `sensor.indeklima_hub_gennemsnitlig_temperatur` | Gennemsnit på tværs af rum | °C |
| `sensor.indeklima_hub_gennemsnitlig_co2` | Gennemsnit på tværs af rum | ppm |
| `sensor.indeklima_hub_gennemsnitlig_voc` | Gennemsnit på tværs af rum | ppb |
| `sensor.indeklima_hub_gennemsnitlig_formaldehyd` | Gennemsnit på tværs af rum | µg/m³ |
| `sensor.indeklima_hub_aabne_vinduer` | Antal åbne EKSTERNE vinduer | stk |
| `sensor.indeklima_hub_luftcirkulation` | **NYT v2.2!** God/Moderat/Dårlig | - |
| `sensor.indeklima_hub_fugtigheds_trend` | Stigende/Faldende/Stabil (30 min) | - |
| `sensor.indeklima_hub_co2_trend` | Stigende/Faldende/Stabil (30 min) | - |
| `sensor.indeklima_hub_severity_trend` | Stigende/Faldende/Stabil (30 min) | - |
| `sensor.indeklima_hub_ventilationsanbefaling` | **v2.1** Ja/Nej/Valgfrit | - |

### Room Sensors

For hvert rum oprettes en device med en status sensor:

**Eksempel:** `sensor.indeklima_stue_status`

**State:** God/Advarsel/Dårlig

**Attributes:**
```yaml
fugtighed: 55.5                   # Gennemsnit hvis flere sensorer
fugtighed_sensorer: 2             # Antal sensorer brugt
temperatur: 21.3
temperatur_sensorer: 1
co2: 850
co2_sensorer: 1
voc: 120
voc_sensorer: 1
formaldehyd: 45
formaldehyd_sensorer: 1
vinduer_udendørs_åbne: 0          # NYT v2.2!
døre_interne_åbne: 1              # NYT v2.2!
luftcirkulation_bonus: true       # NYT v2.2! - True hvis interne døre åbne
last_notified: "2025-01-11T14:30:00+00:00"  # v2.1 - Til cooldown
```

---

## 🌬️ Luftcirkulation (NYT i v2.2!)

### Sensor: `sensor.indeklima_hub_luftcirkulation`

Denne sensor overvåger luftcirkulation mellem rum baseret på åbne interne døre.

**States:**
- **God** - 3+ interne døre åbne (god luftcirkulation mellem rum)
- **Moderat** - 1-2 interne døre åbne (moderat cirkulation)
- **Dårlig** - Ingen interne døre åbne (dårlig cirkulation)

**Attributes:**
```yaml
interne_døre_åbne: 2
rum_med_åbne_døre: "Stue, Badeværelse"
```

**Impact:**
- God luftcirkulation giver **5% severity bonus**
- Bedre fordeling af varme og fugt mellem rum
- Mindre risiko for lokale problemer

### Dashboard Eksempel

```yaml
type: custom:mushroom-template-card
primary: |
  {% set circ = states('sensor.indeklima_hub_luftcirkulation') %}
  {% if circ == 'God' %}
    🌬️ God luftcirkulation
  {% elif circ == 'Moderat' %}
    🌀 Moderat luftcirkulation
  {% else %}
    🚪 Dårlig luftcirkulation
  {% endif %}
secondary: |
  {{ state_attr('sensor.indeklima_hub_luftcirkulation', 'interne_døre_åbne') }} døre åbne
  
  {% set rooms = state_attr('sensor.indeklima_hub_luftcirkulation', 'rum_med_åbne_døre') %}
  {% if rooms != 'Ingen' %}
  Rum: {{ rooms }}
  {% endif %}
icon: |
  {% set circ = states('sensor.indeklima_hub_luftcirkulation') %}
  {% if circ == 'God' %}mdi:fan
  {% elif circ == 'Moderat' %}mdi:fan-speed-2
  {% else %}mdi:fan-off{% endif %}
icon_color: |
  {% set circ = states('sensor.indeklima_hub_luftcirkulation') %}
  {% if circ == 'God' %}green
  {% elif circ == 'Moderat' %}orange
  {% else %}red{% endif %}
```

---

## 🌬️ Ventilationsanbefalinger (v2.1)

### Sensor: `sensor.indeklima_hub_ventilationsanbefaling`

Smart sensor der analyserer indeklima og vejrforhold for at give intelligente ventilationsanbefalinger.

**States:**
- **Ja** - Du bør lufte ud nu (gode forhold, problemer indendørs)
- **Nej** - Vent med at lufte ud (dårlige forhold udendørs)
- **Valgfrit** - Op til dig (vinduer allerede åbne eller grænsetilfælde)

**Attributes:**
```yaml
begrundelse: "Høj fugtighed, Høj CO2"
rum: "Stue, Køkken"
ude_temperatur: 12.5
ude_fugtighed: 65
```

### Beslutningslogik

1. **Tjek om vinduer er åbne** (kun eksterne!)
   - Hvis ja → Status: "Valgfrit" (allerede ventilering)

2. **Analyser indeklima**
   - Fugtighed > max → Problem
   - CO2 > max → Problem
   - VOC > max → Problem

3. **Tjek vejrforhold** (hvis konfigureret)
   - Temperatur < 5°C → "Valgfrit" (for koldt)
   - Fugtighed > max → "Nej" (for fugtigt ude)
   - Ellers → "Ja" (gode forhold)

### Dashboard Eksempel

```yaml
type: custom:mushroom-template-card
primary: |
  {% set status = states('sensor.indeklima_hub_ventilationsanbefaling') %}
  {% if status == 'Ja' %}
    🌬️ Luft ud nu!
  {% elif status == 'Valgfrit' %}
    🤔 Overvej at lufte ud
  {% else %}
    ⏳ Vent med at lufte
  {% endif %}
secondary: |
  {{ state_attr('sensor.indeklima_hub_ventilationsanbefaling', 'begrundelse') }}
  
  {% set rooms = state_attr('sensor.indeklima_hub_ventilationsanbefaling', 'rum') %}
  {% if rooms and rooms != 'Ingen specifikke' %}
  **Rum:** {{ rooms }}
  {% endif %}
icon: |
  {% set status = states('sensor.indeklima_hub_ventilationsanbefaling') %}
  {% if status == 'Ja' %}mdi:window-open-variant
  {% elif status == 'Valgfrit' %}mdi:window-open
  {% else %}mdi:window-closed{% endif %}
icon_color: |
  {% set status = states('sensor.indeklima_hub_ventilationsanbefaling') %}
  {% if status == 'Ja' %}green
  {% elif status == 'Valgfrit' %}orange
  {% else %}red{% endif %}
```

---

## 🔔 Notifikationer (v2.1+)

### Automation Blueprint

Indeklima inkluderer en færdig automation blueprint for per-rum notifikationer:

**Features:**
- ✅ Per-rum notifikationer
- ✅ Smart cooldown (undgå spam)
- ✅ Tidsstyring (kun i åbningstider)
- ✅ Severity threshold (kun ved Advarsel/Dårlig)
- ✅ Inkluderer ventilations tips

**Installation:**
1. Kopier `blueprints/automation/indeklima/room_notification.yaml` til `config/blueprints/automation/indeklima/`
2. Kopier `python_scripts/indeklima_set_last_notified.py` til `config/python_scripts/`
3. Enable python_script i `configuration.yaml`:
   ```yaml
   python_script:
   ```
4. Genstart Home Assistant

**Brug:**
1. Gå til Settings → Automations & Scenes → Blueprints
2. Find "Indeklima - Rum Notifikation"
3. Klik "Create Automation"
4. Konfigurer rum og indstillinger

---

## 🎨 Dashboard Eksempler

### Komplet Indeklima Overview

```yaml
type: vertical-stack
cards:
  # Header
  - type: custom:mushroom-title-card
    title: 🏠 Indeklima Status
    subtitle: v2.2.0
  
  # Overall Status
  - type: horizontal-stack
    cards:
      - type: custom:mushroom-entity-card
        entity: sensor.indeklima_hub_severity_score
        name: Severity Score
        icon: mdi:alert-decagram
        icon_color: |
          {% set score = states('sensor.indeklima_hub_severity_score') | float %}
          {% if score < 30 %}green
          {% elif score < 60 %}orange
          {% else %}red{% endif %}
      
      - type: custom:mushroom-entity-card
        entity: sensor.indeklima_hub_status
        name: Status
        icon: mdi:home-thermometer
  
  # Air Circulation (NEW v2.2!)
  - type: custom:mushroom-template-card
    primary: |
      {% set circ = states('sensor.indeklima_hub_luftcirkulation') %}
      {% if circ == 'God' %}🌬️ God luftcirkulation
      {% elif circ == 'Moderat' %}🌀 Moderat luftcirkulation
      {% else %}🚪 Dårlig luftcirkulation{% endif %}
    secondary: |
      {{ state_attr('sensor.indeklima_hub_luftcirkulation', 'interne_døre_åbne') }} interne døre åbne
    icon: mdi:fan
    icon_color: |
      {% set circ = states('sensor.indeklima_hub_luftcirkulation') %}
      {% if circ == 'God' %}green
      {% elif circ == 'Moderat' %}orange
      {% else %}red{% endif %}
  
  # Windows Status
  - type: entities
    title: 🪟 Vinduer & Døre
    entities:
      - entity: sensor.indeklima_hub_aabne_vinduer
        name: Udvendige Vinduer Åbne
        icon: mdi:window-open
      - type: attribute
        entity: sensor.indeklima_hub_aabne_vinduer
        attribute: rum
        name: Rum med åbne vinduer
  
  # Averages
  - type: entities
    title: 📊 Gennemsnit
    entities:
      - sensor.indeklima_hub_gennemsnitlig_fugtighed
      - sensor.indeklima_hub_gennemsnitlig_temperatur
      - sensor.indeklima_hub_gennemsnitlig_co2
  
  # Trends
  - type: entities
    title: 📈 Trends (30 min)
    entities:
      - sensor.indeklima_hub_fugtigheds_trend
      - sensor.indeklima_hub_co2_trend
      - sensor.indeklima_hub_severity_trend
  
  # Ventilation Recommendation
  - type: custom:mushroom-template-card
    primary: |
      {% set status = states('sensor.indeklima_hub_ventilationsanbefaling') %}
      {% if status == 'Ja' %}🌬️ Luft ud nu!
      {% elif status == 'Valgfrit' %}🤔 Overvej at lufte ud
      {% else %}⏳ Vent med at lufte{% endif %}
    secondary: |
      {{ state_attr('sensor.indeklima_hub_ventilationsanbefaling', 'begrundelse') }}
    icon: mdi:window-open-variant
    icon_color: |
      {% set status = states('sensor.indeklima_hub_ventilationsanbefaling') %}
      {% if status == 'Ja' %}green
      {% elif status == 'Valgfrit' %}orange
      {% else %}red{% endif %}
```

### Per-Room Cards

```yaml
type: custom:mushroom-entity-card
entity: sensor.indeklima_stue_status
name: Stue
icon: mdi:sofa
secondary_info: |
  💧 {{ state_attr('sensor.indeklima_stue_status', 'fugtighed') }}%
  🌡️ {{ state_attr('sensor.indeklima_stue_status', 'temperatur') }}°C
  💨 {{ state_attr('sensor.indeklima_stue_status', 'co2') }} ppm
  🪟 {{ state_attr('sensor.indeklima_stue_status', 'vinduer_udendørs_åbne') }} vinduer
  🚪 {{ state_attr('sensor.indeklima_stue_status', 'døre_interne_åbne') }} døre
```

---

## ⚙️ Indstillinger

### Grænseværdier

Juster grænseværdier efter behov:

| Parameter | Sommer | Vinter | Standard |
|-----------|--------|--------|----------|
| **Max Fugtighed** | 40-80% | 30-70% | 60% / 55% |
| **Max CO2** | 800-2000 ppm | - | 1000 ppm |
| **Max VOC** | 1.0-10.0 mg/m³ | - | 3.0 mg/m³ |
| **Max Formaldehyd** | 0.05-0.5 mg/m³ | - | 0.15 mg/m³ |

**Adgang:**
Settings → Integrations → Indeklima → Configure → ⚙️ Grænseværdier

### Vejr Integration

Konfigurer vejr sensor for bedre ventilationsanbefalinger:

1. Settings → Integrations → Indeklima → Configure
2. Vælg "🌤️ Vejr integration"
3. Vælg din foretrukne vejr sensor
4. Eller lad tom for HA default

---

## 🔧 Fejlfinding

### Sensorer Viser "Unknown"

**Problem:** Sensor viser "unknown" eller "unavailable"

**Løsning:**
1. Tjek at sensor entities findes og er tilgængelige
2. Tjek at sensor returnerer numerisk værdi
3. Se Home Assistant logs: Settings → System → Logs
4. Filtrer på "indeklima"

### Window/Door Status Forkert

**Problem:** Vinduer vises som lukkede når de er åbne

**Løsning:**
1. Tjek at din binary_sensor bruger standard "on/off" states
2. "on" = åben, "off" = lukket
3. Gå til Developer Tools → States
4. Find din window sensor og verificer state

### Luftcirkulation Viser Altid "Dårlig"

**Problem:** Selvom døre er åbne, vises "Dårlig"

**Løsning:**
1. Verificer at interne døre er konfigureret korrekt
2. Gå til Integration → Configure → Administrer rum
3. Rediger rum → Window/Door configuration
4. Sørg for at interne døre IKKE er markeret som "fører til udendørs"

### Ventilationsanbefaling Virker Ikke

**Problem:** Sensor viser altid "Nej" eller "unknown"

**Løsning:**
1. Tjek at mindst ét rum har sensorer konfigureret
2. Konfigurer vejr sensor for bedre anbefalinger
3. Verificer at grænseværdier er sat korrekt

---

## 📝 Changelog

Se [CHANGELOG.md](CHANGELOG.md) for fuld version historik.

### v2.2.0 (2025-01-12)
- 🪟 Indoor/Outdoor vindue klassifikation
- 🌬️ Luftcirkulation sensor
- 🎯 Severity bonus for god luftcirkulation
- 📊 Forbedrede room attributes
- ✅ Fixed window state logic (on = open)

### v2.1.0 (2025-01-11)
- 🌬️ Ventilationsanbefalinger
- 📱 Automation Blueprint
- 🔔 Last notified tracking

### v2.0.0 (2025-01-04)
- 🏠 Device organization
- ✨ Modern entity naming
- 📈 Trend analysis

### v1.0.0 (2025-01-02)
- 🎉 Initial release

---

## 🤝 Bidrag

Bidrag er meget velkomne!

1. Fork projektet
2. Opret en feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit dine ændringer (`git commit -m 'Add some AmazingFeature'`)
4. Push til branch (`git push origin feature/AmazingFeature`)
5. Åbn en Pull Request

---

## 📄 Licens

Dette projekt er licenseret under MIT License - se [LICENSE](LICENSE) filen for detaljer.

---

## 🙏 Anerkendelser

- Home Assistant community
- HACS team
- Alle bidragsydere

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/kingpainter/indeklima/issues)
- **Discussions:** [GitHub Discussions](https://github.com/kingpainter/indeklima/discussions)
- **Documentation:** [GitHub Wiki](https://github.com/kingpainter/indeklima/wiki)


**Made with ❤️ by KingPainter**