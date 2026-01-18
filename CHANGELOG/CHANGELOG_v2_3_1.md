# Changelog Entry for v2.3.1

## [2.3.1] - 2025-01-18

### Fixed - CRITICAL ENCODING FIXES
- 🔧 **Complete Encoding Cleanup** - Removed ALL encoding issues
  - All Python code now uses ONLY English + ASCII
  - All Danish text moved to translation files (strings.json, da.json)
  - Fixed æ, ø, å character handling in all files
  - Removed emojis from Python code
  - Clean UTF-8 encoding throughout

### Technical
- ✅ `normalize_room_id()` function properly handles Danish characters
- ✅ All constants in English (STATUS_GOOD, TREND_STABLE, etc.)
- ✅ State translations via strings.json/da.json
- ✅ No double-encoding issues
- ✅ Config flow labels use translation keys
- ✅ Version incremented to 2.3.1

### Migration from v2.3.0
- **No breaking changes** - Direct upgrade
- If you had encoding issues in v2.3.0, this fixes them all
- Recommend clean install if you experienced duplicate devices

---

**This is the CLEAN version you should use!**
