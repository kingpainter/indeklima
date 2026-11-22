// Indeklima – Central icon definitions (frontend)
//
// Single source of truth for every emoji/glyph used by the Indeklima panel and
// Lovelace cards. Change an icon here and it changes everywhere.
//
// Values are kept identical to the icons previously hardcoded in
// indeklima-cards.js and indeklima-panel.js, so this file introduces no visual
// change. Several names intentionally share a glyph (e.g. WIND for PM2.5,
// circulation and air quality) so each concept can be restyled on its own later.
//
// Loaded as an ES module by both files via: import { ICONS } from "/api/indeklima-icons";

export const ICONS = {
  // Sensors & metrics
  THERMO: "🌡️",
  WATER: "💧",
  FOG: "🌫️",
  BUBBLES: "🫧",
  COMPASS: "🧭",
  CHART: "📊",
  WIND: "💨",
  TORNADO: "🌪️",
  SUN_CLOUD: "🌤️",
  MOLD: "🦠",
  VOC: "🧪",
  FORMALDEHYDE: "⚗️",

  // Ventilation & air quality
  VENT_YES: "🌬️",
  THINK: "🤔",
  CLOCK: "⏰",
  LEAF: "🌿",
  BLOCK: "🚫",
  SKULL: "☠️",

  // Windows, doors, dehumidifier
  WINDOW: "🪟",
  DOOR: "🚪",
  BLUE: "🔵",

  // Status & feedback
  CHECK: "✅",
  WARN: "⚠️",
  WARN_PLAIN: "⚠",
  RED: "🔴",
  HOURGLASS: "⏳",
  REFRESH: "🔄",
  HOME: "🏠",
  CLOSE: "✕",
  TRIANGLE_UP: "▲",
  TRIANGLE_DOWN: "▼",

  // Trend arrows
  TREND_UP: "↗",
  TREND_DOWN: "↘",
  TREND_FLAT: "→",
};
