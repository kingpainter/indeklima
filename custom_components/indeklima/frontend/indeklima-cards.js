// Indeklima – Custom Lovelace Cards (FIXED VERSION)
// Version: 2.9.10 (with security, performance, and accessibility fixes)
// Cards:
//   custom:indeklima-room-card   – single room card (mobile/tablet)
//   custom:indeklima-hub-card    – house overview, original mobile design (vertical)
//   custom:indeklima-tablet-card – house overview, landscape/tablet 3-column
//   custom:indeklima-room-detail-card – detailed room view
// Last Updated: June 2026 (Fixed: September 2026)

// ─────────────────────────────────────────────────────────────────────────────
// Shared helpers
// ─────────────────────────────────────────────────────────────────────────────

const INDEKLIMA_DOMAIN = "indeklima";

function esc(s) {
  return String(s ?? "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function fmtNum(val, unit, decimals = 0) {
  if (val == null) return "–";
  const n = parseFloat(val);
  if (isNaN(n)) return "–";
  return n.toFixed(decimals) + " " + unit;
}

/**
 * FIXED: Whitelist-based color selection to prevent CSS injection.
 * All color values are now explicitly validated.
 */
function statusColor(status) {
  const colorMap = {
    "critical": "#ef4444",
    "warning":  "#f59e0b",
    "good":     "#10b981"
  };
  return colorMap[status] ?? "#64748b"; // Fallback to neutral
}

function statusLabel(status) {
  if (status === "critical") return "Kritisk";
  if (status === "warning")  return "Advarsel";
  return "God";
}

function trendIcon(trend) {
  if (trend === "rising")  return "↗";
  if (trend === "falling") return "↘";
  return "→";
}

function trendColor(trend) {
  const colorMap = {
    "rising":  "#ef4444",
    "falling": "#10b981",
    "stable":  "#94a3b8"
  };
  return colorMap[trend] ?? "#94a3b8";
}

function trendLabel(trend) {
  if (trend === "rising")  return "Stigende";
  if (trend === "falling") return "Faldende";
  return "Stabil";
}

function circLabel(c) {
  if (c === "good")     return "God luftcirkulation";
  if (c === "moderate") return "Moderat";
  return "Dårlig cirkulation";
}

function circColor(c) {
  const colorMap = {
    "good":     "#10b981",
    "moderate": "#f59e0b",
    "poor":     "#ef4444"
  };
  return colorMap[c] ?? "#64748b";
}

function ventLabel(v) {
  if (v === "yes")      return "Luft ud nu!";
  if (v === "optional") return "Valgfrit";
  return "Vent";
}

function ventColor(v) {
  const colorMap = {
    "yes":      "#10b981",
    "optional": "#f59e0b",
    "no":       "#64748b"
  };
  return colorMap[v] ?? "#64748b";
}

function moldLabel(m) {
  if (m === "critical") return "Kritisk skimmelrisiko";
  if (m === "high")     return "Høj skimmelrisiko";
  if (m === "moderate") return "Moderat skimmelrisiko";
  return "Lav skimmelrisiko";
}

function moldColor(m) {
  const colorMap = {
    "critical": "#ef4444",
    "high":     "#f97316",
    "moderate": "#f59e0b",
    "low":      "#10b981"
  };
  return colorMap[m] ?? "#10b981";
}

function dehumLabel(v) {
  if (v === "yes")      return "Tænd affugter";
  if (v === "optional") return "Overvæg affugter";
  return "Affugter ikke nødvendig";
}

function dehumIcon(v) {
  if (v === "yes")      return "💧";
  if (v === "optional") return "🔵";
  return null;
}

function dehumColor(v) {
  const colorMap = {
    "yes":      "#f97316",
    "optional": "#60a5fa",
    "no":       "#64748b"
  };
  return colorMap[v] ?? "#64748b";
}

function moldIcon(m) {
  if (m === "critical" || m === "high" || m === "moderate") return "🦠";
  return "✅";
}

function dehumModeLabel(m) {
  if (m === "manual") return "Manuel";
  if (m === "auto")   return "Automatisk";
  return "Fra";
}

function fmtTimeSince(iso) {
  if (!iso) return "";
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return "";
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch (e) { return ""; }
}

function baseCSS() {
  return `
    --bg:   var(--card-background-color, #1a2535);
    --bg2:  var(--secondary-background-color, #243044);
    --text: var(--primary-text-color, #e2e8f0);
    --sub:  var(--secondary-text-color, #94a3b8);
    --div:  var(--divider-color, rgba(148,163,184,0.12));
  `;
}

function severityRingHTML(severity, color, size) {
  const s  = size || 90;
  const r  = Math.round(s * 0.4);
  const cx = Math.round(s / 2);
  const circ = 2 * Math.PI * r;
  const fill = (Math.min(100, severity) / 100) * circ;
  const gap  = circ - fill;
  const valSize = s >= 90 ? 22 : 18;
  return `
    <div class="ring-wrap">
      <svg class="ring-svg" viewBox="0 0 ${s} ${s}" style="width:${s}px;height:${s}px;display:block;" aria-hidden="true">
        <circle cx="${cx}" cy="${cx}" r="${r}" fill="none" stroke="var(--div)" stroke-width="8"/>
        <circle cx="${cx}" cy="${cx}" r="${r}" fill="none"
          stroke="${color}" stroke-width="8" stroke-linecap="round"
          stroke-dasharray="${fill} ${gap}" stroke-dashoffset="0"
          transform="rotate(-90 ${cx} ${cx})"/>
      </svg>
      <div class="ring-center">
        <div class="ring-val" style="color:${color};font-size:${valSize}px">${Math.round(severity)}</div>
        <div class="ring-unit">/ 100</div>
      </div>
    </div>`;
}


// ─────────────────────────────────────────────────────────────────────────────
// indeklima-room-card (FIXED)
// ─────────────────────────────────────────────────────────────────────────────

class IndeklimaRoomCard extends HTMLElement {
  static getStubConfig() { return { room: "Stue" }; }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._data = null;
    this._config = {};
    this._interval = null;
    this._errCount = 0;
  }

  setConfig(config) {
    if (!config.room) throw new Error("indeklima-room-card: 'room' is required");
    this._config = config;
    this._render();
  }

  set hass(h) {
    const first = !this._hass;
    this._hass = h;
    if (first) this._load();
  }

  connectedCallback() {
    // FIXED: Guard against multiple intervals
    if (this._interval) clearInterval(this._interval);

    this._interval = setInterval(() => {
      // FIXED: Set interval to null after clearing to prevent double-clear
      if (this._errCount > 5) {
        clearInterval(this._interval);
        this._interval = null;
        return;
      }
      if (document.visibilityState === "visible") this._load();
    }, 30000);
  }

  disconnectedCallback() {
    // FIXED: Proper cleanup
    if (this._interval) {
      clearInterval(this._interval);
      this._interval = null;
    }
  }

  async _load() {
    if (!this._hass) return;
    try {
      this._data = await this._hass.callWS({
        type: `${INDEKLIMA_DOMAIN}/get_room_data`,
        room_name: this._config.room,
      });
      this._errCount = 0;
    } catch (e) {
      this._errCount++;
    }
    this._render();
  }

  _render() {
    const r     = this._data;
    const title = this._config.title ?? this._config.room;
    const status = r?.status || "good";
    const color  = statusColor(status);
    const sev    = Math.round(r?.severity || 0);
    const showP  = this._config.show_pressure ?? false;

    const metric = (icon, val, lbl) =>
      `<div class="metric"><div class="m-icon">${icon}</div><div class="m-val">${val}</div><div class="m-lbl">${lbl}</div></div>`;

    const metrics = r ? [
      (r?.temperature_sensors_count ?? 0) > 0 ? metric("&#127777;&#65039;", fmtNum(r.temperature,"°C",1), "Temp") : "",
      (r?.humidity_sensors_count ?? 0) > 0 ? metric("&#128167;", fmtNum(r.humidity,"%"), "Fugt") : "",
      (r?.co2_sensors_count ?? 0) > 0 ? metric("&#127787;&#65039;", fmtNum(r.co2,"ppm"), "CO₂") : "",
      (showP && (r?.pressure_sensors_count ?? 0) > 0) ? metric("&#129517;", fmtNum(r.pressure,"hPa"), "Tryk") : "",
    ].filter(Boolean).join("") : "";

    // FIXED: Error boundary for innerHTML
    const html = `
      <style>
        :host { display: block; ${baseCSS()} font-family: var(--paper-font-body1_-_font-family, sans-serif); }
        .card {
          background: var(--bg); border-radius: 18px; padding: 14px 16px;
          color: var(--text); box-shadow: var(--ha-card-box-shadow, 0 2px 8px rgba(0,0,0,.15));
          border-left: 5px solid ${color};
          background-image: linear-gradient(135deg, ${color}12 0%, transparent 50%);
        }
        .header { display:flex; align-items:center; justify-content:space-between; margin-bottom:12px; }
        .room-name { font-size:16px; font-weight:700; }
        .status-pill {
          font-size:10px; font-weight:700; padding:3px 9px; border-radius:20px;
          background:${color}22; color:${color}; text-transform:uppercase; letter-spacing:.5px;
          ${status !== "good" ? "animation:blink 2s infinite;" : ""}
        }
        @keyframes blink { 0%,100%{opacity:1}50%{opacity:.55} }
        @keyframes led-fade { 0%,100%{opacity:1} 50%{opacity:.45} }
        @keyframes crit-glow { 0%,100%{opacity:1} 50%{opacity:.6} }
        .crit-since {
          font-size:10px; color:#ef4444; margin:-6px 0 10px; font-weight:600;
          display:inline-block; background:#ef444414; border-radius:8px; padding:2px 8px;
          animation: crit-glow 3s ease-in-out infinite;
        }
        .chip.alarm { color:#ef4444; background:#ef444422; animation: led-fade 2.4s ease-in-out infinite; }
        .metrics { display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-bottom:10px; }
        .metric { background:var(--bg2); border-radius:10px; padding:9px 6px; text-align:center; }
        .m-icon { font-size:16px; margin-bottom:3px; }
        .m-val  { font-size:14px; font-weight:700; line-height:1.1; }
        .m-lbl  { font-size:9px; color:var(--sub); margin-top:2px; text-transform:uppercase; }
        .sev-row { display:flex; align-items:center; gap:8px; font-size:11px; color:var(--sub); }
        .sev-bar { flex:1; height:4px; background:var(--div); border-radius:2px; overflow:hidden; }
        .sev-fill { height:100%; background:${color}; border-radius:2px; width:${sev}%; transition:width .6s; }
        .sev-val { font-weight:700; color:${color}; font-size:12px; min-width:36px; text-align:right; }
        .footer { display:flex; gap:6px; margin-top:6px; flex-wrap:wrap; }
        .chip { font-size:10px; background:var(--bg2); padding:3px 7px; border-radius:6px; color:var(--sub); }
        .chip.open { color:#0ea5e9; }
        .rc-status {
          display:flex; align-items:stretch; margin-top:8px;
          background:var(--bg2); border-radius:12px; overflow:hidden;
        }
        .rc-sc-cell {
          flex:1; display:flex; flex-direction:column;
          align-items:center; justify-content:center;
          padding:8px 4px; gap:2px;
          border-bottom:3px solid transparent;
        }
        .rc-sc-div { width:1px; background:var(--div); margin:6px 0; flex-shrink:0; }
        .rc-sc-ico { font-size:16px; line-height:1; }
        .rc-sc-val { font-size:10px; font-weight:700; text-align:center; line-height:1.2; }
        .rc-sc-lbl { font-size:7px; color:var(--sub); text-transform:uppercase; letter-spacing:.5px; }
        .loading { color:var(--sub); font-size:12px; padding:8px 0; }
      </style>
      <ha-card>
        <div class="card">
          <div class="header">
            <div class="room-name">${esc(title)}</div>
            <div class="status-pill">${r ? statusLabel(status) : "..."}</div>
          </div>
          ${r && status === "critical" && r.kritisk_siden ? `<div class="crit-since">⚠️ Kritisk siden ${fmtTimeSince(r.kritisk_siden)}</div>` : ""}
          ${!r ? '<div class="loading">Henter data...</div>' : `
            <div class="metrics">${metrics}</div>
            <div class="sev-row">
              <span>Alvorlighed</span>
              <div class="sev-bar"><div class="sev-fill"></div></div>
              <span class="sev-val">${sev}/100</span>
            </div>
            ${(r.outdoor_windows_open > 0 || r.internal_doors_open > 0 || r.air_circulation_bonus || r.led_alarm_active) ? `
            <div class="footer">
              ${r.led_alarm_active ? `<span class="chip alarm">🔴 LED alarm aktiv</span>` : ""}
              ${r.outdoor_windows_open > 0 ? `<span class="chip open">🪟 ${r.outdoor_windows_open} vindue${r.outdoor_windows_open>1?"r":""}</span>` : ""}
              ${r.internal_doors_open  > 0 ? `<span class="chip open">🚪 ${r.internal_doors_open} dør${r.internal_doors_open>1?"e":""}</span>` : ""}
              ${r.air_circulation_bonus    ? `<span class="chip open">💨 Bonus aktiv</span>` : ""}
            </div>` : ""}
            <div class="rc-status">
              <div class="rc-sc-cell" style="border-bottom-color:${moldColor(r.mold_risk||'low')}">
                <div class="rc-sc-ico">${moldIcon(r.mold_risk)}</div>
                <div class="rc-sc-val" style="color:${moldColor(r.mold_risk||'low')}">${r.mold_risk==="low"?"Lav":r.mold_risk==="moderate"?"Moderat":r.mold_risk==="high"?"Høj":"Kritisk"}</div>
                <div class="rc-sc-lbl">Skimmel</div>
              </div>
              ${r.has_dehumidifier ? `
              <div class="rc-sc-div"></div>
              <div class="rc-sc-cell" style="border-bottom-color:${dehumColor(r.dehumidifier_recommendation||'no')}">
                <div class="rc-sc-ico">${dehumIcon(r.dehumidifier_recommendation||'no') || '💧'}</div>
                <div class="rc-sc-val" style="color:${dehumColor(r.dehumidifier_recommendation||'no')}">${r.dehumidifier_recommendation==='yes'?'Tænd':r.dehumidifier_recommendation==='optional'?'Overvej':'OK'}</div>
                <div class="rc-sc-lbl">Affugter${r.dehumidifier_mode && r.dehumidifier_mode !== 'off' ? ` · ${dehumModeLabel(r.dehumidifier_mode)}` : ''}</div>
              </div>` : ""}
            </div>
          `}
        </div>
      </ha-card>`;

    try {
      this.shadowRoot.innerHTML = html;
    } catch (e) {
      console.error("[indeklima-room-card] Render failed:", e);
      this.shadowRoot.innerHTML = `
        <style>${baseCSS()}</style>
        <div style="color:#ef4444;padding:16px;border-radius:12px;background:var(--bg2);">
          <strong>Render-fejl:</strong> ${esc(e.message)}
        </div>`;
    }
  }

  getCardSize() { return 3; }
}

