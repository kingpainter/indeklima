# 🏠 Indeklima - Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Version](https://img.shields.io/badge/version-2.3.1-blue.svg)](https://github.com/kingpainter/indeklima)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Avanceret indeklima overvågning for Home Assistant med multi-room support, intelligent severity scoring og ventilationsanbefalinger.

**Version:** 2.3.1 | **Quality Scale:** Silver Tier ⭐️

---

## ✨ Hovedfunktioner

- 🏠 **Multi-room support** - Overvåg flere rum individuelt
- 📊 **Per-room sensorer** - Separate temperatur, fugtighed og CO2 sensorer per rum
- 🌬️ **Ventilationsanbefalinger** - Smart analyse baseret på indeklima og vejr
- 📈 **Trend analyse** - 30-minutters trends for fugtighed, CO2 og severity
- 🪟 **Window/door tracking** - Skelne mellem udvendige vinduer og interne døre
- 🌀 **Luftcirkulation** - Overvåg luftcirkulation mellem rum
- 🎯 **Severity scoring** - Intelligent 0-100 score for indeklima kvalitet
- 🤖 **Automation ready** - Færdige blueprints og direkte sensor triggers

---

## 📦 Installation

### Via HACS (Anbefalet)
1. HACS → Integrations → Custom repositories
2. Tilføj: `https://github.com/kingpainter/indeklima`
3. Download "Indeklima"
4. Genstart Home Assistant

