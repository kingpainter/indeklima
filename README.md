# 🏠 Indeklima - Home Assistant Custom Integration

En avanceret Home Assistant integration til overvågning af indeklima med intelligent analyse og smarte ventilationsanbefalinger.

**Version:** 2.1.0  
**Quality Scale:** Silver Tier

Se [CHANGELOG.md](CHANGELOG.md) for fuld version historik.

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

-------------------------------------------------------------
## ✨ Features

### ✅ Implementeret
- 🌡️ **Multi-room overvågning**: Overvåg fugtighed, temperatur, CO2, VOC og formaldehyd i flere rum
- 📊 **Intelligent severity scoring**: Automatisk beregning af indeklima kvalitet (0-100)
- 🔄 **Flere sensorer per rum**: Brug flere sensorer af samme type i ét rum - gennemsnittet beregnes automatisk
- 📈 **Trend-analyse**: 30-minutters trends for fugtighed, CO2 og severity
- 🪟 **Vindue tracking**: Hold styr på åbne vinduer og døre
- 🏠 **Per-rum konfiguration**: Tilføj, rediger og slet rum individuelt
- ⚙️ **Fuld options flow**: Administrer alt efter installation
- 💨 **Dehumidifier support**: Forbered til fremtidig automation
- 🌀 **Fan/Ventilator support**: Forbered til fremtidig automation
- 🌞 **Sæsonbaserede grænser**: Forskellige grænser for sommer og vinter
- 🏷️ **Device organization**: Moderne hub + room device struktur
- 🌍 **Multi-language**: Dansk og engelsk
- 🌬️ **Ventilationsanbefalinger**: Smart sensor der analyserer indeklima og vejr (NYT i v2.1!)
- 📱 **Automation Blueprint**: Færdig notifikations-automation med cooldown (NYT i v2.1!)

## 📦 Installation

### Via HACS (Anbefalet)