if (!customElements.get("indeklima-room-card")) {
  customElements.define("indeklima-room-card", IndeklimaRoomCard);
}


// ─────────────────────────────────────────────────────────────────────────────
// indeklima-hub-card (FIXED)
// ─────────────────────────────────────────────────────────────────────────────

class IndeklimaHubCard extends HTMLElement {
  static getStubConfig() { return { title: "Indeklima Overblik" }; }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._data = null;
    this._config = {};
    this._interval = null;
    this._errCount = 0;
  }

  setConfig(config) {
    this._config = config ?? {};
    this._render();
  }

  set hass(h) {
    const first = !this._hass;
    this._hass = h;
    if (first) this._load();
  }

  connectedCallback() {
    // FIXED: Guard against multiple intervals
    if (this._interval) clearInterval(this._interval);

    this._interval = setInterval(() => {
      if (this._errCount > 5) {
        clearInterval(this._interval);
        this._interval = null;
        return;
      }
      if (document.visibilityState === "visible") this._load();
    }, 30000);
  }

  disconnectedCallback() {
    if (this._interval) {
      clearInterval(this._interval);
      this._interval = null;
    }
  }

  async _load() {
    if (!this._hass) return;
    try {
      this._data = await this._hass.callWS({ type: `${INDEKLIMA_DOMAIN}/get_climate_data` });
      this._errCount = 0;
    } catch (e) {
      this._errCount++;
    }
    this._render();
  }

  _render() {
    const d       = this._data;
    const title   = this._config.title ?? "Indeklima Overblik";
    const compact = this._config.compact ?? false;
    const status  = d?.status || "good";
    const color   = statusColor(status);
    const sev     = d?.severity || 0;
    const rooms   = d?.rooms   || [];
    const avgs    = d?.averages || {};
    const trends  = d?.trends  || {};
    const vent    = d?.ventilation || {};
    const vColor  = ventColor(vent.status);

    // FIXED: Single-pass room filtering instead of double filter
    const problemRooms = [];
    const okRooms = [];
    for (const room of rooms) {
      (room.status === "good" ? okRooms : problemRooms).push(room);
    }

    const makeRoomCard = (r) => {
      const rc = statusColor(r.status);
      const metrics = [
        (r?.temperature_sensors_count ?? 0) > 0 ? `<div class="rc-metric"><div class="rc-val">${fmtNum(r.temperature,"°C",1)}</div><div class="rc-lbl">Temp</div></div>` : "",
        (r?.humidity_sensors_count ?? 0) > 0 ? `<div class="rc-metric"><div class="rc-val">${fmtNum(r.humidity,"%")}</div><div class="rc-lbl">Fugt</div></div>` : "",
        (r?.co2_sensors_count ?? 0) > 0 ? `<div class="rc-metric"><div class="rc-val">${fmtNum(r.co2,"ppm")}</div><div class="rc-lbl">CO₂</div></div>` : "",
      ].filter(Boolean).join("");
      return `<div class="room-card" style="border-left-color:${rc};background-image:linear-gradient(90deg,${rc}0e 0%,transparent 40%);">
        <div class="rc-top">
          <div class="rc-name">${esc(r.name)}</div>
          <span class="rc-pill" style="background:${rc}22;color:${rc};${r.status!=="good"?"animation:blink 2s infinite;":""}">${statusLabel(r.status)}</span>
        </div>
        <div class="rc-bottom">
          <div class="rc-metrics">${metrics}</div>
          <span class="rc-mold" style="color:${moldColor(r.mold_risk||'low')};font-size:10px;">${moldIcon(r.mold_risk)} ${moldLabel(r.mold_risk)}</span>
        </div>
      </div>`;
    };

    const problemCards = problemRooms.map(makeRoomCard).join("");
    const okChips = okRooms.map(r =>
      `<div class="ok-chip">✅ ${esc(r.name)}</div>`
    ).join("");
    const okSection = okRooms.length > 0 ? `
      <div class="ok-rooms-wrap">
        <div class="ok-rooms-lbl">${okRooms.length} rum uden problemer</div>
        <div class="ok-chips-row">${okChips}</div>
      </div>` : "";

    const roomCards = problemCards + okSection;

    const html = `
      <style>
        :host { display:block; ${baseCSS()} font-family:var(--paper-font-body1_-_font-family,sans-serif); }
        .card {
          background:var(--bg); border-radius:18px; padding:16px 18px;
          color:var(--text); box-shadow:var(--ha-card-box-shadow,0 2px 8px rgba(0,0,0,.15));
        }
        .card-title {
          font-size:12px; font-weight:700; text-transform:uppercase;
          letter-spacing:1px; color:var(--sub); margin-bottom:14px;
        }
        .divider { height:1px; background:var(--div); margin:12px 0; }
        .section-lbl {
          font-size:10px; font-weight:600; text-transform:uppercase;
          letter-spacing:1px; color:var(--sub); margin-bottom:8px;
        }
        .loading { color:var(--sub); font-size:13px; padding:8px 0; }

        .top-row { display:flex; align-items:center; gap:16px; }
        .ring-wrap { position:relative; flex-shrink:0; }
        .ring-center {
          position:absolute; inset:0;
          display:flex; flex-direction:column; align-items:center; justify-content:center;
        }
        .ring-val  { font-weight:700; line-height:1; }
        .ring-unit { font-size:10px; color:var(--sub); }
        .top-info { flex:1; min-width:0; }
        .status-badge {
          display:inline-flex; align-items:center; gap:5px;
          padding:4px 10px; border-radius:20px;
          font-size:11px; font-weight:700; margin-bottom:8px;
        }
        .badge-dot { width:6px; height:6px; border-radius:50%; animation:bdot 2s infinite; }
        @keyframes bdot { 0%,100%{opacity:1}50%{opacity:.4} }
        .status-title { font-size:16px; font-weight:700; margin-bottom:2px; }
        .status-sub   { font-size:12px; color:var(--sub); }

        .hub-sev-wrap { margin-top:10px; }
        .hub-sev-row {
          display:flex; justify-content:space-between; align-items:center;
          margin-bottom:5px; font-size:11px; color:var(--sub);
        }
        .hub-sev-lbl   { font-size:10px; }
        .hub-sev-score { font-size:12px; font-weight:700; }
        .hub-sev-track {
          height:6px; border-radius:3px; background:var(--div);
          overflow:visible; position:relative;
        }
        .hub-sev-fill {
          position:absolute; top:0; left:0; height:100%;
          border-radius:3px; transition:width .6s;
          box-shadow:0 0 6px var(--color, #10b981);
        }
        .hub-sev-marker {
          position:absolute; top:-3px;
          width:12px; height:12px; border-radius:50%;
          border:2px solid var(--bg);
          transition:left .6s;
          box-shadow:0 0 4px rgba(0,0,0,.4);
        }

        .avgs { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
        .avg-chip { background:var(--bg2); border-radius:8px; padding:7px 10px; text-align:center; flex:1; min-width:70px; }
        .avg-val { font-size:14px; font-weight:700; }
        .avg-lbl { font-size:9px; color:var(--sub); margin-top:2px; text-transform:uppercase; }

        .rooms-list { display:flex; flex-direction:column; gap:6px; }
        .room-card {
          background:var(--bg2); border-radius:12px; padding:10px 12px;
          border-left:4px solid transparent;
        }
        .rc-top  { display:flex; align-items:center; justify-content:space-between; margin-bottom:6px; }
        .rc-bottom { display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:4px; }
        .rc-name  { font-size:13px; font-weight:700; flex:1; min-width:0; }
        .rc-pill  {
          font-size:9px; font-weight:700; padding:2px 7px; border-radius:20px;
          text-transform:uppercase; letter-spacing:.4px; flex-shrink:0;
        }
        .rc-mold  { font-size:10px; flex-shrink:0; }
        .rc-metrics { display:flex; gap:5px; flex-wrap:wrap; }
        .rc-metric  { text-align:center; min-width:38px; }
        .rc-val     { font-size:12px; font-weight:700; line-height:1.1; }
        .rc-lbl     { font-size:8px; color:var(--sub); margin-top:1px; text-transform:uppercase; }
        .ok-rooms-wrap { margin-top:4px; padding:8px 10px; background:var(--bg2); border-radius:10px; }
        .ok-rooms-lbl  { font-size:9px; font-weight:600; color:var(--sub); text-transform:uppercase; letter-spacing:.8px; margin-bottom:6px; }
        .ok-chips-row  { display:flex; flex-wrap:wrap; gap:5px; }
        .ok-chip       { font-size:10px; background:var(--bg); color:#10b981; padding:3px 8px; border-radius:6px; border:1px solid #10b98130; }

        .status-center {
          display:flex; align-items:stretch;
          background:var(--bg2); border-radius:14px; overflow:hidden;
        }
        .sc-cell {
          flex:1; display:flex; flex-direction:column;
          align-items:center; justify-content:center;
          padding:10px 4px; gap:3px;
          border-bottom:3px solid transparent;
        }
        .sc-divider { width:1px; background:var(--div); margin:8px 0; flex-shrink:0; }
        .sc-icon  { font-size:20px; line-height:1; }
        .sc-val   { font-size:11px; font-weight:700; text-align:center; line-height:1.2; }
        .sc-lbl   { font-size:8px; color:var(--sub); text-transform:uppercase; letter-spacing:.6px; }

        .trends-row { display:flex; gap:8px; }
        .trend-chip { flex:1; background:var(--bg2); border-radius:10px; padding:10px 8px; text-align:center; }
        .trend-header { font-size:9px; font-weight:700; color:var(--sub); text-transform:uppercase; letter-spacing:.8px; margin-bottom:6px; display:flex; align-items:center; justify-content:center; gap:4px; }
        .trend-arrow { font-size:22px; font-weight:900; line-height:1; margin-bottom:4px; }
        .trend-label { font-size:10px; font-weight:600; margin-top:2px; }
      </style>
      <ha-card>
        <div class="card">
          <div class="card-title">${esc(title)}</div>
          ${!d ? '<div class="loading">Henter data...</div>' : `
            <div class="top-row">
              ${severityRingHTML(sev, color, 90)}
              <div class="top-info">
                <div class="status-badge" style="background:${color}1a;color:${color};" role="img" aria-label="${statusLabel(status)}">
                  <span class="badge-dot" style="background:${color}"></span>
                  ${statusLabel(status)}
                </div>
                <div class="status-title">${d.room_count} rum overv̊ges</div>
                <div class="status-sub">🪟 ${d.open_windows_count} åbne vinduer</div>
              </div>
            </div>
            <div class="hub-sev-wrap">
              <div class="hub-sev-row">
                <span class="hub-sev-lbl">Alvorligheds-score</span>
                <span class="hub-sev-score" style="color:${color}">${Math.round(sev)} / 100</span>
              </div>
              <div class="hub-sev-track">
                <div class="hub-sev-fill" style="width:${Math.min(100,sev)}%;background:${color}"></div>
                <div class="hub-sev-marker" style="left:calc(${Math.min(100,sev)}% - 6px);background:${color}"></div>
              </div>
            </div>

            ${!compact ? `
              <div class="divider"></div>
              <div class="section-lbl">Gennemsnit</div>
              <div class="avgs">
                ${(avgs?.temperature ?? null) != null ? `<div class="avg-chip"><div class="avg-val">${fmtNum(avgs.temperature,"°C",1)}</div><div class="avg-lbl">Temp</div></div>` : ""}
                ${(avgs?.humidity ?? null) != null ? `<div class="avg-chip"><div class="avg-val">${fmtNum(avgs.humidity,"%")}</div><div class="avg-lbl">Fugt</div></div>` : ""}
                ${(avgs?.co2 ?? null) != null ? `<div class="avg-chip"><div class="avg-val">${fmtNum(avgs.co2,"ppm")}</div><div class="avg-lbl">CO₂</div></div>` : ""}
              </div>

              <div class="divider"></div>
              <div class="section-lbl">Tendenser (15 min)</div>
              <div class="trends-row">
                <div class="trend-chip">
                  <div class="trend-header">💧 Fugtighed</div>
                  <div class="trend-arrow" style="color:${trendColor(trends.humidity)}">${trendIcon(trends.humidity)}</div>
                  <div class="trend-label" style="color:${trendColor(trends.humidity)}">${trendLabel(trends.humidity)}</div>
                </div>
                <div class="trend-chip">
                  <div class="trend-header">🌫️ CO₂</div>
                  <div class="trend-arrow" style="color:${trendColor(trends.co2)}">${trendIcon(trends.co2)}</div>
                  <div class="trend-label" style="color:${trendColor(trends.co2)}">${trendLabel(trends.co2)}</div>
                </div>
                <div class="trend-chip">
                  <div class="trend-header">📊 Score</div>
                  <div class="trend-arrow" style="color:${trendColor(trends.severity)}">${trendIcon(trends.severity)}</div>
                  <div class="trend-label" style="color:${trendColor(trends.severity)}">${trendLabel(trends.severity)}</div>
                </div>
              </div>` : ""}

            <div class="divider"></div>
            <div class="section-lbl">Indeklima Status</div>
            <div class="status-center">
              <div class="sc-cell" style="border-bottom-color:${moldColor(d.mold_risk||'low')}">
                <div class="sc-icon">${moldIcon(d.mold_risk)}</div>
                <div class="sc-val" style="color:${moldColor(d.mold_risk||'low')}">${d.mold_risk==="low"?"Lav":d.mold_risk==="moderate"?"Moderat":d.mold_risk==="high"?"Høj":"Kritisk"}</div>
                <div class="sc-lbl">Skimmel</div>
              </div>
              <div class="sc-divider"></div>
              <div class="sc-cell" style="border-bottom-color:${vColor}">
                <div class="sc-icon">${vent.status==="yes"?"🌬️":vent.status==="optional"?"🤔":"⏰"}</div>
                <div class="sc-val" style="color:${vColor}">${ventLabel(vent.status)}</div>
                <div class="sc-lbl">Udluftning</div>
              </div>
              <div class="sc-divider"></div>
              <div class="sc-cell" style="border-bottom-color:${circColor(d.air_circulation)}">
                <div class="sc-icon">${d.air_circulation==="good"?"💨":d.air_circulation==="moderate"?"🌪️":"💨"}</div>
                <div class="sc-val" style="color:${circColor(d.air_circulation)}">${d.air_circulation==="good"?"God":d.air_circulation==="moderate"?"Moderat":"Dårlig"}</div>
                <div class="sc-lbl">Cirkulation</div>
              </div>
              ${rooms.some(r => r.has_dehumidifier) ? `
              <div class="sc-divider"></div>
              <div class="sc-cell" style="border-bottom-color:${dehumColor(d.dehumidifier_recommendation||'no')}">
                <div class="sc-icon">${dehumIcon(d.dehumidifier_recommendation||'no') || '💧'}</div>
                <div class="sc-val" style="color:${dehumColor(d.dehumidifier_recommendation||'no')}">${d.dehumidifier_recommendation==='yes'?'Tænd':d.dehumidifier_recommendation==='optional'?'Overvej':'OK'}</div>
                <div class="sc-lbl">Affugter</div>
              </div>` : ""}
            </div>

            <div class="divider"></div>
            <div class="section-lbl">Rum</div>
            <div class="rooms-list">${roomCards}</div>
          `}
        </div>
      </ha-card>`;

    try {
      this.shadowRoot.innerHTML = html;
    } catch (e) {
      console.error("[indeklima-hub-card] Render failed:", e);
      this.shadowRoot.innerHTML = `
        <style>${baseCSS()}</style>
        <div style="color:#ef4444;padding:16px;border-radius:12px;background:var(--bg2);">
          <strong>Render-fejl:</strong> ${esc(e.message)}
        </div>`;
    }
  }

  getCardSize() { return this._config.compact ? 4 : 7; }
}

