# Changelog - Indeklima v2.5.1

## Version 2.5.1 - Mold Risk Visible on All Cards

**Release Date:** May 2026
**Type:** PATCH — Frontend only, backward compatible
**Previous Version:** 2.5.0

---

## 🆕 What's New

### Mold Risk Shown on All Lovelace Cards

Mold risk was already calculated by the backend and exposed via WebSocket, but was only partially visible in the frontend — hidden when "low" and shown as a small emoji icon only when elevated. This release makes mold risk always visible on all cards with consistent color coding.

---

## 🔄 Changes per Card

### `indeklima-room-card`

**Before:** Mold chip only shown in footer when `mold_risk !== "low"` — invisible at low risk.

**After:** Mold chip always shown with full color coding:
- 🟢 Green — Lav skimmelrisiko
- 🟡 Orange — Moderat skimmelrisiko
- 🟠 Orange-red — Høj skimmelrisiko
- 🔴 Red + blink — Kritisk skimmelrisiko

---

### `indeklima-hub-card`

**Before:**
- No global mold section
- Per-room: only a small emoji icon shown when `mold_risk !== "low"`

**After:**
- New "Skimmelrisiko" section showing global house average (from `d.mold_risk`) with icon, label, and sub-text "Husgennemsnit baseret på fugt og temperatur"
- Per-room: mold always shown as colored badge (icon + full label) on every room row

---

### `indeklima-tablet-card`

**Before:**
- No global mold in column 1
- Per-room in column 2: only icon + label shown when `mold_risk !== "low"`

**After:**
- New "Skimmelrisiko" block in column 1 after air circulation
- Per-room in column 2: mold always shown on every room row

---

### `indeklima-room-detail-card`

No changes — this card already had a full mold section with description text. ✅

---

## 📁 Changed Files

| File | Change |
|---|---|
| `frontend/indeklima-cards.js` | Mold always visible on all cards, version `2.5.1` |

---

## ✅ Backward Compatibility

Frontend-only change. No changes to backend, sensors, WebSocket API, or configuration. All existing automations and dashboards work exactly as before.
