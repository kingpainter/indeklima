# Blueprint Migration Guide: v2.2.0 → v2.3.1

## 🔴 CRITICAL: Old Blueprint DOES NOT WORK with v2.3.1!

The `room_notification.yaml` blueprint uses **Danish** status values internally, but v2.3.1 uses **English** constants.

---

## ❌ What's Broken in Old Blueprint

### Issue 1: Trigger States (Lines 78-79)
```yaml
# OLD (BROKEN)
to:
  - "Advarsel"  # ❌ v2.3.1 uses "warning"
  - "Dårlig"    # ❌ v2.3.1 uses "critical"
```

### Issue 2: Threshold Selector (Lines 29-36)
```yaml
# OLD (BROKEN)
options:
  - label: "Advarsel"
    value: "Advarsel"  # ❌ Wrong
  - label: "Dårlig"
    value: "Dårlig"    # ❌ Wrong
```

### Issue 3: Template Conditions (Lines 92-95)
```yaml
# OLD (BROKEN)
{% if threshold == 'Dårlig' %}
  {{ current == 'Dårlig' }}
{% else %}
  {{ current in ['Advarsel', 'Dårlig'] }}
```

---

## ✅ What's Fixed in New Blueprint

### Fix 1: English Constants Internally
```yaml
# NEW (WORKS)
to:
  - "warning"    # ✅ English constant
  - "critical"   # ✅ English constant
```

### Fix 2: Correct Selector Values
```yaml
# NEW (WORKS)
options:
  - label: "Advarsel"      # Danish label (UI)
    value: "warning"       # English value (internal)
  - label: "Dårlig"
    value: "critical"
```

### Fix 3: Fixed Templates
```yaml
# NEW (WORKS)
{% set threshold = !input severity_threshold %}  # Now "warning" or "critical"
{% set current = trigger.to_state.state %}
{% if threshold == 'critical' %}
  {{ current == 'critical' }}
{% else %}
  {{ current in ['warning', 'critical'] }}
{% endif %}
```

### Fix 4: Status Translation for Notifications
```yaml
# NEW - Translates English → Danish for user-facing message
status_dansk: >
  {% if trigger.to_state.state == 'critical' %}Dårlig
  {% elif trigger.to_state.state == 'warning' %}Advarsel
  {% else %}{{ trigger.to_state.state }}{% endif %}
```

---

## 📦 Installation

### Step 1: Remove Old Blueprint

1. Go to: **Settings** → **Automations & Scenes** → **Blueprints**
2. Find "Indeklima - Rum Notifikation"
3. Delete any automations using it (they won't work anyway)
4. Delete the old blueprint

### Step 2: Install New Blueprint

**Manual Installation:**
```bash
# Copy to Home Assistant
blueprints/automation/indeklima/room_notification.yaml
```

**Location:**
```
config/
└── blueprints/
    └── automation/
        └── indeklima/
            └── room_notification.yaml
```

### Step 3: Reload Blueprints

1. Go to: **Settings** → **Automations & Scenes** → **Blueprints**
2. Click **⋮** (top right) → **Reload blueprints**
3. New blueprint should appear with "(v2.3.1)" in title

### Step 4: Create New Automations

1. Click **+ Create Automation**
2. Select "Indeklima - Rum Notifikation (v2.3.1)"
3. Configure:
   - **Rum Sensor:** `sensor.indeklima_[rum]_status`
   - **Notifikations Service:** Your notify service
   - **Alvorligheds Tærskel:** Advarsel eller Dårlig
   - **Cooldown:** 2 hours (default)
   - **Tid:** 09:00 - 21:00 (customize)

---

## 🔍 How to Verify It Works

### Test 1: Check Sensor States
```yaml
# Developer Tools → States
sensor.indeklima_stue_status: "warning"    # ✅ English
sensor.indeklima_koekken_status: "good"    # ✅ English
```

### Test 2: Test Automation
1. Manually trigger bad indoor climate
2. Wait 5 minutes
3. Check if notification arrives
4. Verify cooldown works

### Test 3: Check Notification Message
Should show Danish text:
```
Status: Advarsel        ← Translated correctly
🌡️ Fugtighed: 62%
💨 CO2: 1200 ppm
```

---

## 📊 Comparison Table

| Feature | Old Blueprint | New Blueprint v2.3.1 |
|---------|--------------|---------------------|
| Status values | Danish | English (translated) |
| Works with v2.3.1 | ❌ No | ✅ Yes |
| UI labels | Danish | Danish |
| Notifications | Danish | Danish |
| Template logic | ❌ Broken | ✅ Fixed |
| Threshold selector | ❌ Wrong values | ✅ Correct values |
| Backward compatible | v2.2.0 only | v2.3.1+ |

---

## 🚨 Common Issues

### Issue: Automation doesn't trigger
**Cause:** Still using old blueprint with Danish values  
**Fix:** Delete automation, use new blueprint

### Issue: Selector shows English values
**Cause:** Blueprint cache  
**Fix:** Reload blueprints (Step 3 above)

### Issue: Gets notification every 5 minutes
**Cause:** Cooldown not working  
**Fix:** Check `last_notified` attribute exists in sensor

---

## 📝 Technical Notes

### Status Value Mapping

| Internal (English) | UI Display (Danish) | User Sees |
|-------------------|-------------------|-----------|
| `good` | God | ✅ God |
| `warning` | Advarsel | ⚠️ Advarsel |
| `critical` | Dårlig | 🔴 Dårlig |

### Why the Change?

v2.3.1 follows **Home Assistant best practices**:
- Code uses English constants
- Translations via `strings.json` / `da.json`
- Makes integration international-ready
- Cleaner code, easier maintenance

### Ventilation Recommendations

Same issue - now uses English internally:
```yaml
# v2.3.1
sensor.indeklima_hub_ventilationsanbefaling: "yes"  # English
# Displays as "Ja" in Danish UI
```

---

## ✅ Migration Checklist

- [ ] Backup existing automations (screenshot settings)
- [ ] Delete old blueprint
- [ ] Install new blueprint (v2.3.1)
- [ ] Reload blueprints
- [ ] Recreate automations using new blueprint
- [ ] Test one room first
- [ ] Verify notifications work
- [ ] Verify cooldown works
- [ ] Deploy to all rooms

---

## 🔗 Related Files

- `room_notification_v2.3.1.yaml` - New blueprint
- `ENGLISH_CONSTANTS.md` - Why we switched to English
- `CHANGELOG_v2_3_1.md` - Full changelog

---

**This migration is REQUIRED for v2.3.1 compatibility!** ✅