if (!customElements.get("indeklima-hub-card")) {
  customElements.define("indeklima-hub-card", IndeklimaHubCard);
}


// ─────────────────────────────────────────────────────────────────────────────
// indeklima-tablet-card (FIXED)
// ─────────────────────────────────────────────────────────────────────────────

class IndeklimaTabletCard extends HTMLElement {
  static getStubConfig() { return { title: "Indeklima Overblik" }; }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass = null;
    this._data = null;
    this._config = {};
    this._interval = null;
    this._errCount = 0;
  }

  setConfig(config) {
    this._config = config ?? {};
    this._render();
  }

  set hass(h) {
    const first = !this._hass;
    this._hass = h;
    if (first) this._load();
  }

  connectedCallback() {
    if (this._interval) clearInterval(this._interval);
    this._interval = setInterval(() => {
      if (this._errCount > 5) {
        clearInterval(this._interval);
        this._interval = null;
        return;
      }
      if (document.visibilityState === "visible") this._load();
    }, 30000);
  }

  disconnectedCallback() {
    if (this._interval) {
      clearInterval(this._interval);
      this._interval = null;
    }
  }

  async _load() {
    if (!this._hass) return;
    try {
      this._data = await this._hass.callWS({ type: `${INDEKLIMA_DOMAIN}/get_climate_data` });
      this._errCount = 0;
    } catch (e) {
      this._errCount++;
    }
    this._render();
  }

  _render() {
    const d      = this._data;
    const title  = this._config.title ?? "Indeklima Overblik";
    const status = d?.status || "good";
    const color  = statusColor(status);
    const sev    = d?.severity || 0;
    const rooms  = d?.rooms   || [];
    const avgs   = d?.averages || {};
    const trends = d?.trends  || {};
    const vent   = d?.ventilation || {};
    const vColor = ventColor(vent.status);

    const col1 = !d ? '<div class="loading">Henter...</div>' : `
      <div class="score-block">
        ${severityRingHTML(sev, color, 108)}
        <div class="score-meta">
          <div class="score-badge" style="background:${color}1a;color:${color};">
            <span class="bdot" style="background:${color}"></span>${statusLabel(status)}
          </div>
          <div class="score-sub">${d.room_count} rum</div>
          <div class="score-sub">🪟 ${d.open_windows_count} åbne vinduer</div>
        </div>
      </div>

      <div class="sec-lbl mt10">Gennemsnit</div>
      <div class="avg-grid">
        ${(avgs?.temperature ?? null) != null ? `<div class="avg-cell"><div class="av">${fmtNum(avgs.temperature,"°C",1)}</div><div class="al">Temp</div></div>` : ""}
        ${(avgs?.humidity ?? null) != null ? `<div class="avg-cell"><div class="av">${fmtNum(avgs.humidity,"%")}</div><div class="al">Fugt</div></div>` : ""}
        ${(avgs?.co2 ?? null) != null ? `<div class="avg-cell"><div class="av">${fmtNum(avgs.co2,"ppm")}</div><div class="al">CO2</div></div>` : ""}
        ${(avgs?.pressure ?? null) != null ? `<div class="avg-cell"><div class="av">${fmtNum(avgs.pressure,"hPa")}</div><div class="al">Tryk</div></div>` : ""}
      </div>

      <div class="divider"></div>
      <div class="sec-lbl">Status</div>
      <div class="stat-grid">
        <div class="stat-cell" style="border-bottom-color:${vColor}">
          <div class="stat-ico">${vent.status==="yes"?"🌬️":vent.status==="optional"?"🤔":"⏰"}</div>
          <div class="stat-val" style="color:${vColor}">${ventLabel(vent.status)}</div>
          <div class="stat-lbl">Udluftning</div>
        </div>
        <div class="stat-cell" style="border-bottom-color:${moldColor(d.mold_risk||'low')}">
          <div class="stat-ico">${moldIcon(d.mold_risk)}</div>
          <div class="stat-val" style="color:${moldColor(d.mold_risk||'low')}">${d.mold_risk==="low"?"Lav":d.mold_risk==="moderate"?"Moderat":d.mold_risk==="high"?"Høj":"Kritisk"}</div>
          <div class="stat-lbl">Skimmel</div>
        </div>
        <div class="stat-cell" style="border-bottom-color:${circColor(d.air_circulation)}">
          <div class="stat-ico">${d.air_circulation==="good"?"💨":d.air_circulation==="moderate"?"🌪️":"💨"}</div>
          <div class="stat-val" style="color:${circColor(d.air_circulation)}">${d.air_circulation==="good"?"God":d.air_circulation==="moderate"?"Moderat":"Dårlig"}</div>
          <div class="stat-lbl">Cirkulation</div>
        </div>
        ${rooms.some(r => r.has_dehumidifier) ? `
        <div class="stat-cell" style="border-bottom-color:${dehumColor(d.dehumidifier_recommendation||'no')}">
          <div class="stat-ico">${dehumIcon(d.dehumidifier_recommendation||'no') || '💧'}</div>
          <div class="stat-val" style="color:${dehumColor(d.dehumidifier_recommendation||'no')}">${d.dehumidifier_recommendation==='yes'?'Tænd':d.dehumidifier_recommendation==='optional'?'Overvej':'OK'}</div>
          <div class="stat-lbl">Affugter</div>
        </div>` : ""}
      </div>
    `;

    const roomRows = rooms.map(r => {
      const rc = statusColor(r.status);
      const sp = Math.min(100, r.severity || 0);
      return `
        <div class="room-row" style="border-left-color:${rc};background-image:linear-gradient(90deg,${rc}0d 0%,transparent 40%);">
          <div class="rr-left">
            <div class="rr-name">${esc(r.name)}</div>
            <span class="rr-pill" style="background:${rc}22;color:${rc};${r.status!=="good"?"animation:blink 2s infinite;":""}">${statusLabel(r.status)}</span>
            <span class="rr-mold" style="font-size:11px;margin-left:4px;color:${moldColor(r.mold_risk||'low')}">${moldIcon(r.mold_risk)} ${moldLabel(r.mold_risk)}</span>
          </div>
          <div class="rr-metrics">
            ${(r?.temperature_sensors_count ?? 0) > 0 ? `<div class="rrm"><div class="rrm-v">${fmtNum(r.temperature,"°C",1)}</div><div class="rrm-l">Temp</div></div>` : ""}
            ${(r?.humidity_sensors_count ?? 0) > 0 ? `<div class="rrm"><div class="rrm-v">${fmtNum(r.humidity,"%")}</div><div class="rrm-l">Fugt</div></div>` : ""}
            ${(r?.co2_sensors_count ?? 0) > 0 ? `<div class="rrm"><div class="rrm-v">${fmtNum(r.co2,"ppm")}</div><div class="rrm-l">CO2</div></div>` : ""}
          </div>
          <div class="rr-sev">
            <div class="rr-sev-val" style="color:${rc}">${Math.round(sp)}</div>
            <div class="rr-bar-bg"><div class="rr-bar" style="width:${sp}%;background:${rc}"></div></div>
          </div>
        </div>`;
    }).join("");

    const col2 = `
      <div class="sec-lbl">${rooms.length} rum</div>
      <div class="rooms-list">${roomRows || '<div class="loading">Ingen rum konfigureret</div>'}</div>
    `;

    const col3 = !d ? "" : `
      <div class="sec-lbl">Tendenser (15 min)</div>
      <div class="trends-col">
        ${[["💧","Fugtighed",trends.humidity],["🌫️","CO₂",trends.co2],["📊","Score",trends.severity]]
          .map(([ico, lbl, tr]) => `
            <div class="trend-row">
              <div class="trend-row-left">
                <span class="trend-ico">${ico}</span>
                <span class="trend-row-lbl">${lbl}</span>
              </div>
              <div class="trend-row-right">
                <span class="trend-row-arrow" style="color:${trendColor(tr)}">${trendIcon(tr)}</span>
                <span class="trend-row-txt" style="color:${trendColor(tr)}">${trendLabel(tr)}</span>
              </div>
            </div>`).join("")}
      </div>

      <div class="divider"></div>
      <div class="sec-lbl">Vinduer / døre</div>
      ${(d?.open_windows && d.open_windows.length)
        ? `<div class="win-list">${d.open_windows.map(w=>`<div class="win-chip">🪟 ${esc(w)}</div>`).join("")}</div>`
        : `<div class="no-win">Ingen åbne vinduer</div>`}
    `;

    const html = `
      <style>
        :host { display:block; height:100%; ${baseCSS()} font-family:var(--paper-font-body1_-_font-family,sans-serif); }
        ha-card {
          width:100%; height:100%; min-height:0;
          max-height:100vh;
          display:flex; flex-direction:column; overflow:hidden;
          background:var(--bg); border-radius:18px;
          box-shadow:var(--ha-card-box-shadow,0 2px 8px rgba(0,0,0,.15));
        }
        .card {
          flex:1; min-height:0;
          display:flex; flex-direction:column; overflow:hidden;
          padding:14px 16px;
          color:var(--text);
        }
        .card-title {
          flex-shrink:0;
          font-size:11px; font-weight:700; text-transform:uppercase;
          letter-spacing:1px; color:var(--sub); margin-bottom:12px;
        }
        .divider { height:1px; background:var(--div); margin:14px 0; }
        .sec-lbl {
          font-size:11px; font-weight:600; text-transform:uppercase;
          letter-spacing:1px; color:var(--sub); margin-bottom:8px;
        }
        .mt10 { margin-top:14px; }
        .loading { color:var(--sub); font-size:12px; }

        .cols { flex:1; min-height:0; display:grid; grid-template-columns:150px 1fr 175px; gap:0 14px; align-items:stretch; overflow:hidden; }
        .col { min-width:0; min-height:0; overflow:auto; }
        .col-mid { border-left:1px solid var(--div); border-right:1px solid var(--div); padding:0 14px; }

        .score-block { display:flex; align-items:center; gap:12px; margin-bottom:8px; }
        .ring-wrap { position:relative; flex-shrink:0; }
        .ring-center {
          position:absolute; inset:0;
          display:flex; flex-direction:column; align-items:center; justify-content:center;
        }
        .ring-val  { font-weight:700; line-height:1; }
        .ring-unit { font-size:10px; color:var(--sub); }
        .score-badge {
          display:inline-flex; align-items:center; gap:4px;
          padding:3px 8px; border-radius:20px;
          font-size:11px; font-weight:700; margin-bottom:4px;
        }
        .bdot { width:5px; height:5px; border-radius:50%; animation:bdot 2s infinite; }
        @keyframes bdot { 0%,100%{opacity:1}50%{opacity:.4} }
        .score-sub { font-size:11px; color:var(--sub); }

        .avg-grid { display:grid; grid-template-columns:1fr 1fr; gap:8px; }
        .avg-cell { background:var(--bg2); border-radius:8px; padding:10px 6px; text-align:center; }
        .av { font-size:14px; font-weight:700; }
        .al { font-size:9px; color:var(--sub); margin-top:2px; text-transform:uppercase; }

        .stat-grid {
          display:grid; grid-template-columns:1fr 1fr; gap:10px;
        }
        .stat-cell {
          background:var(--bg2); border-radius:10px;
          padding:14px 8px; text-align:center;
          border-bottom:3px solid transparent;
        }
        .stat-ico { font-size:22px; line-height:1.1; }
        .stat-val { font-size:12px; font-weight:700; line-height:1.2; margin-top:4px; }
        .stat-lbl { font-size:9px; color:var(--sub); text-transform:uppercase; letter-spacing:.4px; margin-top:2px; }

        .rooms-list { display:flex; flex-direction:column; gap:7px; }
        .room-row {
          display:flex; align-items:center; gap:8px;
          background:var(--bg2); border-radius:12px;
          padding:10px 10px; border-left:4px solid transparent;
        }
        .rr-left { flex-shrink:0; min-width:120px; }
        .rr-name { font-size:13px; font-weight:700; margin-bottom:3px; }
        .rr-pill {
          font-size:9px; font-weight:700; padding:2px 7px; border-radius:20px;
          text-transform:uppercase; letter-spacing:.4px; display:inline-block;
        }
        .rr-mold { display:inline-block; margin-top:3px; }
        @keyframes blink { 0%,100%{opacity:1}50%{opacity:.55} }

        .rr-metrics { display:flex; gap:5px; flex:1; }
        .rrm { background:var(--bg); border-radius:8px; padding:6px 8px; text-align:center; flex:1; }
        .rrm-v { font-size:13px; font-weight:700; line-height:1.1; }
        .rrm-l { font-size:8px; color:var(--sub); margin-top:1px; text-transform:uppercase; }

        .rr-sev { flex-shrink:0; text-align:center; min-width:36px; }
        .rr-sev-val { font-size:13px; font-weight:700; line-height:1; }
        .rr-bar-bg { height:3px; background:var(--div); border-radius:2px; overflow:hidden; margin-top:4px; }
        .rr-bar    { height:100%; border-radius:2px; transition:width .6s; }

        .trends-col { display:flex; flex-direction:column; gap:5px; }
        .trend-row {
          display:flex; align-items:center; justify-content:space-between;
          background:var(--bg2); border-radius:10px; padding:8px 10px;
        }
        .trend-row-left  { display:flex; align-items:center; gap:6px; }
        .trend-row-right { display:flex; align-items:center; gap:5px; }
        .trend-ico       { font-size:14px; flex-shrink:0; }
        .trend-row-lbl   { font-size:10px; font-weight:600; color:var(--sub); text-transform:uppercase; letter-spacing:.5px; }
        .trend-row-arrow { font-size:18px; font-weight:900; line-height:1; }
        .trend-row-txt   { font-size:10px; font-weight:700; }

        .win-list { display:flex; flex-direction:column; gap:4px; }
        .win-chip {
          font-size:11px; background:var(--bg2);
          border-left:2px solid #0ea5e9;
          padding:5px 8px; border-radius:7px;
        }
        .no-win {
          font-size:11px; color:var(--sub);
          background:var(--bg2); border-radius:8px;
          padding:8px 10px; text-align:center;
        }
      </style>
      <ha-card>
        <div class="card">
          <div class="card-title">${esc(title)}</div>
          <div class="cols">
            <div class="col">${col3}</div>
            <div class="col col-mid">${col2}</div>
            <div class="col">${col1}</div>
          </div>
        </div>
      </ha-card>`;

    try {
      this.shadowRoot.innerHTML = html;
    } catch (e) {
      console.error("[indeklima-tablet-card] Render failed:", e);
      this.shadowRoot.innerHTML = `
        <style>${baseCSS()}</style>
        <div style="color:#ef4444;padding:16px;border-radius:12px;background:var(--bg2);">
          <strong>Render-fejl:</strong> ${esc(e.message)}
        </div>`;
    }
  }

  getCardSize() { return 4; }
}