### Manuelt
1. Download [latest release](https://github.com/kingpainter/indeklima/releases)
2. Kopier `custom_components/indeklima` til din HA installation
3. Genstart Home Assistant

---

## ⚙️ Opsætning

1. **Settings** → **Devices & Services** → **Add Integration**
2. Søg efter "Indeklima"
3. Følg wizard:
   - Navngiv integration
   - Tilføj rum (et ad gangen)
   - Vælg sensorer per rum
   - Marker udvendige vinduer/døre
   - Konfigurer grænseværdier (valgfrit)

---

## 📊 Sensorer

### Hub Sensorer (Globale)

| Sensor | Beskrivelse |
|--------|-------------|
| `sensor.indeklima_hub_severity_score` | Samlet indeklima score (0-100) |
| `sensor.indeklima_hub_status` | God/Advarsel/Dårlig |
| `sensor.indeklima_hub_gennemsnitlig_fugtighed` | Gennemsnit alle rum |
| `sensor.indeklima_hub_gennemsnitlig_temperatur` | Gennemsnit alle rum |
| `sensor.indeklima_hub_gennemsnitlig_co2` | Gennemsnit alle rum |
| `sensor.indeklima_hub_luftcirkulation` | God/Moderat/Dårlig |
| `sensor.indeklima_hub_ventilationsanbefaling` | Ja/Nej/Valgfrit |
| `sensor.indeklima_hub_fugtigheds_trend` | Stigende/Faldende/Stabil |
| `sensor.indeklima_hub_co2_trend` | Stigende/Faldende/Stabil |

### Per-Room Sensorer (v2.3+)

Hvert rum får automatisk:

| Sensor | Betingelse | Device Class |
|--------|------------|--------------|
| `sensor.indeklima_[rum]_status` | Altid | - |
| `sensor.indeklima_[rum]_temperatur` | Hvis temp sensorer | `temperature` |
| `sensor.indeklima_[rum]_fugtighed` | Hvis humid sensorer | `humidity` |
| `sensor.indeklima_[rum]_co2` | Hvis CO2 sensorer | `carbon_dioxide` |

**Fordele:**
- ✅ Direkte historik og grafer
- ✅ `trigger: numeric_state` i automations
- ✅ Korrekte enheder og device classes
- ✅ Voice assistant support

---

## 🎨 Dashboard Eksempler

### Simple Room Card
```yaml
type: entities
title: 🛏️ Soveværelse
entities:
  - sensor.indeklima_sovevaerelse_status
  - sensor.indeklima_sovevaerelse_temperatur
  - sensor.indeklima_sovevaerelse_fugtighed
  - sensor.indeklima_sovevaerelse_co2
```

### History Graph
```yaml
type: history-graph
entities:
  - sensor.indeklima_sovevaerelse_temperatur
  - sensor.indeklima_sovevaerelse_fugtighed
  - sensor.indeklima_sovevaerelse_co2
hours_to_show: 24
```

### Apex Charts
```yaml
type: custom:apexcharts-card
graph_span: 24h
series:
  - entity: sensor.indeklima_sovevaerelse_temperatur
    name: Temperatur
  - entity: sensor.indeklima_sovevaerelse_fugtighed
    name: Fugtighed
  - entity: sensor.indeklima_sovevaerelse_co2
    name: CO2
    y_axis_id: co2
```

---

## 🤖 Automation Eksempler

### Høj CO2 Alert
```yaml
automation:
  - alias: "Høj CO2 - Soveværelse"
    trigger:
      - platform: numeric_state
        entity_id: sensor.indeklima_sovevaerelse_co2
        above: 1000
        for:
          minutes: 5
    action:
      - service: notify.mobile_app
        data:
          message: "CO2 er {{ states('sensor.indeklima_sovevaerelse_co2') }} ppm"
```

### Høj Fugtighed + Temperatur
```yaml
automation:
  - alias: "Dårligt indeklima"
    trigger:
      - platform: numeric_state
        entity_id: sensor.indeklima_sovevaerelse_fugtighed
        above: 60
      - platform: numeric_state
        entity_id: sensor.indeklima_sovevaerelse_co2
        above: 1200
    action:
      - service: notify.mobile_app
        data:
          title: "Indeklima advarsel"
          message: |
            Fugtighed: {{ states('sensor.indeklima_sovevaerelse_fugtighed') }}%
            CO2: {{ states('sensor.indeklima_sovevaerelse_co2') }} ppm
```

---

## 🔧 Konfiguration

### Grænseværdier

| Parameter | Sommer | Vinter |
|-----------|--------|--------|
| Max Fugtighed | 60% | 55% |
| Max CO2 | 1000 ppm | 1000 ppm |
| Max VOC | 3.0 mg/m³ | 3.0 mg/m³ |
| Max Formaldehyd | 0.15 mg/m³ | 0.15 mg/m³ |

**Juster:** Settings → Integrations → Indeklima → Configure

### Window/Door Klassifikation

- ✅ **Udvendig** = Fører til udendørs (bruges til ventilation)
- ❌ **Intern** = Mellem rum (bruges til luftcirkulation)

---

## 🆕 Hvad er Nyt?

### v2.3.1 (2025-01-18)
- 🔧 **Encoding fix** - Alle danske tegn håndteres korrekt
- ✅ **Clean constants** - Alle Python konstanter på engelsk
- 📝 **Translations** - Dansk via strings.json/da.json
- 🎯 **No breaking changes** - Direkte upgrade fra v2.3.0

### v2.3.0 (2025-01-13)
- 📊 **Per-room metric sensors** - Separate sensorer per rum
- ✅ **Backward compatible** - Status attributes beholdes
- 📈 **Better automations** - Direkte numeric_state triggers

### v2.2.0 (2025-01-12)
- 🪟 **Window/door tracking** - Indoor/outdoor klassifikation
- 🌬️ **Luftcirkulation sensor** - God/Moderat/Dårlig
- 🎯 **Severity bonus** - 5% reduktion ved god luftcirkulation

### v2.1.0 (2025-01-11)
- 🌬️ **Ventilationsanbefalinger** - Smart analyse med vejr integration
- 📱 **Automation blueprint** - Færdig notifikations-automation

---

## 🔍 Fejlfinding

### Sensorer viser "unknown"
1. Verificer at sensor entities er tilgængelige
2. Tjek logs: Settings → System → Logs (filtrer "indeklima")
3. Genstart Home Assistant

### Per-room sensorer mangler
1. Tjek at rummet HAR sensorer konfigureret
2. Settings → Integrations → Indeklima → [Rum] → Verificer
3. Genstart Home Assistant efter ændringer

### Vinduer/døre status forkert
1. Binary sensors skal bruge "on" = åben, "off" = lukket
2. Developer Tools → States → Verificer sensor state
3. Tjek window/door klassifikation (udvendig vs intern)

---

## 📚 Dokumentation

- [Upgrade Guide v2.3.0](UPGRADE_v2_3_0.md)
- [English Constants Guide](ENGLISH_CONSTANTS.md)
- [HA Compliance](HA_COMPLIANCE.md)
- [Full Changelog](CHANGELOG.md)

---

## 🤝 Bidrag

Bidrag er velkomne via [GitHub](https://github.com/kingpainter/indeklima)

---

## 📄 Licens

MIT License - se [LICENSE](LICENSE)

---

## 📞 Support

- [GitHub Issues](https://github.com/kingpainter/indeklima/issues)
- [GitHub Discussions](https://github.com/kingpainter/indeklima/discussions)

---

**Made with ❤️ by KingPainter** | v2.3.1 | January 2025
