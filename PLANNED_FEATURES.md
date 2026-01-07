# Indeklima Planned Features

> ⚠️ **VIGTIGT**: Denne fil beskriver features der er **planlagt** men endnu ikke implementeret i v2.0.0

## 🚧 Status: Under Udvikling

Disse features er under aktivt arbejde og vil blive inkluderet i fremtidige versioner.

---

## 🌬️ Ventilationsanbefalinger (v2.1)

### Planlagt Sensor: `sensor.indeklima_hub_ventilationsanbefaling`

Denne sensor vil analysere indeklimaet og give intelligente anbefalinger om hvornår du skal lufte ud.

#### States:
- **`Ja`** - Du bør lufte ud nu
- **`Nej`** - Vent med at lufte ud
- **`Valgfrit`** - Det er op til dig (enten fordi vinduer allerede er åbne, eller betingelserne er grænsende)

#### Attributes:
```yaml
begrundelse: "Høj fugtighed, Høj CO2"
rum: "Stue, Køkken"
ude_temperatur: 12.5
ude_fugtighed: 65
```

### Beslutningslogik:

#### 1. Tjek Om Vinduer Er Åbne
```
Hvis vinduer åbne → Status: "Valgfrit"
Begrundelse: "Vinduer allerede åbne"
```

#### 2. Analyser Indeklima
```
Problem → Årsag
─────────────────────────
Fugtighed > max → "Høj fugtighed"
CO2 > max → "Høj CO2"
VOC > max → "Høj VOC"
```

#### 3. Tjek Udendørs Forhold
```
Hvis ingen vejr data:
  → Anbefal ventilation baseret på indeklima

Hvis vejr data tilgængelig:
  Temperatur < 5°C → "Valgfrit" (for koldt ude)
  Fugtighed > max → "Nej" (for fugtigt ude)
  Ellers → "Ja" (gode forhold)
```

### Dashboard Eksempel (Fremtidig):

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

## 🔔 Per-Rum Notifikationer (v2.1)

### Automation Blueprint (Planlagt)

Indeklima vil inkludere en automation blueprint der gør det nemt at sætte notifikationer op per rum.

#### Placering:
```
config/blueprints/automation/indeklima/room_notification.yaml
```

#### Features:

##### 1. Rum-Specifik
```yaml
room_sensor: sensor.indeklima_stue_status
notify_service: notify.mobile_app_flemming
```

##### 2. Smart Cooldown
```yaml
cooldown_hours: 2  # Minimum tid mellem beskeder
```

##### 3. Tidsstyring
```yaml
time_start: "09:00:00"
time_end: "21:00:00"
```

##### 4. Severity Threshold
```yaml
severity_threshold: "Advarsel"  # Eller "Dårlig"
```

##### 5. Ventilations Tips
```yaml
include_ventilation_tip: true
```

#### Eksempel Besked (Fremtidig):

```
🏠 Indeklima: Stue

Status: Advarsel

🌡️ Fugtighed: 62%
💨 CO2: 1150 ppm
🌡️ Temperatur: 22.5°C

💡 Ventilation: Ja
Høj fugtighed, Høj CO2
```

---

## 📲 Automatisk Device Kontrol (v2.2)

### Affugter Automation

```yaml
# Planlagt funktionalitet
automation:
  - alias: "Automatisk Affugter - Badeværelse"
    trigger:
      - platform: numeric_state
        entity_id: sensor.indeklima_badevaerelse_status
        attribute: fugtighed
        above: 65
    
    action:
      - service: humidifier.turn_on
        target:
          entity_id: humidifier.badevaerelse_affugter
```

### Fan Control

```yaml
# Planlagt funktionalitet
automation:
  - alias: "Automatisk Ventilator - Køkken"
    trigger:
      - platform: numeric_state
        entity_id: sensor.indeklima_koekken_status
        attribute: co2
        above: 1200
    
    action:
      - service: fan.turn_on
        target:
          entity_id: fan.koekken_emhaette
```

---

## 🎯 Use Cases (Fremtidige)

### Use Case 1: Lukas' Værelse

**Problem:** Lukas glemmer at lufte ud, luften bliver dårlig om natten.

**Løsning (v2.1):**
```yaml
# Vil blive muligt med automation blueprint
trigger:
  - platform: state
    entity_id: sensor.indeklima_lukas_vaerelse_status
    to: "Advarsel"
    for:
      minutes: 5

condition:
  - condition: time
    after: "07:00"
    before: "22:00"
  - condition: state
    entity_id: sensor.indeklima_hub_ventilationsanbefaling
    state: "Ja"

action:
  - service: notify.mobile_app_lukas
    data:
      title: "💨 Luft ud!"
      message: |
        Din værelse trænger til frisk luft!
        
        Fugtighed: {{ state_attr('sensor.indeklima_lukas_vaerelse_status', 'fugtighed') }}%
        
        👍 Godt tidspunkt at åbne vinduet nu!
```

### Use Case 2: Badeværelse Efter Bad

**Problem:** Høj fugtighed efter bad, risiko for skimmelsvamp.

**Løsning (v2.2):**
```yaml
# Automatisk affugter kontrol
trigger:
  - platform: numeric_state
    entity_id: sensor.indeklima_badevaerelse_status
    attribute: fugtighed
    above: 70
    for:
      minutes: 10

action:
  - service: humidifier.turn_on
    target:
      entity_id: humidifier.badevaerelse_affugter
```

---

## 🗺️ Implementerings Roadmap

### v2.1 (Q1 2025)
- [ ] Ventilationsanbefaling sensor
- [ ] Automation blueprint
- [ ] Weather integration forbedringer
- [ ] Diagnostics platform

### v2.2 (Q2 2025)
- [ ] Automatisk device kontrol
- [ ] Service calls for manuel kontrol
- [ ] Advanced notifikations system
- [ ] Integration med ventilationssystemer

### v3.0 (Q3-Q4 2025)
- [ ] Machine learning patterns
- [ ] Predictive maintenance
- [ ] Energy optimization
- [ ] Multi-home support

---

## 💡 Nuværende Workarounds

Indtil disse features er implementeret, kan du bruge disse løsninger:

### Manual Ventilations Check
```yaml
# Simpel automation baseret på severity
automation:
  - alias: "Høj Severity - Overvej Ventilation"
    trigger:
      - platform: numeric_state
        entity_id: sensor.indeklima_hub_severity_score
        above: 50
    
    action:
      - service: notify.family
        data:
          message: "Indeklima score høj - overvej at lufte ud"
```

### Simple Notifikationer
```yaml
# Per-rum advarsel uden blueprint
automation:
  - alias: "Indeklima Advarsel - Stue"
    trigger:
      - platform: state
        entity_id: sensor.indeklima_stue_status
        to: "Advarsel"
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
            Fugtighed: {{ state_attr('sensor.indeklima_stue_status', 'fugtighed') }}%
            CO2: {{ state_attr('sensor.indeklima_stue_status', 'co2') }} ppm
```

---

## 🤝 Hjælp Til!

Vil du hjælpe med at implementere disse features?

1. Fork projektet på GitHub
2. Vælg en feature fra roadmap
3. Opret en feature branch
4. Submit en Pull Request

Eller bare giv feedback på hvilke features du synes er vigtigst!

---

**Disse features kommer snart! 🚀**