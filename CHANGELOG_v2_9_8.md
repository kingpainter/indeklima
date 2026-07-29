# Changelog v2.9.8

**Date:** 2026-07-29
**Focus:** `indeklima-tablet-card` layout iteration + HACS release-tag fix

---

## Context

Iterative layout work on `IndeklimaTabletCard` (the 3-column landscape/panel
card, used on the 7" Lenovo tablet in `type: panel` view), done directly from
screenshot feedback across several rounds. Versions 2.9.5–2.9.7 were built in
a sandboxed environment during a Filesystem MCP outage and delivered as
downloads; v2.9.8 is the point where these changes were confirmed applied to
both the GitHub repo and this changelog, and where a version bump + release
was made specifically to force HACS to pick up the new file (see "Fixed"
below).

## Changed — `indeklima-cards.js` (`IndeklimaTabletCard`)

1. **Swapped Gennemsnit/Status ("green") with Tendenser/Vinduer ("red")**
   content blocks between the left and right sidebar columns. The severity
   ring + score/room-count/window-count header block at the top of the left
   column was deliberately kept in place — only the two lower content blocks
   swapped sides, not the entire columns.
2. **Equalized sidebar column widths** to 175px/175px (previously 175px/150px),
   with the extra width taken from the flexible middle (room list) column,
   which is `1fr`.
3. **Bottom-aligned the Status block** (Udluftning/Skimmel/Cirkulation/
   Affugter) with the room list in the middle column: split the green content
   into `.green-top` (Gennemsnit) and `.green-bottom` (Status), made the
   containing column a flex column, and applied `margin-top: auto` to
   `.green-bottom`.
4. **Restyled the Gennemsnit avg-cells** to visually match the Status
   stat-cells: added a per-metric icon (thermometer/droplet/fog/gauge),
   increased padding (10px → 14px), and added a colored `border-bottom`
   (blue for Temp, purple for Tryk, house status color for Fugt/CO₂).
5. **Removed scroll capability** on the 3-column grid (`.cols`) and its
   `.col` children — changed `overflow-y: auto` to `overflow: visible`,
   since the layout has been reworked to fit within the panel without
   scrolling.

## Fixed — HACS reinstalling stale version

**Symptom:** After a HACS update, the tablet card reverted to what looked
like an old layout, even though the correct file had been manually placed on
the HA server and the GitHub repo's working tree already contained the new
code.

**Root cause:** HACS installs from the latest published GitHub release/tag,
not directly from the repo's default branch working tree. No release had
been tagged since v2.9.4, so HACS kept re-installing that old release
regardless of newer, untagged commits/files sitting in the repo.

**Fix:** Bumped `__version__` in `const.py` and `version` in `manifest.json`
from `2.9.4` → `2.9.8`, and updated the version comment in
`indeklima-cards.js` to match. A new GitHub release/tag (`v2.9.8`) still
needs to be published (commit, push, and tag via GitHub Desktop) for HACS to
actually have something newer to install — this is a manual step outside
Claude's Filesystem MCP access.

## Learned rule

When a frontend/backend fix appears to have "reverted" after a HACS update
despite the GitHub repo looking correct, check the **live server file**
directly (not just the GitHub working tree) and compare version markers.
HACS operates on published releases/tags, not on whatever the latest commit
in the default branch happens to contain — a version bump + new release is
required to get HACS to actually redeploy new frontend code, even for
JS-only changes with no backend logic change.
