# Changelog - Indeklima v2.4.0

## Version 2.4.0 - Custom Panel & Lovelace Cards

**Release Date:** March 2026  
**Type:** MINOR — New features, backward compatible  
**Previous Version:** 2.3.3

---

## 🆕 What's New

### Custom Sidebar Panel

Indeklima now has a dedicated sidebar panel in Home Assistant — no more navigating to a dashboard to check your climate! The panel is admin-only and available at `/indeklima` in your HA instance.

**Panel features:**
- **Overblik tab** — Severity ring, average temperature/humidity/CO₂/pressure, trends (30 min), open windows
- **Rum tab** — All rooms in a grid with status color-coding, live metrics, severity bar, click a room for detail view
- **Udluftning tab** — Ventilation recommendation with reason chips, outdoor weather stats, air circulation status, open windows list
- Live data via WebSocket — updates automatically every 30 seconds
- Rooms sorted by severity (critical first)
- Climate-themed dark design: deep teals, organic gradients, breath animations

### Custom Lovelace Cards

Two new cards available in the card picker:

#### `custom:indeklima-room-card`
Compact room card for any dashboard.
- Shows temperature, humidity, CO₂ (only sensors that exist for the room)
- Color-coded border and background based on status (good/warning/critical)
- Severity progress bar
- Window/door open badges
- Pulse animation for warning/critical status

Config:
```yaml
type: custom:indeklima-room-card
room: "Stue"        # required — must match room name in integration
title: "Stuen"      # optional override
show_pressure: true # optional, default false
```

#### `custom:indeklima-hub-card`
Full house overview card.
- Severity ring with score
- All rooms as status pills (color-coded)
- Ventilation recommendation
- Air circulation status
- Trends for humidity, CO₂, severity
- Compact mode option

Config:
```yaml
type: custom:indeklima-hub-card
title: "Indeklima Overblik"  # optional
compact: false               # optional — hides averages, circulation, trends
```

### WebSocket API

New backend WebSocket commands for the panel and cards:
- `indeklima/get_climate_data` — Full house data including all rooms, averages, trends, ventilation
- `indeklima/get_room_data` — Detailed data for a specific room (by room name)

---

## 📁 New Files

```
custom_components/indeklima/
├── panel.py              # Panel + Lovelace resource registration
├── websocket.py          # WebSocket API (2 commands)
└── frontend/
    ├── indeklima-panel.js   # Sidebar panel (vanilla JS web component)
    └── indeklima-cards.js   # Lovelace cards (2 cards)
```

---

## 🔄 Changed Files

| File | Change |
|------|--------|
| `__init__.py` | + panel registration, + websocket registration, + unload cleanup |
| `const.py` | Version bump to 2.4.0 |
| `manifest.json` | Version bump to 2.4.0 |

---

## ✅ Backward Compatibility

- All existing sensors and entities are unchanged
- Dashboard YAML cards (Mushroom etc.) continue to work exactly as before
- Custom panel and cards are purely additive
- No breaking changes to config flow or options

---

## 🛠️ Installation

1. Copy all files to `custom_components/indeklima/`
2. Create the `frontend/` subfolder and copy the two JS files there
3. Reload the integration (Settings → Devices & Services → Indeklima → Reload)
4. The panel appears in your sidebar automatically
5. Cards are available in the Lovelace card picker

---

## 🎯 Quality Tier

Still **Silver Tier** — Gold Tier features (diagnostics, repair flow, unit tests) are planned for a future release.

---

## 🐛 Bug Fixes

None — this is a pure feature release.
