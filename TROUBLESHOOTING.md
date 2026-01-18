# 🔧 Indeklima Troubleshooting Guide

Complete troubleshooting guide for Indeklima v2.3.2

---

## 📋 Quick Diagnostic Checklist

Before diving into specific issues, run through this quick checklist:

- [ ] Integration version is v2.3.1 or v2.3.2 (check Settings → Integrations → Indeklima)
- [ ] Home Assistant is up to date (check Settings → System → Updates)
- [ ] All underlying sensors are working (check Developer Tools → States)
- [ ] No errors in logs (Settings → System → Logs, filter "indeklima")
- [ ] Integration has been restarted after configuration changes

---

## 🔍 Common Issues & Solutions

### 1. Sensors Show "Unknown" or "Unavailable"

**Symptom:** Indeklima sensors display "unknown" or "unavailable"

**Diagnostic Steps:**

1. **Check underlying sensors:**
   ```
   Developer Tools → States
   Search for your sensor (e.g., sensor.living_room_humidity)
   ```
   
   ✅ **Good:** Shows numeric value (e.g., "55.2")
   ❌ **Bad:** Shows "unknown" or "unavailable"

2. **Verify sensor returns numbers:**
   ```
   Click on sensor in States view
   Check "State" value
   ```
   
   ✅ **Good:** `55.2` or `1234`
   ❌ **Bad:** `high`, `normal`, `error`

3. **Check integration logs:**
   ```
   Settings → System → Logs
   Filter: "indeklima"
   Look for: ValueError, TypeError, AttributeError
   ```

**Solutions:**

**If underlying sensor is unavailable:**
- Fix the underlying sensor first
- Check device battery/connection
- Verify sensor integration is working

**If sensor returns non-numeric value:**
- Some sensors return text like "high" or "normal"
- Create a template sensor to convert:
  
  ```yaml
  # configuration.yaml
  template:
    - sensor:
        - name: "Living Room Humidity Numeric"
          state: >
            {% set state = states('sensor.living_room_humidity_original') %}
            {% if state == 'low' %}30
            {% elif state == 'normal' %}50
            {% elif state == 'high' %}70
            {% else %}{{ state }}{% endif %}
          unit_of_measurement: "%"
          device_class: humidity
  ```

**If error in logs says "could not convert string to float":**
- Sensor is returning text instead of numbers
- Use template sensor (above) to fix

**Force integration update:**
```
Settings → Integrations → Indeklima → 3 dots → Reload
Wait 5 minutes for coordinator to update
```

---

### 2. Window/Door Status Incorrect

**Symptom:** Windows show closed when open (or vice versa)

**Diagnostic Steps:**

1. **Check sensor state:**
   ```
   Developer Tools → States
   Find: binary_sensor.living_room_window
   
   ✅ Correct:
   - State: "on" when window is OPEN
   - State: "off" when window is CLOSED
   
   ❌ Incorrect:
   - State: "off" when window is OPEN
   - State: "on" when window is CLOSED
   - State: "open" or "closed" (text instead of on/off)
   ```

2. **Verify sensor type:**
   - Must be **binary_sensor** domain
   - Must use **on/off** states (not open/closed text)

**Solutions:**

**For reversed sensors (off=open, on=closed):**

Create a reversed template binary sensor:

```yaml
# configuration.yaml
template:
  - binary_sensor:
      - name: "Living Room Window Fixed"
        state: >
          {{ is_state('binary_sensor.living_room_window_original', 'off') }}
        device_class: window
```

**For text-based sensors (open/closed as text):**

Convert to proper binary sensor:

```yaml
# configuration.yaml
template:
  - binary_sensor:
      - name: "Living Room Window Binary"
        state: >
          {{ is_state('sensor.living_room_window_text', 'open') }}
        device_class: window
```