1. Åbn HACS i Home Assistant
2. Gå til "Integrations"
3. Gå til Tilføj Custom Repositories ( https://github.com/kingpainter/indeklima ) gem
4. Klik på "+" og søg efter "Indeklima"
5. Klik "Download"
6. Genstart Home Assistant
7. Gå til Indstillinger → Enheder & Tjenester → Tilføj Integration
8. Søg efter "Indeklima"

### Manuel Installation

1. Kopier `custom_components/indeklima` mappen til din Home Assistant `custom_components` mappe
2. Genstart Home Assistant
3. Gå til Indstillinger → Enheder & Tjenester → Tilføj Integration
4. Søg efter "Indeklima"

## ⚙️ Konfiguration

### Første opsætning

1. Tilføj integrationen via UI
2. Tilføj dine rum et ad gangen:
   - **Rum navn**: F.eks. "Stue", "Køkken", "Soveværelse"
   - **Sensorer**: Vælg relevante sensorer for rummet
   - Du kan vælge **flere sensorer af samme type** - gennemsnittet vil automatisk blive beregnet
   - Fugtighed (påkrævet for det meste funktionalitet)
   - Temperatur (valgfri, understøtter flere sensorer)
   - CO2, VOC, Formaldehyd (valgfri, understøtter flere sensorer)
   - Vindue/dør sensorer (valgfri, understøtter flere sensorer)
   - **Devices** (valgfri - til fremtidig automation):
     - Affugter
     - Ventilator/Fan
   - **Notifikationer** (valgfri): Vælg hvem der skal modtage advarsler om dette rum

### Indstillinger

Du kan justere grænseværdier via integrationens indstillinger:

- **Max fugtighed sommer**: Standard 60%
- **Max fugtighed vinter**: Standard 55%
- **Max CO2**: Standard 1000 ppm
- **Max VOC**: Standard 3.0 mg/m³
- **Max Formaldehyd**: Standard 0.15 mg/m³
- **Vejr entity**: Vælg din vejr sensor (bruges til ventilationsanbefalinger)

### Efter Installation

Via **Options Flow** kan du:
- ✏️ Rediger eksisterende rum
- 🗑️ Slet enkelte rum
- ➕ Tilføj nye rum
- ⚙️ Juster grænseværdier
- 🌤️ Skift vejr sensor

## 📊 Sensorer

### Hub Sensors (Indeklima Hub device)
Globale sensorer der aggregerer data fra alle rum:

- `sensor.indeklima_hub_severity_score` - Samlet indeklima score (0-100)
- `sensor.indeklima_hub_status` - God/Advarsel/Dårlig/Kritisk
- `sensor.indeklima_hub_gennemsnitlig_fugtighed` - Gennemsnit på tværs af alle rum
- `sensor.indeklima_hub_gennemsnitlig_temperatur`
- `sensor.indeklima_hub_gennemsnitlig_co2`
- `sensor.indeklima_hub_gennemsnitlig_voc`
- `sensor.indeklima_hub_gennemsnitlig_formaldehyd`
- `sensor.indeklima_hub_aabne_vinduer` - Liste over rum med åbne vinduer
- `sensor.indeklima_hub_fugtigheds_trend` - Stigende/Faldende/Stabil
- `sensor.indeklima_hub_co2_trend`
- `sensor.indeklima_hub_severity_trend`
- `sensor.indeklima_hub_ventilationsanbefaling` - Ja/Nej/Valgfrit (NYT i v2.1!)

### Room Sensors
For hvert rum oprettes en device med en status sensor:

**Eksempel:** `sensor.indeklima_stue_status`

**State:** God/Advarsel/Dårlig

**Attributes:**
```yaml
fugtighed: 55.5
fugtighed_sensorer: 2
temperatur: 21.3
temperatur_sensorer: 1
co2: 850
co2_sensorer: 1
voc: 120
voc_sensorer: 1
formaldehyd: 45
formaldehyd_sensorer: 1
last_notified: "2025-01-11T14:30:00+00:00"  # NYT i v2.1!
```

## 🌬️ Ventilationsanbefalinger (NYT i v2.1!)

### Sensor: `sensor.indeklima_hub_ventilationsanbefaling`

Denne sensor analyserer dit indeklima og giver intelligente anbefalinger om hvornår du skal lufte ud.

**States:**
- **Ja** - Du bør lufte ud nu (godt indeklima + gode udeforhold)
- **Nej** - Vent med at lufte ud (enten godt indeklima eller dårlige udeforhold)
- **Valgfrit** - Det er op til dig (vinduer allerede åbne eller grænsetilfælde)

**Attributes:**
```yaml
begrundelse: "Høj fugtighed, Høj CO2"
rum: "Stue, Køkken"
ude_temperatur: 12.5
ude_fugtighed: 65
```

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

## 📱 Automation Blueprint (NYT i v2.1!)

Indeklima inkluderer nu en færdig automation blueprint til per-rum notifikationer!

### Installation

1. **Enable python_script** i configuration.yaml:
```yaml
python_script:
```

2. **Kopier filer:**
```
config/python_scripts/indeklima_set_last_notified.py
config/blueprints/automation/indeklima/room_notification.yaml
```

3. **Genstart Home Assistant**

### Brug Blueprint

1. Gå til Settings → Automations & Scenes
2. Klik "+ Create Automation"
3. Vælg "Indeklima - Rum Notifikation v2.1"
4. Konfigurer:
   - Rum sensor
   - Notifikations service
   - Severity threshold
   - Cooldown timer (standard 2 timer)
   - Aktiv fra/til tidspunkt
   - Inkluder ventilations tip

### Features

- ✅ Smart cooldown system (ingen spam)
- ✅ Tidsstyring (kun i åbningstider)
- ✅ Severity threshold valg
- ✅ Inkluderer ventilationsanbefalinger
- ✅ Per-rum konfiguration

## 🎨 Dashboard Eksempel

### Simpel Oversigt
```yaml
type: vertical-stack
cards:
  # Hovedstatus
  - type: custom:mushroom-template-card
    primary: |
      {% set s = states('sensor.indeklima_hub_severity_score') | int(0) %}
      {% if s > 70 %}🚨 Kritisk indeklima
      {% elif s > 40 %}⚠️ Kræver opmærksomhed
      {% else %}✅ Godt indeklima{% endif %}
    secondary: |
      Severity: {{ states('sensor.indeklima_hub_severity_score') }}/100
      Status: {{ states('sensor.indeklima_hub_status') }}
      Trend: {{ states('sensor.indeklima_hub_severity_trend') }}
    icon: mdi:home-thermometer
    icon_color: |
      {% set s = states('sensor.indeklima_hub_severity_score') | int(0) %}
      {% if s > 70 %}red
      {% elif s > 40 %}orange
      {% else %}green{% endif %}

  # Ventilationsanbefaling (NYT!)
  - type: custom:mushroom-template-card
    primary: |
      {% set status = states('sensor.indeklima_hub_ventilationsanbefaling') %}
      {% if status == 'Ja' %}🌬️ Luft ud nu!
      {% elif status == 'Valgfrit' %}🤔 Overvej at lufte
      {% else %}⏳ Vent med at lufte{% endif %}
    secondary: |
      {{ state_attr('sensor.indeklima_hub_ventilationsanbefaling', 'begrundelse') }}

  # Gennemsnit
  - type: grid
    columns: 3
    square: false
    cards:
      - type: statistic
        entity: sensor.indeklima_hub_gennemsnitlig_fugtighed
        name: Fugtighed
        period: hour
      - type: statistic
        entity: sensor.indeklima_hub_gennemsnitlig_temperatur
        name: Temperatur
        period: hour
      - type: statistic
        entity: sensor.indeklima_hub_gennemsnitlig_co2
        name: CO2
        period: hour

  # Trends
  - type: entities
    title: 📈 Trends (30 min)
    entities:
      - entity: sensor.indeklima_hub_fugtigheds_trend
        name: Fugtighed
      - entity: sensor.indeklima_hub_co2_trend
        name: CO2
      - entity: sensor.indeklima_hub_severity_trend
        name: Severity

  # Rum oversigt
  - type: custom:auto-entities
    card:
      type: entities
      title: 🏠 Rum Status
    filter:
      include:
        - entity_id: "sensor.indeklima_*_status"
          options:
            secondary_info: last-changed
    sort:
      method: state
      reverse: true
```

### Per-Rum Kort
```yaml
type: custom:mushroom-entity-card
entity: sensor.indeklima_stue_status
name: Stue
icon: mdi:sofa
secondary_info: |
  💧 {{ state_attr('sensor.indeklima_stue_status', 'fugtighed') }}%
  💨 {{ state_attr('sensor.indeklima_stue_status', 'co2') }} ppm
  🌡️ {{ state_attr('sensor.indeklima_stue_status', 'temperatur') }}°C
```

## 🔔 Notifikationer

### Med Blueprint (Anbefalet)
Se [Automation Blueprint](#-automation-blueprint-nyt-i-v21) sektionen ovenfor.

### Simpel Automation
```yaml
automation:
  - alias: "Indeklima Advarsel - Stue"
    trigger:
      - platform: state
        entity_id: sensor.indeklima_stue_status
        to: 
          - "Advarsel"
          - "Dårlig"
        for:
          minutes: 5
    
    condition:
      - condition: time
        after: "08:00"
        before: "22:00"
    
    action:
      - service: notify.mobile_app_flemming
        data:
          title: "⚠️ Indeklima: Stue"
          message: |
            Status: {{ states('sensor.indeklima_stue_status') }}
            
            💧 Fugtighed: {{ state_attr('sensor.indeklima_stue_status', 'fugtighed') }}%
            💨 CO2: {{ state_attr('sensor.indeklima_stue_status', 'co2') }} ppm
```

## 🤝 Bidrag

Bidrag er meget velkomne! 

1. Fork projektet
2. Opret en feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit dine ændringer (`git commit -m 'Add some AmazingFeature'`)
4. Push til branchen (`git push origin feature/AmazingFeature`)
5. Åbn en Pull Request

## 📍 Roadmap

### v2.2 (Q1 2025)
- [ ] Automatisk device kontrol (affugtere, fans)
- [ ] Integration med ventilationssystemer
- [ ] Advanced notifikations system
- [ ] Service calls for manuel kontrol

### v3.0 (Q2-Q4 2025)
- [ ] Machine learning for mønstergenkendelse
- [ ] Historisk analyse og rapporter
- [ ] Multi-home support
- [ ] Energy optimization
- [ ] Diagnostics platform (Gold tier)

## 🐛 Fejlrapportering

Fandt du en fejl? [Opret et issue](https://github.com/kingpainter/indeklima/issues)

## 📄 Licens

MIT License - se [LICENSE](LICENSE) filen for detaljer

## 🙏 Credits

Udviklet med ❤️ til Home Assistant fællesskabet