if (!customElements.get("indeklima-tablet-card")) {
  customElements.define("indeklima-tablet-card", IndeklimaTabletCard);
}


// ─────────────────────────────────────────────────────────────────────────────
// indeklima-room-detail-card (FIXED)
// ─────────────────────────────────────────────────────────────────────────────

class IndeklimaRoomDetailCard extends HTMLElement {

  static getStubConfig() { return { room: "Stue" }; }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._hass     = null;
    this._room     = null;
    this._climate  = null;
    this._config   = {};
    this._interval = null;
    this._errCount = 0;
    this._loadError = null;
  }

  setConfig(config) {
    if (!config.room) throw new Error("indeklima-room-detail-card: 'room' is required");
    this._config = config;
    this._render();
  }

  set hass(h) {
    const first = !this._hass;
    this._hass = h;
    if (first) this._load();
  }

  connectedCallback() {
    if (this._interval) clearInterval(this._interval);
    this._interval = setInterval(() => {
      if (this._errCount > 5) {
        clearInterval(this._interval);
        this._interval = null;
        return;
      }
      if (document.visibilityState === "visible") this._load();
    }, 30000);
  }

  disconnectedCallback() {
    if (this._interval) {
      clearInterval(this._interval);
      this._interval = null;
    }
  }

  async _load() {
    if (!this._hass) return;

    // FIXED: Load room and climate data separately for partial caching
    try {
      this._room = await this._hass.callWS({
        type: `${INDEKLIMA_DOMAIN}/get_room_data`,
        room_name: this._config.room,
      });
      this._loadError = null;
      this._errCount = 0;
    } catch (e) {
      this._errCount++;
      if (!this._room) {
        this._loadError = e?.message || String(e);
      }
    }

    // Load climate data separately - failure doesn't invalidate room data
    try {
      this._climate = await this._hass.callWS({
        type: `${INDEKLIMA_DOMAIN}/get_climate_data`
      });
    } catch (e) {
      console.warn("[indeklima-room-detail] Climate data failed:", e);
      // Don't fail completely if climate data fails
    }

    this._render();
  }

  _render() {
    const r       = this._room;
    const cl      = this._climate;
    const title   = this._config.title ?? (this._config.room ? esc(this._config.room) : "Rum");
    const compact = this._config.compact ?? false;

    const status  = r?.status || "good";
    const color   = statusColor(status);
    const sev     = r?.severity || 0;

    const trends  = cl?.trends  || {};
    const vent    = cl?.ventilation || {};
    const vColor  = ventColor(vent.status);

    const mold      = r?.mold_risk || "low";
    const mColor    = moldColor(mold);

    const metricCell = (icon, val, lbl, highlight) => `
      <div class="metric-cell" style="${highlight ? `border-bottom: 2px solid ${highlight};` : ""}">
        <div class="mc-icon">${icon}</div>
        <div class="mc-val">${val}</div>
        <div class="mc-lbl">${lbl}</div>
      </div>`;

    const metrics = r ? [
      (r?.temperature_sensors_count ?? 0) > 0
        ? metricCell("🌡️", fmtNum(r.temperature, "°C", 1), "Temperatur", "#0ea5e9") : "",
      (r?.humidity_sensors_count ?? 0) > 0
        ? metricCell("💧", fmtNum(r.humidity, "%"), "Fugtighed", color) : "",
      (r?.co2_sensors_count ?? 0) > 0
        ? metricCell("🌫️", fmtNum(r.co2, "ppm"), "CO₂", color) : "",
      (r?.pressure_sensors_count ?? 0) > 0
        ? metricCell("🧭", fmtNum(r.pressure, "hPa"), "Lufttryk", "#8b5cf6") : "",
    ].filter(Boolean).join("") : "";

    const sevPct = Math.min(100, sev);

    const winCount  = r?.outdoor_windows_open || 0;
    const doorCount = r?.internal_doors_open  || 0;
    const bonusActive = r?.air_circulation_bonus ?? false;

    const statusChips = [
      winCount  > 0 ? `<span class="chip chip-blue">🪟 ${winCount} vindue${winCount > 1 ? "r" : ""} åbent</span>` : "",
      doorCount > 0 ? `<span class="chip chip-blue">🚪 ${doorCount} dør${doorCount > 1 ? "e" : ""} åben</span>` : "",
      bonusActive    ? `<span class="chip chip-green">💨 Cirkulations-bonus aktiv</span>` : "",
      winCount === 0 && doorCount === 0
        ? `<span class="chip chip-sub">Ingen åbne vinduer eller døre</span>` : "",
    ].filter(Boolean).join("");

    const moldDesc =
      mold === "critical" ? "Fugtniveau er kritisk — skimmel vokser aktivt. Udluft straks og undersøg kolde flader."
      : mold === "high"   ? "Høj risiko for skimmelvækst. Reducer fugtighed hurtigst muligt."
      : mold === "moderate" ? "Moderat risiko. Hold øje med fugtighed og sørg for udluftning."
      : "Fugtindhold er på et sikkert niveau.";

    const html = `
      <style>
        :host { display:block; ${baseCSS()} font-family:var(--paper-font-body1_-_font-family,sans-serif); }

        .card {
          background:var(--bg); border-radius:18px; padding:16px 18px;
          color:var(--text); box-shadow:var(--ha-card-box-shadow,0 2px 8px rgba(0,0,0,.15));
          border-top: 3px solid ${color};
          background-image: linear-gradient(180deg, ${color}0d 0%, transparent 60px);
        }

        .header { display:flex; align-items:center; gap:14px; margin-bottom:14px; }
        .ring-wrap { position:relative; flex-shrink:0; }
        .ring-center {
          position:absolute; inset:0;
          display:flex; flex-direction:column; align-items:center; justify-content:center;
        }
        .ring-val  { font-weight:700; line-height:1; }
        .ring-unit { font-size:10px; color:var(--sub); }

        .header-info { flex:1; min-width:0; }
        .room-title { font-size:20px; font-weight:800; margin-bottom:5px; line-height:1.1; }
        .status-badge {
          display:inline-flex; align-items:center; gap:5px;
          padding:4px 12px; border-radius:20px;
          font-size:12px; font-weight:700;
          background:${color}1a; color:${color};
          ${status !== "good" ? "animation:bdot-pulse 2s infinite;" : ""}
        }
        .bdot { width:7px; height:7px; border-radius:50%; background:${color}; animation:bdot 2s infinite; }
        @keyframes bdot { 0%,100%{opacity:1}50%{opacity:.4} }
        @keyframes bdot-pulse { 0%,100%{box-shadow:0 0 0 0 ${color}40}50%{box-shadow:0 0 0 6px ${color}00} }
        .crit-since-row {
          font-size:11px; color:#ef4444; font-weight:600; margin:-4px 0 12px;
          display:inline-flex; align-items:center; gap:5px;
          background:#ef444414; border-radius:8px; padding:4px 10px;
          animation: crit-glow 3s ease-in-out infinite;
        }
        @keyframes blink { 0%,100%{opacity:1}50%{opacity:.55} }
        @keyframes led-fade { 0%,100%{opacity:1} 50%{opacity:.45} }
        @keyframes crit-glow { 0%,100%{opacity:1} 50%{opacity:.6} }
        .alarm-banner {
          display:flex; align-items:center; gap:8px;
          background:#ef444422; color:#ef4444; border-radius:10px;
          padding:8px 12px; font-size:12px; font-weight:700;
          margin-bottom:12px; animation: led-fade 2.4s ease-in-out infinite;
        }

        .sev-wrap { margin-bottom:14px; }
        .sev-label-row {
          display:flex; justify-content:space-between; align-items:center;
          margin-bottom:5px; font-size:11px; color:var(--sub);
        }
        .sev-score { font-size:13px; font-weight:700; color:${color}; }
        .sev-track {
          height:6px; border-radius:3px; background:var(--div);
          overflow:visible; position:relative;
        }
        .sev-fill {
          position:absolute; top:0; left:0; height:100%;
          width:${sevPct}%; background:${color};
          border-radius:3px; transition:width .6s;
          box-shadow:0 0 6px ${color}80;
        }
        .sev-marker {
          position:absolute; top:-3px;
          width:12px; height:12px; border-radius:50%;
          background:${color}; border:2px solid var(--bg);
          left:calc(${sevPct}% - 6px);
          transition:left .6s;
          box-shadow:0 0 4px ${color};
        }

        .divider { height:1px; background:var(--div); margin:12px 0; }
        .section-lbl {
          font-size:10px; font-weight:600; text-transform:uppercase;
          letter-spacing:1px; color:var(--sub); margin-bottom:8px;
        }

        .metrics-grid {
          display:grid;
          grid-template-columns:repeat(4, 1fr);
          gap:8px;
        }
        .metric-cell {
          background:var(--bg2); border-radius:12px;
          padding:10px 6px; text-align:center;
          transition:transform .15s;
        }
        .metric-cell:hover { transform:translateY(-2px); }
        .mc-icon { font-size:18px; margin-bottom:4px; }
        .mc-val  { font-size:15px; font-weight:800; line-height:1.1; }
        .mc-lbl  { font-size:8px; color:var(--sub); margin-top:3px; text-transform:uppercase; letter-spacing:.5px; }

        .trends-row { display:flex; gap:8px; }
        .trend-chip {
          flex:1; background:var(--bg2); border-radius:10px;
          padding:10px 8px; text-align:center;
        }
        .trend-header { font-size:9px; font-weight:700; color:var(--sub); text-transform:uppercase; letter-spacing:.8px; margin-bottom:6px; display:flex; align-items:center; justify-content:center; gap:4px; }
        .trend-arrow  { font-size:24px; font-weight:900; line-height:1; margin-bottom:4px; }
        .trend-label  { font-size:10px; font-weight:700; margin-top:2px; }

        .detail-status-grid {
          display:grid; grid-template-columns:1fr 1fr; gap:8px;
        }
        .ds-cell {
          background:var(--bg2); border-radius:12px;
          padding:12px; border-left:3px solid transparent;
        }
        .ds-full { grid-column:1 / -1; }
        .ds-header { display:flex; align-items:center; gap:8px; margin-bottom:4px; }
        .ds-icon   { font-size:20px; flex-shrink:0; }
        .ds-title  { font-size:14px; font-weight:700; line-height:1.2; }
        .ds-sub    { font-size:9px; font-weight:600; color:var(--sub); text-transform:uppercase; letter-spacing:.8px; margin-bottom:5px; }
        .ds-detail { font-size:11px; color:var(--sub); line-height:1.5; }
        .ds-reading{ font-size:10px; color:var(--sub); margin-top:4px; opacity:.7; }

        .chips-row { display:flex; flex-wrap:wrap; gap:6px; }
        .chip {
          font-size:11px; font-weight:500;
          padding:5px 10px; border-radius:20px;
          display:inline-flex; align-items:center; gap:5px;
        }
        .chip-blue  { background:#0ea5e91a; color:#0ea5e9; }
        .chip-green { background:#10b9811a; color:#10b981; }
        .chip-sub   { background:var(--bg2); color:var(--sub); }

        .loading { color:var(--sub); font-size:13px; padding:16px 0; text-align:center; }
        .load-error { padding:16px 0; text-align:center; }
        .err-icon  { font-size:28px; margin-bottom:8px; }
        .err-title { font-size:14px; font-weight:700; color:#ef4444; margin-bottom:4px; }
        .err-sub   { font-size:12px; color:var(--sub); margin-bottom:6px; line-height:1.5; }
        .err-sub code { background:var(--bg2); padding:2px 6px; border-radius:4px; color:var(--text); font-size:11px; }
        .err-detail { font-size:10px; color:var(--sub); opacity:.6; }
      </style>
      <ha-card>
        <div class="card">

          ${this._loadError && !r ? `
            <div class="load-error">
              <div class="err-icon">⚠️</div>
              <div class="err-title">Kunne ikke hente rum-data</div>
              <div class="err-sub">Tjek at rum-navnet matcher præcist:<br><code>${esc(this._config.room || "ukendt")}</code></div>
              <div class="err-detail">${esc(this._loadError)}</div>
            </div>
          ` : !r ? '<div class="loading">Henter data…</div>' : `

            <div class="header">
              ${severityRingHTML(sev, color, 88)}
              <div class="header-info">
                <div class="room-title">${esc(title)}</div>
                <div class="status-badge">
                  <span class="bdot"></span>
                  ${statusLabel(status)}
                </div>
              </div>
            </div>

            ${r.led_alarm_active ? `<div class="alarm-banner">🔴 LED alarm aktiv i dette rum</div>` : ""}
            ${status === "critical" && r.kritisk_siden ? `<div class="crit-since-row">⚠️ Kritisk siden ${fmtTimeSince(r.kritisk_siden)}</div>` : ""}

            <div class="sev-wrap">
              <div class="sev-label-row">
                <span>Alvorligheds-score</span>
                <span class="sev-score">${Math.round(sev)} / 100</span>
              </div>
              <div class="sev-track">
                <div class="sev-fill"></div>
                <div class="sev-marker"></div>
              </div>
            </div>

            <div class="section-lbl">Målinger</div>
            <div class="metrics-grid">${metrics || '<span style="color:var(--sub);font-size:12px;">Ingen sensorer konfigureret</span>'}</div>

            ${!compact ? `
              <div class="divider"></div>
              <div class="section-lbl">Tendenser (15 min)</div>
              <div class="trends-row">
                <div class="trend-chip">
                  <div class="trend-header">💧 Fugtighed</div>
                  <div class="trend-arrow" style="color:${trendColor(trends.humidity)}">${trendIcon(trends.humidity)}</div>
                  <div class="trend-label" style="color:${trendColor(trends.humidity)}">${trendLabel(trends.humidity)}</div>
                </div>
                <div class="trend-chip">
                  <div class="trend-header">🌫️ CO₂</div>
                  <div class="trend-arrow" style="color:${trendColor(trends.co2)}">${trendIcon(trends.co2)}</div>
                  <div class="trend-label" style="color:${trendColor(trends.co2)}">${trendLabel(trends.co2)}</div>
                </div>
                <div class="trend-chip">
                  <div class="trend-header">📊 Score</div>
                  <div class="trend-arrow" style="color:${trendColor(trends.severity)}">${trendIcon(trends.severity)}</div>
                  <div class="trend-label" style="color:${trendColor(trends.severity)}">${trendLabel(trends.severity)}</div>
                </div>
              </div>` : ""}

            <div class="divider"></div>
            <div class="section-lbl">Indeklima Status</div>
            <div class="detail-status-grid">

              <div class="ds-cell" style="border-left-color:${vColor}">
                <div class="ds-header">
                  <span class="ds-icon">${vent.status === "yes" ? "🌬️" : vent.status === "optional" ? "🤔" : "⏰"}</span>
                  <span class="ds-title" style="color:${vColor}">${ventLabel(vent.status)}</span>
                </div>
                <div class="ds-sub">Udluftning</div>
                <div class="ds-detail">${(vent.reason || []).join(", ") || "Indeklima er OK"}</div>
              </div>

              <div class="ds-cell" style="border-left-color:${mColor}">
                <div class="ds-header">
                  <span class="ds-icon">${moldIcon(mold)}</span>
                  <span class="ds-title" style="color:${mColor}">${mold==="low"?"Lav":mold==="moderate"?"Moderat":mold==="high"?"Høj":"Kritisk"}</span>
                </div>
                <div class="ds-sub">Skimmelrisiko</div>
                <div class="ds-detail">${moldDesc}</div>
                ${r.mold_humidity != null ? `<div class="ds-reading">Fugtsensor: ${r.mold_humidity.toFixed(1)} %</div>` : ""}
              </div>

              ${r.has_dehumidifier ? `
              <div class="ds-cell ds-full" style="border-left-color:${dehumColor(r.dehumidifier_recommendation||'no')}">
                <div class="ds-header">
                  <span class="ds-icon">${dehumIcon(r.dehumidifier_recommendation||'no') || '💧'}</span>
                  <span class="ds-title" style="color:${dehumColor(r.dehumidifier_recommendation||'no')}">${dehumLabel(r.dehumidifier_recommendation||'no')}</span>
                </div>
                <div class="ds-sub">Affugter${r.dehumidifier_mode && r.dehumidifier_mode !== 'off' ? ` · ${dehumModeLabel(r.dehumidifier_mode)}` : ''}</div>
                <div class="ds-detail">${r.dehumidifier_recommendation === 'yes' ? 'Fugt- eller skimmelrisiko er forhøjet — affugter anbefales.' : r.dehumidifier_recommendation === 'optional' ? 'Fugtniveauet er let forhøjet — overvej at tænde.' : 'Fugtindhold er på et sikkert niveau.'}</div>
              </div>` : ""}

            </div>

            ${!compact ? `
              <div class="divider"></div>
              <div class="section-lbl">Vinduer og døre</div>
              <div class="chips-row">${statusChips}</div>` : ""}

          `}
        </div>
      </ha-card>`;

    try {
      this.shadowRoot.innerHTML = html;
    } catch (e) {
      console.error("[indeklima-room-detail-card] Render failed:", e);
      this.shadowRoot.innerHTML = `
        <style>${baseCSS()}</style>
        <div style="color:#ef4444;padding:16px;border-radius:12px;background:var(--bg2);">
          <strong>Render-fejl:</strong> ${esc(e.message)}
        </div>`;
    }
  }

  getCardSize() { return this._config.compact ? 4 : 8; }
}