**Then update Indeklima configuration:**
1. Settings → Integrations → Indeklima → Configure
2. Manage rooms → Edit room
3. Window/Door sensors → Select the "Fixed" sensor instead
4. Save and reload integration

---

### 3. Air Circulation Always "Poor"

**Symptom:** Air circulation shows "Poor" even with doors open

**Diagnostic Steps:**

1. **Check door classification:**
   ```
   Settings → Integrations → Indeklima → Configure
   Manage rooms → Edit each room with doors
   Window/Door configuration
   ```
   
   **Internal doors should NOT be checked (no ✓):**
   - Bathroom door → ❌ (not outdoor)
   - Bedroom door → ❌ (not outdoor)
   - Closet door → ❌ (not outdoor)
   
   **Only outdoor windows/doors should be checked (✓):**
   - Living room window → ✅ (outdoor)
   - Balcony door → ✅ (outdoor)

2. **Verify door sensors work:**
   ```
   Developer Tools → States
   Find each door sensor
   Open door physically
   Verify state changes to "on"
   ```

3. **Check air circulation sensor attributes:**
   ```
   Developer Tools → States
   Find: sensor.indeklima_hub_air_circulation
   Check attributes:
     internal_doors_open: 0  ← Should be > 0 if doors are open
     rooms_with_open_doors: "None"  ← Should list rooms
   ```

**Solutions:**

**Fix door classification:**
1. Review every room's door/window configuration
2. Mark ONLY outdoor openings as "outdoor" (✓)
3. Leave ALL internal doors unmarked (❌)
4. Save changes
5. Reload integration

**Expected behavior:**
- 0 internal doors open = `poor` 🚪
- 1-2 internal doors open = `moderate` 🌀
- 3+ internal doors open = `good` 🌬️

**Example correct setup:**
```
Living Room:
  - Window → ✓ Outdoor
  - Balcony door → ✓ Outdoor
  - Door to hallway → ❌ Internal

Bathroom:
  - Window → ✓ Outdoor
  - Door → ❌ Internal

Bedroom:
  - Window → ✓ Outdoor
  - Door to hallway → ❌ Internal
  - Door to walk-in → ❌ Internal
```

---

### 4. Ventilation Recommendation Stuck on "No"

**Symptom:** Ventilation recommendation always shows "No" or "unknown"

**Diagnostic Steps:**

1. **Check if ANY room has sensors:**
   ```
   Settings → Integrations → Indeklima → Configure
   Manage rooms → Check each room
   
   At least ONE room needs:
   - Humidity sensors, OR
   - CO2 sensors, OR
   - VOC sensors
   ```

2. **Verify thresholds are triggerable:**
   ```
   Settings → Integrations → Indeklima → Configure
   Thresholds
   
   Check values vs. actual sensor readings:
   - Max humidity summer: 60% (default)
   - Max humidity winter: 55% (default)
   - Max CO2: 1000 ppm (default)
   ```
   
   If your humidity is always below threshold, you'll never get "Yes"

3. **Check weather integration:**
   ```
   Settings → Integrations → Indeklima → Configure
   Weather Integration
   
   If no weather entity selected:
   - Recommendations are basic
   - Won't consider outdoor conditions
   ```

4. **Check sensor attributes for reason:**
   ```
   Developer Tools → States
   Find: sensor.indeklima_hub_ventilation_recommendation
   Attributes → "reason"
   
   Examples:
   - "Indeklima er OK" → Nothing wrong, no need to ventilate
   - "For fugtigt ude" → Outdoor humidity too high
   - "For koldt ude" → Outdoor temperature too low
   ```

**Solutions:**

**Add sensors to rooms:**
1. At least one room needs climate sensors
2. Humidity or CO2 sensors work best
3. Edit room → Add sensors → Save

**Adjust thresholds if too strict:**
1. Settings → Configure → Thresholds
2. Lower max humidity (e.g., 60 → 55) to trigger easier
3. Lower max CO2 (e.g., 1000 → 800) for stricter monitoring

