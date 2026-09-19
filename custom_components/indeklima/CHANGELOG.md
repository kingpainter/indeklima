# Indeklima - Version History

## Current Version: 2.9.10

### [2.9.10] - 2026-09-19

**Type:** Security & Performance Patch

**Summary:** Critical security fixes for CSS injection vulnerability, memory leak prevention, performance optimization, and accessibility improvements.

**Key Changes:**
- 🔒 Security: Whitelist-based color validation prevents CSS injection
- 🔒 Security: XSS protection with error boundaries around HTML assignments
- ⚡ Performance: Memory leak fix in polling intervals
- ⚡ Performance: Single-pass array filtering optimization
- ⚡ Performance: Opacity-based animations (GPU efficiency)
- ♿ Accessibility: ARIA labels for image elements and decorative SVG hiding
- 🐛 Bug Fixes: Enhanced null-safety checks and error handling

**Breaking Changes:** None

**Affected Files:**
- `indeklima-cards.js` (1,476 lines)
- `const.py` (version bump)
- `manifest.json` (version bump)

**Full Changelog:** See [`CHANGELOG_v2_9_10.md`](CHANGELOG_v2_9_10.md)

---

## Upgrade Instructions

### Via HACS
Home Assistant will automatically detect and notify about this update through the Community Store.

### Manual Update
1. Navigate to your Home Assistant integrations folder
2. Replace the `indeklima/` directory with the updated version
3. Restart Home Assistant or reload the integration

### Post-Update
No special configuration changes are required. Existing setups will continue to work with enhanced security and performance.

---

## Version Archives

For detailed information about previous versions, refer to individual `CHANGELOG_v*` files.

---

**Integration:** Indeklima (Home Assistant)  
**Repository:** https://github.com/kongemaleren/indeklima  
**Support:** GitHub Issues
