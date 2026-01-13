# Upgrade Guide: v2.1.0 → v2.2.0

## 🎉 Hvad Er Nyt i v2.2.0?

### ✅ Nye Features

1. **🪟 Indoor/Outdoor Window Tracking**
   - Skelne mellem udvendige vinduer og interne døre
   - Udvendige: Fører til frisk luft (bruges til ventilation)
   - Interne: Mellem rum (bruges til luftcirkulation)

2. **🌬️ Luftcirkulation Sensor**
   - Ny sensor: `sensor.indeklima_hub_luftcirkulation`
   - States: "God", "Moderat", "Dårlig"
   - Baseret på antal åbne interne døre

3. **📊 Forbedrede Ventilationsanbefalinger**
   - Kun eksterne vinduer tæller som "allerede ventilerer"
   - Mere præcise anbefalinger

4. **🎯 Severity Bonus**
   - 5% reduktion i severity hvis interne døre er åbne
   - Bedre luftcirkulation = lavere score

---

## 📦 Installation

### Fra v2.1.0 (Anbefalet Path)

Dette er en **backward-compatible** opdatering med automatisk migration!

#### Step 1: Opdater Filer
```
1. Kopier alle opdaterede filer til custom_components/indeklima/
2. Tjek at version er 2.2.0 i:
   - manifest.json
   - const.py
```

#### Step 2: Genstart Home Assistant
```
Settings → System → Restart
```

#### Step 3: Konfigurer Vinduer (Valgfrit)

Dine eksisterende vinduer/døre er automatisk sat til "udvendige" (backward compatibility).

For at konfigurere indoor/outdoor:

```
1. Gå til Indeklima integration
2. Klik "Configure"
3. Vælg "🏠 Administrer rum"
4. Rediger hvert rum
5. På vindue/dør skærmen: Marker hvilke der fører til udendørs
6. Gem
```

**Eksempel:**
- ✅ Stue vindue → Marker "Fører til udendørs"
- ✅ Altandør → Marker "Fører til udendørs"
- ❌ Badeværelsesdør → IKKE markeret (intern)
- ❌ Walk-in dør → IKKE markeret (intern)

---

## 🆕 Nye Sensorer

### Hub Sensors

**`sensor.indeklima_hub_luftcirkulation`**
- **State:** "God" / "Moderat" / "Dårlig"
- **Attributes:**
  - `interne_døre_åbne`: Antal
  - `rum_med_åbne_døre`: Liste

**`sensor.indeklima_hub_aabne_vinduer`** (Opdateret)
- **State:** Antal åbne UDVENDIGE vinduer
- **Attributes:**
  - `rum`: Rum med åbne eksterne vinduer
  - `count`: Antal eksterne vinduer
  - `interne_døre_rum`: Rum med åbne interne døre (NYT)
  - `interne_døre_count`: Antal interne døre (NYT)

### Room Sensor Attributes (Opdateret)

Alle room sensors har nu:

```yaml
sensor.indeklima_stue_status:
  attributes:
    vinduer_udendørs_åbne: 0     # NYT
    døre_interne_åbne: 1         # NYT
    luftcirkulation_bonus: true  # NYT - hvis intern dør åben
```

---

## 🎨 Dashboard Eksempler

### Luftcirkulation Kort

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
  {{ state_attr('sensor.indeklima_hub_luftcirkulation', 'interne_døre_åbne') }} interne døre åbne
  
  Rum: {{ state_attr('sensor.indeklima_hub_luftcirkulation', 'rum_med_åbne_døre') }}
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

### Opdateret Vindue Oversigt

```yaml
type: entities
title: 🪟 Vinduer & Døre Status
entities:
  - entity: sensor.indeklima_hub_aabne_vinduer
    name: Udvendige Vinduer Åbne
    secondary_info: last-changed
  - type: attribute
    entity: sensor.indeklima_hub_aabne_vinduer
    attribute: rum
    name: Rum med åbne vinduer
  - type: divider
  - entity: sensor.indeklima_hub_luftcirkulation
    name: Luftcirkulation Status
  - type: attribute
    entity: sensor.indeklima_hub_aabne_vinduer
    attribute: interne_døre_count
    name: Interne Døre Åbne
```

### Per-Rum Vindue Status

```yaml
type: custom:mushroom-entity-card
entity: sensor.indeklima_stue_status
name: Stue
secondary_info: |
  🪟 {{ state_attr('sensor.indeklima_stue_status', 'vinduer_udendørs_åbne') }} eksterne
  🚪 {{ state_attr('sensor.indeklima_stue_status', 'døre_interne_åbne') }} interne
  {% if state_attr('sensor.indeklima_stue_status', 'luftcirkulation_bonus') %}
  ✅ Luftcirkulation bonus aktiv
  {% endif %}
```

---

## 🔧 Migration Details

### Automatisk Migration

Når du opgraderer fra v2.1.0:

1. **Gamle format** (string list):
```python
"window_sensors": [
    "binary_sensor.stue_vindue",
    "binary_sensor.altan_door"
]
```

2. **Konverteres automatisk til**:
```python
"window_sensors": [
    {
        "entity_id": "binary_sensor.stue_vindue",
        "is_outdoor": True  # Default = outdoor
    },
    {
        "entity_id": "binary_sensor.altan_door",
        "is_outdoor": True
    }
]
```

### Manuel Konfiguration

Efter opdatering kan du manuelt konfigurere hvilke vinduer/døre der er interne:

```
Settings → Integrations → Indeklima
→ Configure → 🏠 Administrer rum
→ Rediger rum → Vindue/Dør konfiguration
```