**Configure weather entity:**
1. Settings → Configure → Weather Integration
2. Select your weather entity (e.g., `weather.home`)
3. Save

**Test manually:**
1. Temporarily increase humidity in a room (boil water)
2. Wait 5 minutes
3. Check if recommendation changes to "Yes"

**Expected logic:**
```
IF indoor humidity/CO2 is high:
  AND outdoor conditions are good:
    → "yes" (ventilate now)
  AND outdoor conditions are bad:
    → "no" (wait for better weather)
ELSE:
  → "no" (indoor climate is OK)
```

---

### 5. New Room Not Appearing

**Symptom:** Added new room but sensors don't show up

**Diagnostic Steps:**

1. **Check if restart was done:**
   - New rooms REQUIRE Home Assistant restart
   - Settings → System → Restart

2. **Verify room in device registry:**
   ```
   Settings → Devices & Services → Devices
   Search: "Indeklima"
   Look for: "Indeklima [Your Room Name]"
   ```

3. **Check if room has any sensors:**
   - Rooms with NO sensors only get status sensor
   - Add at least one sensor type to get metric sensors

**Solutions:**

**Restart Home Assistant:**
```
Settings → System → Restart
Wait 2-3 minutes
Check Devices again
```

**Add sensors to room:**
```
Settings → Integrations → Indeklima → Configure
Manage rooms → Edit [Room Name]
Add at least:
- Temperature sensors, OR
- Humidity sensors, OR
- CO2 sensors
Save → Restart HA
```

**Check for errors:**
```
Settings → System → Logs
Filter: "indeklima"
Look for: "Failed to setup", "Error", room name
```

**Verify room name characters:**
- Avoid special characters (except æ, ø, å)
- Keep names simple
- Examples: "Living Room", "Bedroom 1", "Køkken"

---

### 6. Automations Not Triggering

**Symptom:** Blueprint automation created but no notifications

**Diagnostic Steps:**

1. **Verify automation is enabled:**
   ```
   Settings → Automations & Scenes
   Find your automation
   Check: No warning icons
   Toggle should be ON (blue)
   ```

2. **Check automation configuration:**
   ```
   Edit automation
   Verify:
   - Room Sensor: Correct sensor selected
   - Notification Service: Valid service (e.g., notify.mobile_app_phone)
   - Time window: Current time is within range
   - Severity threshold: Matches current room status
   ```

3. **Check cooldown:**
   ```
   Developer Tools → States
   Find: sensor.indeklima_[room]_status
   Attributes → last_notified
   
   If recently notified:
   - Cooldown prevents new notification
   - Default: 2 hours between notifications
   ```

4. **Review automation traces:**
   ```
   Automation → Your automation → Traces tab
   See exactly what happened:
   - Did trigger fire?
   - Did conditions pass?
   - What failed?
   ```

**Solutions:**

**Enable automation:**
```
Settings → Automations & Scenes
Find automation
Toggle ON
```

**Fix configuration issues:**

**Wrong sensor:**
```
Edit automation
Room Sensor field
Should be: sensor.indeklima_[room_id]_status
Example: sensor.indeklima_living_room_status
Not: sensor.living_room_temperature
```

**Wrong notification service:**
```
Verify service exists:
Developer Tools → Services
Search for your notify service
Test it manually
```

**Time window too narrow:**
```
Edit automation
Aktiv Fra: 09:00 (or earlier)
Aktiv Til: 21:00 (or later)
```

**Cooldown too long:**
```
Edit automation
Cooldown Timer: 2 hours (or less)
Or manually reset last_notified:
Developer Tools → States → Edit
```

**Test automation manually:**
```
Edit automation
Click "Run Actions" (top right)
Should trigger immediately if conditions met
Check phone for notification
```

---

### 7. Duplicate Devices After Upgrade

**Symptom:** Multiple "Indeklima" integrations or duplicate room devices