if (!customElements.get("indeklima-room-detail-card")) {
  customElements.define("indeklima-room-detail-card", IndeklimaRoomDetailCard);
}


// ─────────────────────────────────────────────────────────────────────────────
// Card Registration
// ─────────────────────────────────────────────────────────────────────────────

window.customCards = window.customCards || [];

if (!window.customCards.find(c => c.type === "indeklima-room-card")) {
  window.customCards.push({
    type:        "indeklima-room-card",
    name:        "Indeklima - Rum",
    description: "Live indeklimavisning for et rum - temperatur, fugt, CO2 og alvorlighed",
    preview:     true,
    documentationURL: "https://github.com/kingpainter/indeklima",
  });
}

if (!window.customCards.find(c => c.type === "indeklima-hub-card")) {
  window.customCards.push({
    type:        "indeklima-hub-card",
    name:        "Indeklima - Hus overblik (mobil)",
    description: "Komplet hus-overblik optimeret til mobil og portrait",
    preview:     true,
    documentationURL: "https://github.com/kingpainter/indeklima",
  });
}

if (!window.customCards.find(c => c.type === "indeklima-tablet-card")) {
  window.customCards.push({
    type:        "indeklima-tablet-card",
    name:        "Indeklima - Hus overblik (tablet/landscape)",
    description: "3-kolonne landscape-layout til tablet og desktop",
    preview:     true,
    documentationURL: "https://github.com/kingpainter/indeklima",
  });
}

if (!window.customCards.find(c => c.type === "indeklima-room-detail-card")) {
  window.customCards.push({
    type:        "indeklima-room-detail-card",
    name:        "Indeklima - Rum detaljer",
    description: "Detaljekort for ét rum: score, målinger, tendenser, udluftning, skimmelrisiko og vinduer",
    preview:     true,
    documentationURL: "https://github.com/kingpainter/indeklima",
  });
}
