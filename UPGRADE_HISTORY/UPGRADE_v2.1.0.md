# Upgrade Guide: v2.0.0 → v2.1.0

## 🎉 Hvad Er Nyt i v2.1.0?

### ✅ Nye Features

1. **🌬️ Ventilationsanbefaling**
   - Smart sensor: `sensor.indeklima_hub_ventilationsanbefaling`
   - States: "Ja", "Nej", "Valgfrit"
   - Analyserer indeklima + vejrforhold
   - Anbefaler præcist hvornår du skal lufte ud

2. **📱 Automation Blueprint**
   - Færdig notifikations-automation
   - Smart cooldown system
   - Inkluderer ventilations tips
   - Fuld per-rum support

3. **🔔 Last Notified Tracking**
   - Alle room sensors tracker sidste notifikation
   - `last_notified` attribute tilgængeligt
   - Bruges til intelligent cooldown

---

## 📦 Installation

### Fra v2.0.0 (Anbefalet Path)

Dette er en **backward-compatible** opdatering! Ingen breaking changes.

#### Step 1: Opdater Filer
```
1. Kopier alle opdaterede filer til custom_components/indeklima/
2. Tjek at version er 2.1.0 i:
   - manifest.json
   - const.py
```

#### Step 2: Genstart Home Assistant
```
Settings → System → Restart
```

#### Step 3: Tjek Nye Sensorer
Efter genstart vil du se:
- ✅ `sensor.indeklima_hub_ventilationsanbefaling`
- ✅ `last_notified` attribute på alle room sensors

#### Step 4: Installer Python Script (Valgfrit)
Hvis du vil bruge blueprintet:

```
1. Enable python_script integration i configuration.yaml:
   python_script:

2. Opret folder: config/python_scripts/

3. Kopier indeklima_set_last_notified.py til python_scripts/

4. Genstart Home Assistant
```

#### Step 5: Installer Blueprint (Valgfrit)
```
1. Opret folder: config/blueprints/automation/indeklima/

2. Kopier room_notification.yaml til blueprints/automation/indeklima/

3. Gå til Settings → Automations & Scenes → Blueprints

4. Blueprint skulle være tilgængelig nu!
```

---

## 🌬️ Brug Ventilationsanbefaling

### Dashboard Kort

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

### Simple Automation

```yaml
automation:
  - alias: "Notifikation - Tid Til At Lufte Ud"
    trigger:
      - platform: state
        entity_id: sensor.indeklima_hub_ventilationsanbefaling
        to: "Ja"
        for:
          minutes: 5
    
    action:
      - service: notify.family
        data:
          title: "🌬️ Tid til at lufte ud!"
          message: |
            {{ state_attr('sensor.indeklima_hub_ventilationsanbefaling', 'begrundelse') }}
            
            Rum: {{ state_attr('sensor.indeklima_hub_ventilationsanbefaling', 'rum') }}
```

---

## 📱 Brug Automation Blueprint

### Opret Automation Fra Blueprint

1. **Gå til Settings → Automations & Scenes**
2. **Klik "+ Create Automation"**
3. **Vælg "Indeklima - Rum Notifikation v2.1"**
4. **Konfigurer:**

```yaml
Rum Sensor: sensor.indeklima_stue_status
Notifikations Service: notify.mobile_app_flemming
Alvorligheds Tærskel: Advarsel
Cooldown Timer: 2 timer
Aktiv Fra: 09:00
Aktiv Til: 21:00
Inkluder Ventilations Tip: ✓
```

5. **Gem automation**

### Eksempel På Notifikation

Du vil modtage beskeder som:

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

## 🔧 Tekniske Detaljer

### Ventilationsanbefaling Logik

1. **Tjek Vinduer**
   - Hvis vinduer åbne → "Valgfrit" (allerede ventilering)

2. **Analyser Indeklima**
   - Fugtighed > max → Problem
   - CO2 > max → Problem
   - VOC > max → Problem

3. **Tjek Vejr** (hvis tilgængeligt)
   - Temperatur < 5°C → "Valgfrit" (for koldt)
   - Fugtighed > max → "Nej" (for fugtigt ude)
   - Ellers → "Ja" (gode forhold)

4. **Anbefaling**
   - Problemer + gode forhold → "Ja"
   - Problemer + dårlige forhold → "Valgfrit" eller "Nej"
   - Ingen problemer → "Nej"

### Cooldown System

Blueprintet bruger `last_notified` attribute:

1. Når notifikation sendes → Python script opdaterer timestamp
2. Næste trigger → Tjek om cooldown periode er gået
3. Cooldown aktiv → Skip notifikation
4. Cooldown udløbet → Send notifikation

---

## ⚙️ Konfiguration

### Vejr Sensor (Vigtigt!)

For bedste ventilationsanbefalinger, konfigurer vejr sensor:

```
1. Gå til Indeklima integration
2. Klik "Configure"
3. Vælg "🌤️ Vejr integration"
4. Vælg din vejr sensor (f.eks. weather.home)
5. Gem
```

Hvis ingen vejr sensor er valgt, vil anbefaling kun baseres på indeklima.

---

## 🐛 Troubleshooting

### Ventilationsanbefaling Viser "unknown"

**Problem:** Sensoren viser "unknown"

**Fix:**
1. Tjek at du har konfigureret mindst ét rum
2. Tjek at rum har fugtigheds- eller CO2 sensorer
3. Genstart integration

### Blueprint Virker Ikke

**Problem:** Automation trigger ikke

**Fix:**
1. Tjek at python_script er enabled
2. Tjek at indeklima_set_last_notified.py er i config/python_scripts/
3. Se logs: Settings → System → Logs (filtrer på "indeklima")

### Last Notified Opdateres Ikke

**Problem:** `last_notified` attribute forbliver tom

**Fix:**
1. Tjek at python_script integration virker: Developer Tools → Services → python_script.indeklima_set_last_notified
2. Test manuelt:
   ```yaml
   service: python_script.indeklima_set_last_notified
   data:
     entity_id: sensor.indeklima_stue_status
   ```

---

## 📊 Nye Sensorer

### Hub Sensor

- `sensor.indeklima_hub_ventilationsanbefaling`
  - **State:** "Ja" / "Nej" / "Valgfrit"
  - **Attributes:**
    - `begrundelse`: Hvorfor denne anbefaling?
    - `rum`: Hvilke rum trænger til udluftning?
    - `ude_temperatur`: Nuværende udendørs temperatur
    - `ude_fugtighed`: Nuværende udendørs fugtighed

### Room Sensor Attributes (Opdateret)

Alle room sensors har nu:
- `last_notified`: ISO 8601 timestamp for sidste notifikation
- Eksempel: `"2025-01-11T14:30:00+00:00"`

---

## ✅ Tjekliste

Efter opdatering:

- [ ] Version 2.1.0 i Settings → Integrations → Indeklima
- [ ] `sensor.indeklima_hub_ventilationsanbefaling` eksisterer
- [ ] `last_notified` attribute på room sensors
- [ ] Python script installeret (hvis bruger blueprint)
- [ ] Blueprint tilgængeligt (hvis bruger det)
- [ ] Vejr sensor konfigureret (anbefalet)

---

## 🎯 Næste Skridt

### v2.2 (Planlagt)
- Automatisk affugter kontrol
- Fan automation baseret på CO2
- Integration med ventilationssystemer
- Service calls til manuel kontrol

---

**Velkommen til Indeklima v2.1.0! 🎉**

Nyd smarte ventilationsanbefalinger! 🌬️