**Cause:** 
- Bug in v2.3.0 (encoding issue)
- Manual addition of same integration twice

**Solutions:**

**Clean reinstall (recommended):**

1. **Backup configuration (optional but recommended):**
   ```
   Settings → Integrations → Indeklima → 3 dots
   Download diagnostics (if available)
   Or screenshot your room configurations
   ```

2. **Remove ALL Indeklima entries:**
   ```
   Settings → Integrations
   Find each "Indeklima" entry
   Click entry → Delete
   Repeat for all duplicates
   ```

3. **Restart Home Assistant:**
   ```
   Settings → System → Restart
   ```

4. **Clear browser cache:**
   ```
   Ctrl+F5 (Windows/Linux)
   Cmd+Shift+R (Mac)
   Or Settings → Clear browsing data
   ```

5. **Re-add integration (with v2.3.1+):**
   ```
   Settings → Integrations → Add Integration
   Search: Indeklima
   Configure all rooms fresh
   ```

**Prevention:**
- Always use v2.3.1 or v2.3.2
- Never downgrade to v2.3.0
- Only add integration once

---

### 8. High Severity Score (Seems Wrong)

**Symptom:** Severity shows 70+ but everything looks fine

**Diagnostic Steps:**

1. **Check ALL metrics in ALL rooms:**
   ```
   Developer Tools → States
   Search: sensor.indeklima_
   
   Look for HIGH values in:
   - Humidity (any room > threshold?)
   - CO2 (any room > 1000 ppm?)
   - VOC (any room > 3.0?)
   - Formaldehyde (any room > 0.15?)
   ```

2. **Review severity calculation:**
   ```
   Severity formula (per room):
   
   Humidity excess:     0-30 points
   CO2 excess:          0-30 points
   VOC excess:          0-20 points
   Formaldehyde excess: 0-20 points
   Total:              0-100 points
   
   One bad value can spike the score!
   ```

3. **Check thresholds:**
   ```
   Settings → Integrations → Indeklima → Configure
   Thresholds
   
   Are they appropriate for your situation?
   - Default humidity winter: 55%
   - Default humidity summer: 60%
   - Default CO2: 1000 ppm
   ```

**Solutions:**

**Find the problem room:**
```
Check each room's status sensor attributes
Look for highest individual values
Focus fixing that specific room
```

**Adjust thresholds if too strict:**
```
Settings → Configure → Thresholds

Examples:
- Live in humid climate? Raise humidity max to 65%
- Have many people? Raise CO2 max to 1200 ppm
- Very sensitive? Lower thresholds
```

**Improve air circulation:**
```
Open internal doors
Good air circulation = 5% severity reduction
3+ internal doors open = "good" air circulation
```

**Example high severity causes:**
```
Room A: Humidity 65% (max 55%) → +30 points
Room B: CO2 1500 ppm (max 1000) → +15 points
Total: 45/100 = "Warning" status
```

---

### 9. Integration Won't Load After Upgrade

**Symptom:** After upgrading, integration shows error or doesn't load

**Diagnostic Steps:**

1. **Check logs immediately:**
   ```
   Settings → System → Logs
   Filter: "indeklima"
   Look for: ImportError, ModuleNotFoundError, SyntaxError
   ```

2. **Verify files are updated:**
   ```
   Check: custom_components/indeklima/
   All files present?
   manifest.json version correct?
   const.py version matches?
   ```

3. **Check for file corruption:**
   ```
   Open files in text editor
   Look for strange characters
   Verify file isn't empty
   ```

**Solutions:**

**Full reinstall:**

1. **Delete integration (in HA):**
   ```
   Settings → Integrations → Indeklima → Delete
   ```

2. **Delete files (in file system):**
   ```
   Delete: custom_components/indeklima/
   ```

3. **Restart Home Assistant:**
   ```
   Settings → System → Restart
   ```

