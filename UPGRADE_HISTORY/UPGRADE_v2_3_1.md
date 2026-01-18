# Upgrade Guide: v2.2.0 → v2.3.1

## 🎉 What's New in v2.3.1?

### ✅ Critical Fixes

1. **🔧 Complete Encoding Cleanup**
   - All Python code uses ONLY English + ASCII
   - All Danish text moved to translation files (strings.json, da.json)
   - Fixed æ, ø, å character handling in all files
   - Removed emojis from Python code
   - Clean UTF-8 encoding throughout

2. **✅ English Constants System**
   - `STATUS_GOOD = "good"` (was "God")
   - `STATUS_WARNING = "warning"` (was "Advarsel")
   - `STATUS_CRITICAL = "critical"` (was "Dårlig")
   - All translations via strings.json/da.json

3. **📊 Per-Room Metric Sensors** (from v2.3.0)
   - Separate sensors for temperature, humidity, and CO2 per room
   - Better device classes for correct display in HA
   - Automatic average if multiple sensors of same type
   - Attributes show number of sensors used

4. **✅ Backward Compatible**
   - Status sensor attributes preserved (humidity, temperature, co2, etc.)
   - Existing dashboards work without changes
   - No breaking changes!

---

## 📦 Installation

### From v2.2.0 or v2.3.0 (Recommended Path)

This is a **fully backward-compatible** update! No breaking changes.

#### Step 1: Update Files
```
1. Copy all updated files to custom_components/indeklima/
2. Check that version is 2.3.1 in:
   - manifest.json
   - const.py
```

#### Step 2: Restart Home Assistant
```
Settings → System → Restart
```

#### Step 3: Check New Sensors

After restart you'll see new sensors for each room:

**If Living Room has:**
- 2× temperature sensors
- 2× humidity sensors  
- 1× CO2 sensor

**You'll get:**
- ✅ `sensor.indeklima_living_room_temperature` (average of 2 sensors)
- ✅ `sensor.indeklima_living_room_humidity` (average of 2 sensors)
- ✅ `sensor.indeklima_living_room_co2` (from 1 sensor)
- ✅ `sensor.indeklima_living_room_status` (as before, with attributes)

---

## 🔧 What Changed from v2.3.0 → v2.3.1

### 1. English Constants

**BEFORE (v2.3.0 - BROKEN):**
```python
# const.py
STATUS_GOOD = "God"        # ❌ Danish in code
STATUS_WARNING = "Advarsel"
STATUS_CRITICAL = "Dårlig"

# sensor.py
data["status"] = "God"     # ❌ Hardcoded Danish
```

**AFTER (v2.3.1 - FIXED):**
```python
# const.py
STATUS_GOOD = "good"       # ✅ English constant
STATUS_WARNING = "warning"
STATUS_CRITICAL = "critical"

# sensor.py
data["status"] = STATUS_GOOD  # ✅ Uses constant

# strings.json (English)
"state": {
  "good": "Good",
  "warning": "Warning",
  "critical": "Critical"
}

# da.json (Danish translation)
"state": {
  "good": "God",
  "warning": "Advarsel",
  "critical": "Dårlig"
}
```

### 2. Fixed Character Encoding

**All Danish characters properly handled:**
- `normalize_room_id()` converts æ→ae, ø→oe, å→aa
- No double-encoding issues
- Clean UTF-8 throughout

### 3. Blueprint Compatibility

**CRITICAL:** Old blueprint does NOT work with v2.3.1!

See [BLUEPRINT_MIGRATION.md](BLUEPRINT_MIGRATION.md) for updated blueprint.

---

## 📊 New Sensors (from v2.3.0)

### Room Temperature Sensor

**Sensor:** `sensor.indeklima_[room]_temperature`

**Properties:**
- **State:** Average of all temp sensors in room (°C)
- **Unit:** °C
- **Device Class:** `temperature`
- **Icon:** `mdi:thermometer`

**Attributes:**
```yaml
sensors_used: 2  # Number of sensors used for average
```

**Example:**
```yaml
sensor.indeklima_living_room_temperature:
  state: 21.3
  unit_of_measurement: "°C"
  device_class: temperature
  attributes:
    sensors_used: 2
```

### Room Humidity Sensor

**Sensor:** `sensor.indeklima_[room]_humidity`

**Properties:**
- **State:** Average of all humidity sensors in room (%)
- **Unit:** %
- **Device Class:** `humidity`
- **Icon:** `mdi:water-percent`

