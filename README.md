# README.md - Insert this section after line 14 (after "Quality Scale: Silver Tier")

## ✨ Features

### ✅ Implementeret (v2.2.0)
- 🪟 **Indoor/Outdoor Window Tracking** - Skelne mellem udvendige vinduer og interne døre
- 🌬️ **Luftcirkulation Sensor** - Overvåg luftcirkulation mellem rum
- 🎯 **Severity Bonus** - Reduktion i score ved god luftcirkulation
- 🌡️ **Multi-room overvågning**: Overvåg fugtighed, temperatur, CO2, VOC og formaldehyd i flere rum
- 📊 **Intelligent severity scoring**: Automatisk beregning af indeklima kvalitet (0-100)
- 🔄 **Flere sensorer per rum**: Brug flere sensorer af samme type i ét rum - gennemsnittet beregnes automatisk
- 📈 **Trend-analyse**: 30-minutters trends for fugtighed, CO2 og severity
- 🪟 **Window tracking**: Hold styr på åbne vinduer (eksterne) og døre (interne)
- 🏠 **Per-rum konfiguration**: Tilføj, rediger og slet rum individuelt
- ⚙️ **Fuld options flow**: Administrer alt efter installation
- 💨 **Dehumidifier support**: Forbered til fremtidig automation
- 🌀 **Fan/Ventilator support**: Forbered til fremtidig automation
- 🌞 **Sæsonbaserede grænser**: Forskellige grænser for sommer og vinter
- 🏷️ **Device organization**: Moderne hub + room device struktur
- 🌐 **Multi-language**: Dansk og engelsk
- 🌬️ **Ventilationsanbefalinger**: Smart sensor der analyserer indeklima og vejr (v2.1)
- 📱 **Automation Blueprint**: Færdig notifikations-automation med cooldown (v2.1)

### 🚧 Planlagt (v2.3+)
- 📲 Automatisk device kontrol (affugtere, fans)
- 🎯 Diagnostics platform
- 🔗 Integration med ventilationssystemer

---

# And update the Sensors section (around line 83):

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
- `sensor.indeklima_hub_aabne_vinduer` - Antal åbne EKSTERNE vinduer
- `sensor.indeklima_hub_luftcirkulation` - God/Moderat/Dårlig (NYT i v2.2!)
- `sensor.indeklima_hub_fugtigheds_trend` - Stigende/Faldende/Stabil
- `sensor.indeklima_hub_co2_trend`
- `sensor.indeklima_hub_severity_trend`
- `sensor.indeklima_hub_ventilationsanbefaling` - Ja/Nej/Valgfrit (v2.1)

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
vinduer_udendørs_åbne: 0          # NYT i v2.2!
døre_interne_åbne: 1              # NYT i v2.2!
luftcirkulation_bonus: true       # NYT i v2.2!
last_notified: "2025-01-11T14:30:00+00:00"
```

---

# And add this new section after the Ventilationsanbefalinger section:

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

# Update the Changelog section at the bottom:

## 📝 Changelog

Se [CHANGELOG.md](CHANGELOG.md) for fuld version historik.

### v2.2.0 (2025-01-12)
- 🪟 Indoor/Outdoor vindue klassifikation
- 🌬️ Luftcirkulation sensor
- 🎯 Severity bonus for god luftcirkulation
- 📊 Forbedrede room attributes

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