4. **Re-download from HACS or GitHub:**
   ```
   HACS → Integrations → Redownload
   Or: Download fresh from GitHub releases
   ```

5. **Copy to custom_components:**
   ```
   Extract zip
   Copy custom_components/indeklima to config/custom_components/
   ```

6. **Restart again:**
   ```
   Settings → System → Restart
   ```

7. **Re-add integration:**
   ```
   Settings → Integrations → Add Integration
   Search: Indeklima
   ```

**Check for conflicting custom components:**
```
Sometimes other integrations interfere
Temporarily disable other custom integrations
Test if Indeklima loads
```

---

## 🛠️ Advanced Troubleshooting

### Enable Debug Logging

For detailed troubleshooting, enable debug logging:

**Method 1: configuration.yaml**
```yaml
logger:
  default: info
  logs:
    custom_components.indeklima: debug
```

**Method 2: Developer Tools**
```
Developer Tools → Services
Service: logger.set_level
Service data:
  custom_components.indeklima: debug
```

Then check logs:
```
Settings → System → Logs
Filter: "indeklima"
```

**Remember to disable after troubleshooting:**
```yaml
logger:
  default: info
  logs:
    custom_components.indeklima: info
```

---

### Check Coordinator Data

See exactly what data the integration has:

```
Developer Tools → States
Find: any indeklima sensor
Click "Related" tab
See all sensors and their data
```

Or use a template:
```yaml
# Developer Tools → Template
{{ state_attr('sensor.indeklima_hub_severity_score', 'attribution') }}
{{ states.sensor | selectattr('entity_id', 'search', 'indeklima') | list }}
```

---

### Verify Entity IDs

Make sure your entity IDs match expectations:

**Pattern for hub sensors:**
```
sensor.indeklima_hub_[sensor_type]

Examples:
sensor.indeklima_hub_severity_score
sensor.indeklima_hub_average_humidity
sensor.indeklima_hub_air_circulation
```

**Pattern for room sensors:**
```
sensor.indeklima_[room_id]_[metric]

Examples:
sensor.indeklima_living_room_status
sensor.indeklima_living_room_temperature
sensor.indeklima_bedroom_humidity
sensor.indeklima_koekken_co2
```

**Room ID normalization:**
```
"Living Room" → living_room
"Bedroom 1" → bedroom_1
"Køkken" → koekken (ø→oe)
"Badeværelse" → badevaerelse (æ→ae, ø→oe)
```

---

## 📞 Getting Help

If you've tried everything and still have issues:

1. **Gather information:**
   - Indeklima version (Settings → Integrations)
   - Home Assistant version (Settings → About)
   - Log excerpts (Settings → System → Logs)
   - Screenshots of configuration
   - What you've already tried

2. **Search existing issues:**
   - GitHub Issues: https://github.com/kingpainter/indeklima/issues
   - Check both open AND closed issues

3. **Create new issue (if needed):**
   - Use issue template
   - Provide all information above
   - Be specific about the problem
   - Include error messages from logs

4. **Ask in discussions:**
   - GitHub Discussions: https://github.com/kingpainter/indeklima/discussions
   - For general questions or ideas
   - Community can help too

---

## ✅ Preventive Maintenance

Avoid issues before they happen:

### Regular Checks (Monthly)

- [ ] Review sensor battery levels
- [ ] Check for unavailable sensors
- [ ] Verify automations still work
- [ ] Review and adjust thresholds if needed
- [ ] Check for integration updates

### After Home Assistant Updates

- [ ] Verify integration still loads
- [ ] Check logs for new warnings
- [ ] Test one automation
- [ ] Verify sensors update correctly

### After Indeklima Updates

- [ ] Read changelog carefully
- [ ] Check for breaking changes
- [ ] Test in dev environment if possible
- [ ] Update automations/dashboards if needed

---

**Last Updated:** 2025-01-18 (v2.3.2)

**Need more help?** See [README.md](README.md) or open an issue on GitHub!