**Attributes:**
```yaml
sensors_used: 2
```

### Room CO2 Sensor

**Sensor:** `sensor.indeklima_[room]_co2`

**Properties:**
- **State:** Average of all CO2 sensors in room (ppm)
- **Unit:** ppm
- **Device Class:** `carbon_dioxide`
- **Icon:** `mdi:molecule-co2`

**Attributes:**
```yaml
sensors_used: 1
```

---

## 🔄 Backward Compatibility

### Status Sensor Attributes Preserved

**BEFORE v2.3.0:**
```yaml
sensor.indeklima_living_room_status:
  state: "warning"
  attributes:
    humidity: 55.5
    temperature: 21.3
    co2: 850
```

**AFTER v2.3.1:**
```yaml
# Status sensor (unchanged)
sensor.indeklima_living_room_status:
  state: "warning"          # ✅ English constant (displays as "Advarsel" in Danish UI)
  attributes:
    humidity: 55.5          # ✅ Still here!
    temperature: 21.3       # ✅ Still here!
    co2: 850                # ✅ Still here!
    humidity_sensors_count: 2
    temperature_sensors_count: 2
    co2_sensors_count: 1

# NEW individual sensors
sensor.indeklima_living_room_temperature:
  state: 21.3
  unit_of_measurement: "°C"
  device_class: temperature
  attributes:
    sensors_used: 2

sensor.indeklima_living_room_humidity:
  state: 55.5
  unit_of_measurement: "%"
  device_class: humidity
  attributes:
    sensors_used: 2

sensor.indeklima_living_room_co2:
  state: 850
  unit_of_measurement: "ppm"
  device_class: carbon_dioxide
  attributes:
    sensors_used: 1
```

### Existing Dashboards Still Work

**Old dashboard cards:**
```yaml
# This still works! ✅
type: custom:mushroom-entity-card
entity: sensor.indeklima_living_room_status
secondary_info: |
  💧 {{ state_attr('sensor.indeklima_living_room_status', 'humidity') }}%
  🌡️ {{ state_attr('sensor.indeklima_living_room_status', 'temperature') }}°C
```

**New dashboard cards (better):**
```yaml
# Now you can also use separate sensors! 🎉
type: entities
entities:
  - sensor.indeklima_living_room_status
  - sensor.indeklima_living_room_temperature
  - sensor.indeklima_living_room_humidity
  - sensor.indeklima_living_room_co2
```

---

## 🎨 Dashboard Examples

### Simple Entity Card

```yaml
type: entities
title: 🏠 Living Room Climate
entities:
  - entity: sensor.indeklima_living_room_status
    name: Status
  - entity: sensor.indeklima_living_room_temperature
    name: Temperature
  - entity: sensor.indeklima_living_room_humidity
    name: Humidity
  - entity: sensor.indeklima_living_room_co2
    name: CO2
```

### Mushroom Cards Grid

```yaml
type: grid
columns: 2
square: false
cards:
  - type: custom:mushroom-entity-card
    entity: sensor.indeklima_living_room_temperature
    name: Temperature
    icon: mdi:thermometer
    
  - type: custom:mushroom-entity-card
    entity: sensor.indeklima_living_room_humidity
    name: Humidity
    icon: mdi:water-percent
    
  - type: custom:mushroom-entity-card
    entity: sensor.indeklima_living_room_co2
    name: CO2
    icon: mdi:molecule-co2
```

### History Graph

```yaml
type: history-graph
title: 📈 Living Room - Last 24 hours
entities:
  - entity: sensor.indeklima_living_room_temperature
    name: Temperature
  - entity: sensor.indeklima_living_room_humidity
    name: Humidity
  - entity: sensor.indeklima_living_room_co2
    name: CO2
hours_to_show: 24
```

---

## 🤖 Automation Examples

### BEFORE v2.3.0 (Template-based)

```yaml
automation:
  - alias: "High CO2 - Living Room"
    trigger:
      - platform: template
        value_template: >
          {{ state_attr('sensor.indeklima_living_room_status', 'co2') | float(0) > 1000 }}
    
    action:
      - service: notify.mobile_app
        data:
          message: "Living room has high CO2!"
```

### AFTER v2.3.1 (Direct sensor - Better!)

```yaml
automation:
  - alias: "High CO2 - Living Room"
    trigger:
      - platform: numeric_state
        entity_id: sensor.indeklima_living_room_co2
        above: 1000
        for:
          minutes: 5
    
    action:
      - service: notify.mobile_app
        data:
          title: "🌬️ High CO2!"
          message: |
            Living room: {{ states('sensor.indeklima_living_room_co2') }} ppm
```