For hver dør/vindue:
- ✅ Markeret = Fører til udendørs (bruges til ventilation)
- ❌ Ikke markeret = Intern dør (bruges til luftcirkulation)

---

## 🎯 Nye Beregninger

### Severity Bonus

Hvis interne døre er åbne:
```
Original severity: 50
Luftcirkulation bonus: × 0.95
Ny severity: 47.5 (5% reduktion)
```

### Luftcirkulation Status

```
≥ 3 interne døre åbne → "God"
≥ 1 intern dør åben   → "Moderat"
0 interne døre åbne   → "Dårlig"
```

### Ventilationsanbefaling

**Før v2.2:**
```
ANY vinduer/døre åben → "Valgfrit" (allerede ventilerer)
```

**Efter v2.2:**
```
KUN eksterne vinduer åbne → "Valgfrit"
Kun interne døre åbne     → "Ja" (stadig brug for ventilation)
```

---

## 💡 Use Cases

### Use Case 1: Badeværelse Efter Bad

**Før:**
- Badeværelsesdør åben → System tror du ventilerer
- Ventilationsanbefaling: "Valgfrit"

**Efter:**
- Badeværelsesdør = intern → Kun luftcirkulation
- Ventilationsanbefaling: "Ja - Åbn vindue!"
- Severity: -5% (god luftcirkulation)

### Use Case 2: Walk-in Closet

**Før:**
- Walk-in dør åben → Tæller som ventilation
- Misvisende "åbne vinduer" count

**Efter:**
- Walk-in dør = intern → Kun luftcirkulation
- Korrekt "åbne vinduer" count
- Luftcirkulation bonus hvis dør åben

### Use Case 3: Altandør Om Sommeren

**Før:**
- Altandør åben → Fungerer korrekt

**Efter:**
- Altandør = ekstern → Fungerer korrekt
- Stadig tæller som ventilation
- Ingen ændring (backward compatible)

---

## 📊 Dashboard Automation Eksempler

### Notifikation: Dårlig Luftcirkulation

```yaml
automation:
  - alias: "Advarsel - Dårlig Luftcirkulation"
    trigger:
      - platform: state
        entity_id: sensor.indeklima_hub_luftcirkulation
        to: "Dårlig"
        for:
          minutes: 30
    
    condition:
      - condition: numeric_state
        entity_id: sensor.indeklima_hub_severity_score
        above: 40
    
    action:
      - service: notify.family
        data:
          title: "🚪 Åbn nogle døre!"
          message: |
            Luftcirkulationen er dårlig og indeklimaet er ikke optimalt.
            
            Overvej at åbne døre mellem rum for bedre cirkulation.
```

### Automation: Forbedret Ventilationsanbefaling

```yaml
automation:
  - alias: "Smart Ventilationsanbefaling"
    trigger:
      - platform: state
        entity_id: sensor.indeklima_hub_ventilationsanbefaling
        to: "Ja"
        for:
          minutes: 5
    
    condition:
      # Kun hvis INGEN eksterne vinduer er åbne
      - condition: numeric_state
        entity_id: sensor.indeklima_hub_aabne_vinduer
        below: 1
    
    action:
      - service: notify.family
        data:
          title: "🌬️ Tid til at lufte ud!"
          message: |
            {{ state_attr('sensor.indeklima_hub_ventilationsanbefaling', 'begrundelse') }}
            
            Rum: {{ state_attr('sensor.indeklima_hub_ventilationsanbefaling', 'rum') }}
            
            {% if state_attr('sensor.indeklima_hub_aabne_vinduer', 'interne_døre_count') | int > 0 %}
            ✅ God luftcirkulation ({{ state_attr('sensor.indeklima_hub_aabne_vinduer', 'interne_døre_count') }} interne døre åbne)
            {% else %}
            💡 Overvej også at åbne døre mellem rum
            {% endif %}
```

---

## 🛠️ Troubleshooting

### Problem: Gamle vinduer vises ikke i config

**Fix:**
1. Gå til rum konfiguration
2. Re-select vinduer/døre
3. Konfigurer outdoor/indoor
4. Gem

### Problem: Luftcirkulation sensor viser altid "Dårlig"

**Tjek:**
1. Er dine interne døre konfigureret korrekt?
2. Er de contact sensors i "off" state når åben?
3. Se Developer Tools → States

### Problem: Severity ændrer sig ikke med åbne døre

**Debug:**
```yaml
# Check room data
{{ state_attr('sensor.indeklima_stue_status', 'døre_interne_åbne') }}
{{ state_attr('sensor.indeklima_stue_status', 'luftcirkulation_bonus') }}

# Check severity
{{ states('sensor.indeklima_hub_severity_score') }}
```

---

## ✅ Tjekliste

Efter opdatering:

- [ ] Version 2.2.0 i Settings → Integrations → Indeklima
- [ ] `sensor.indeklima_hub_luftcirkulation` eksisterer
- [ ] Åbne vinduer count er korrekt (kun eksterne)
- [ ] Konfigurer interne døre per rum
- [ ] Test at severity bonus virker
- [ ] Opdater dashboard med nye sensorer

---

## 🎯 Næste Skridt

### v2.3 (Planlagt)
- Automatisk affugter kontrol baseret på luftcirkulation
- Fan automation: Tænd hvis dårlig cirkulation
- Severity notification per room med cooldown

---

**Velkommen til Indeklima v2.2.0! 🎉**

Nyd intelligent indoor/outdoor tracking! 🪟