### Multi-Condition Automation

```yaml
automation:
  - alias: "Bad Indoor Climate - Living Room"
    trigger:
      # High humidity OR high CO2
      - platform: numeric_state
        entity_id: sensor.indeklima_living_room_humidity
        above: 60
      
      - platform: numeric_state
        entity_id: sensor.indeklima_living_room_co2
        above: 1200
    
    condition:
      # Only between 7am-10pm
      - condition: time
        after: "07:00:00"
        before: "22:00:00"
    
    action:
      - service: notify.family
        data:
          title: "🏠 Indoor Climate Warning"
          message: |
            Living room needs ventilation!
            
            Humidity: {{ states('sensor.indeklima_living_room_humidity') }}%
            CO2: {{ states('sensor.indeklima_living_room_co2') }} ppm
            Temperature: {{ states('sensor.indeklima_living_room_temperature') }}°C
```

---

## 🔧 Technical Details

### Sensor Naming Convention

**Pattern:** `sensor.indeklima_[room_id]_[metric]`

**Examples:**
- `sensor.indeklima_living_room_temperature`
- `sensor.indeklima_bedroom_humidity`
- `sensor.indeklima_kitchen_co2`

### Room ID Normalization

Room ID is normalized version of room name:
- Spaces → `_`
- `æ` → `ae`
- `ø` → `oe`
- `å` → `aa`
- Lowercase

**Examples:**
- "Living Room" → `living_room`
- "Bedroom" → `bedroom`
- "Kitchen" → `kitchen`
- "Bathroom" → `bathroom`

### Device Class Benefits

With correct device classes you get:

1. **Automatic Units** - HA shows °C, %, ppm automatically
2. **Correct Icon** - Based on device class
3. **Better Graphs** - HA knows how to visualize data
4. **Voice Assistant** - "Alexa, what's the temperature in the living room?"
5. **Statistics** - Automatic long-term statistics

---

## 🛠️ Troubleshooting

### Problem: I don't see the new sensors

**Solution:**
1. Check that room HAS sensors configured
2. Go to Settings → Integrations → Indeklima
3. Click on room → Check sensor configuration
4. Restart Home Assistant

### Problem: Sensors show "unknown"

**Solution:**
1. Check that underlying sensors work
2. Developer Tools → States → Find your sensors
3. Verify they return numeric values
4. See logs: Settings → System → Logs (filter on "indeklima")

### Problem: Duplicate devices after upgrade

**Solution (v2.3.0 encoding issue):**
1. This was an encoding bug in v2.3.0
2. v2.3.1 fixes this completely
3. If you have duplicates from v2.3.0:
   - Remove integration completely
   - Restart HA
   - Re-add integration with v2.3.1

### Problem: Blueprint doesn't work

**Solution:**
1. Old blueprint uses Danish values
2. Download new blueprint for v2.3.1
3. See [BLUEPRINT_MIGRATION.md](BLUEPRINT_MIGRATION.md)

---

## ✅ Checklist

After upgrade:

- [ ] Version 2.3.1 in Settings → Integrations → Indeklima
- [ ] New sensors appear per room (temperature, humidity, CO2)
- [ ] Status sensor attributes still available
- [ ] Existing dashboards work
- [ ] Correct device classes (check Developer Tools → States)
- [ ] Test automations if you created new ones
- [ ] Update blueprints if using notifications

---

## 🎯 Next Steps

### v2.4.0 (Planned - Q1 2025)
- VOC and Formaldehyde per-room sensors (if demand)
- Improved attributes with individual sensor values
- Better debugging tools
- Diagnostics platform (Gold tier)

### v3.0.0 (Vision - Q2-Q4 2025)
- Machine learning patterns
- Predictive maintenance
- Energy optimization
- Multi-home support

---

## 📚 Related Guides

- [README.md](README.md) - Full documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [HA_COMPLIANCE.md](HA_COMPLIANCE.md) - Home Assistant compliance
- [BLUEPRINT_MIGRATION.md](BLUEPRINT_MIGRATION.md) - Blueprint upgrade guide
- [ENGLISH_CONSTANTS.md](ENGLISH_CONSTANTS.md) - Why English constants

---

**Welcome to Indeklima v2.3.1! 🎉**

Enjoy better sensors, cleaner code, and easier automations! 📊
