"""Indeklima integration for Home Assistant.

Version: 2.5.2
"""
from __future__ import annotations

import logging
from datetime import timedelta, datetime
from typing import Any

from homeassistant.util import dt as dt_util

from homeassistant.config_entries import ConfigEntry, ConfigEntryNotReady
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.event import async_track_state_change_event, async_call_later
from homeassistant.core import Event, EventStateChangedData, callback as ha_callback

from .const import (
    normalize_room_id,
    DOMAIN,
    CONF_ROOMS,
    CONF_HUMIDITY_SENSORS,
    CONF_TEMPERATURE_SENSORS,
    CONF_CO2_SENSORS,
    CONF_VOC_SENSORS,
    CONF_FORMALDEHYDE_SENSORS,
    CONF_PRESSURE_SENSORS,
    CONF_MOLD_SENSORS,
    CONF_DEHUMIDIFIER,
    CONF_DEHUMIDIFIER_LED,
    CONF_DEHUMIDIFIER_BUTTON,
    CONF_DEHUMIDIFIER_ON_DURATION,
    DEFAULT_DEHUMIDIFIER_ON_DURATION,
    CONF_ROOM_LED_CRITICAL_SEVERITY,
    DEFAULT_LED_CRITICAL_SEVERITY,
    DEHUM_LED_BLINK_INTERVAL,
    DEHUM_LED_RECOVERY_CYCLES,
    CONF_QUIET_HOURS_START,
    CONF_QUIET_HOURS_END,
    CONF_ROOM_QUIET_HOURS_START,
    CONF_ROOM_QUIET_HOURS_END,
    DEFAULT_QUIET_HOURS_START,
    DEFAULT_QUIET_HOURS_END,
    DEHUM_MODE_MANUAL,
    DEHUM_MODE_AUTO,
    DEHUM_MODE_OFF,
    CONF_WINDOW_SENSORS,
    CONF_WINDOW_ENTITY,
    CONF_WINDOW_IS_OUTDOOR,
    CONF_WEATHER_ENTITY,
    CONF_HUMIDITY_SUMMER_MAX,
    CONF_HUMIDITY_WINTER_MAX,
    CONF_CO2_MAX,
    CONF_VOC_MAX,
    CONF_FORMALDEHYDE_MAX,
    CONF_MOLD_RISK_HUMIDITY,
    CONF_MOLD_RISK_TEMP_MIN,
    CONF_MOLD_RISK_TEMP_MAX,
    DEFAULT_HUMIDITY_SUMMER_MAX,
    DEFAULT_HUMIDITY_WINTER_MAX,
    DEFAULT_CO2_MAX,
    DEFAULT_VOC_MAX,
    DEFAULT_FORMALDEHYDE_MAX,
    DEFAULT_MOLD_RISK_HUMIDITY,
    DEFAULT_MOLD_RISK_TEMP_MIN,
    DEFAULT_MOLD_RISK_TEMP_MAX,
    MOLD_RISK_LOW,
    MOLD_RISK_MODERATE,
    MOLD_RISK_HIGH,
    MOLD_RISK_CRITICAL,
    DEHUMIDIFIER_YES,
    DEHUMIDIFIER_NO,
    DEHUMIDIFIER_OPTIONAL,
    SCAN_INTERVAL,
    TREND_WINDOW,
    STATUS_GOOD,
    STATUS_WARNING,
    STATUS_CRITICAL,
    SEASON_SUMMER,
    SEASON_WINTER,
    TREND_RISING,
    TREND_FALLING,
    TREND_STABLE,
    VENTILATION_YES,
    VENTILATION_NO,
    VENTILATION_OPTIONAL,
    CIRCULATION_GOOD,
    CIRCULATION_MODERATE,
    CIRCULATION_POOR,
    CIRCULATION_BONUS,
    __version__,
)
from .panel import async_register_panel, async_unregister_panel, async_unregister_cards_resource
from .websocket import async_register_websocket_commands
from .repairs import (
    raise_coordinator_failed_issue,
    clear_coordinator_failed_issue,
    raise_sensor_unavailable_issue,
    clear_sensor_unavailable_issue,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Indeklima from a config entry."""
    coordinator = IndeklimaDataCoordinator(hass, entry)

    # Attempt first refresh but do not block setup if sensors are temporarily
    # unavailable (e.g. right after an HA restart). Sensors will be picked up
    # on the next 30-second poll cycle instead.
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning(
            "Indeklima first refresh incomplete — sensors may be unavailable at boot "
            "(will retry in %s seconds): %s",
            SCAN_INTERVAL,
            err,
        )

    # Modern HA pattern: use entry.runtime_data instead of hass.data
    entry.runtime_data = coordinator

    # Keep hass.data for backwards compatibility with websocket/diagnostics helpers
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register devices
    device_registry = dr.async_get(hass)

    # Register hub device
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, f"{entry.entry_id}_hub")},
        name="Indeklima Hub",
        manufacturer="Indeklima",
        model="Climate Monitor v2",
        sw_version=__version__,
    )

    # Register room devices
    for room in coordinator.rooms:
        room_name = room.get("name")
        room_id = normalize_room_id(room_name)

        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, f"{entry.entry_id}_room_{room_id}")},
            name=f"Indeklima {room_name}",
            manufacturer="Indeklima",
            model="Room Monitor",
            sw_version=__version__,
            via_device=(DOMAIN, f"{entry.entry_id}_hub"),
        )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # ── Register panel and WebSocket API (v2.4.0) ──────────────────────────
    async_register_websocket_commands(hass)
    await async_register_panel(hass)

    # Register dehumidifier button listeners
    coordinator.async_setup_dehumidifier_listeners()

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _LOGGER.info("Indeklima integration v%s setup completed", __version__)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # ── Unregister panel and cards resource (v2.4.0) ───────────────────────
    async_unregister_panel(hass)
    await async_unregister_cards_resource(hass)

    # Cancel dehumidifier button listeners and pending timers
    coordinator = entry.runtime_data
    if coordinator is not None:
        coordinator.async_unload_dehumidifier_listeners()

    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


class IndeklimaDataCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Indeklima data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.hass = hass
        self.entry = entry
        self.rooms = entry.data.get(CONF_ROOMS, [])

        # Get thresholds from options
        self.humidity_summer_max = entry.options.get(
            CONF_HUMIDITY_SUMMER_MAX, DEFAULT_HUMIDITY_SUMMER_MAX
        )
        self.humidity_winter_max = entry.options.get(
            CONF_HUMIDITY_WINTER_MAX, DEFAULT_HUMIDITY_WINTER_MAX
        )
        self.co2_max = entry.options.get(CONF_CO2_MAX, DEFAULT_CO2_MAX)
        self.voc_max = entry.options.get(CONF_VOC_MAX, DEFAULT_VOC_MAX)
        self.formaldehyde_max = entry.options.get(
            CONF_FORMALDEHYDE_MAX, DEFAULT_FORMALDEHYDE_MAX
        )

        # Mold risk thresholds
        self.mold_risk_humidity = entry.options.get(
            CONF_MOLD_RISK_HUMIDITY, DEFAULT_MOLD_RISK_HUMIDITY
        )
        self.mold_risk_temp_min = entry.options.get(
            CONF_MOLD_RISK_TEMP_MIN, DEFAULT_MOLD_RISK_TEMP_MIN
        )
        self.mold_risk_temp_max = entry.options.get(
            CONF_MOLD_RISK_TEMP_MAX, DEFAULT_MOLD_RISK_TEMP_MAX
        )

        # Weather entity
        self.weather_entity = entry.options.get(CONF_WEATHER_ENTITY)

        # Quiet hours (hub-level default; rooms may override via
        # CONF_ROOM_QUIET_HOURS_START/END on the room dict)
        self.quiet_hours_start = entry.options.get(
            CONF_QUIET_HOURS_START, DEFAULT_QUIET_HOURS_START
        )
        self.quiet_hours_end = entry.options.get(
            CONF_QUIET_HOURS_END, DEFAULT_QUIET_HOURS_END
        )

        # Dehumidifier control state per room: {room_name: {"mode": ..., "unsub_timer": ...}}
        self._dehumidifier_state: dict[str, dict] = {}
        self._button_unsubs: list = []

        # LED critical-alarm blink timers per room: {room_name: unsub_callable}
        self._led_blink_unsubs: dict[str, Any] = {}

        # Critical-status start timestamp per room (independent of LED/dehumidifier
        # config -- tracks the room's own severity status for any room)
        self._room_critical_since: dict[str, datetime | None] = {}

        # History for trends
        self.history: dict[str, list[tuple[datetime, float]]] = {
            "humidity": [],
            "co2": [],
            "severity": [],
        }

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SCAN_INTERVAL),
        )

    def _get_season(self) -> str:
        """Determine current season."""
        month = dt_util.now().month
        if 5 <= month <= 9:
            return SEASON_SUMMER
        return SEASON_WINTER

    def _get_humidity_max(self) -> float:
        """Get max humidity based on season."""
        season = self._get_season()
        if season == SEASON_SUMMER:
            return self.humidity_summer_max
        return self.humidity_winter_max

    def _get_sensor_values(self, entity_ids: list[str], room_name: str = "") -> list[float]:
        """Get numeric values from multiple sensors."""
        values = []
        for entity_id in entity_ids:
            if not entity_id:
                continue
            state = self.hass.states.get(entity_id)
            if state and state.state not in ("unknown", "unavailable"):
                try:
                    values.append(float(state.state))
                    # Clear any existing repair issue for this sensor
                    if room_name:
                        clear_sensor_unavailable_issue(
                            self.hass, self.entry.entry_id, entity_id
                        )
                except (ValueError, TypeError):
                    pass
            else:
                # Sensor is unavailable — raise a repair issue
                if room_name:
                    raise_sensor_unavailable_issue(
                        self.hass, self.entry.entry_id, room_name, entity_id
                    )
        return values

    def _calculate_mold_risk(self, humidity: float | None, temperature: float | None) -> str:
        """Calculate mold risk level from humidity and temperature.

        Mold growth is favoured when:
          - Relative humidity is sustained above ~70 %
          - Temperature is between 5 °C and 35 °C

        Returns one of: MOLD_RISK_LOW / MODERATE / HIGH / CRITICAL.
        """
        if humidity is None:
            return MOLD_RISK_LOW

        temp_in_range = True
        if temperature is not None:
            temp_in_range = self.mold_risk_temp_min <= temperature <= self.mold_risk_temp_max

        if not temp_in_range:
            return MOLD_RISK_LOW

        if humidity >= self.mold_risk_humidity + 15:   # ≥85 %
            return MOLD_RISK_CRITICAL
        elif humidity >= self.mold_risk_humidity + 5:  # ≥75 %
            return MOLD_RISK_HIGH
        elif humidity >= self.mold_risk_humidity:       # ≥70 %
            return MOLD_RISK_MODERATE
        return MOLD_RISK_LOW

    def _calculate_severity(self, room_data: dict) -> float:
        """Calculate severity score for a room (0-100, lower is better)."""
        severity = 0.0
        humidity_max = self._get_humidity_max()

        # Humidity severity (0-30 points)
        if "humidity" in room_data:
            humidity = room_data["humidity"]
            if humidity > humidity_max:
                excess = humidity - humidity_max
                severity += min(30, excess * 3)

        # CO2 severity (0-30 points)
        if "co2" in room_data:
            co2 = room_data["co2"]
            if co2 > self.co2_max:
                excess = co2 - self.co2_max
                severity += min(30, (excess / 1000) * 30)

        # VOC severity (0-20 points)
        if "voc" in room_data:
            voc = room_data["voc"]
            if voc > self.voc_max:
                excess = voc - self.voc_max
                severity += min(20, excess * 5)

        # Formaldehyde severity (0-20 points)
        if "formaldehyde" in room_data:
            formaldehyde = room_data["formaldehyde"]
            if formaldehyde > self.formaldehyde_max:
                excess = formaldehyde - self.formaldehyde_max
                severity += min(20, excess * 50)

        # Note: Pressure does NOT affect severity scoring.
        # It is informational only (barometric pressure is not an indoor
        # climate quality metric that users can control).

        return min(100, severity)

    def _get_status_from_severity(self, severity: float) -> str:
        """Convert severity score to status."""
        if severity < 30:
            return STATUS_GOOD
        elif severity < 60:
            return STATUS_WARNING
        return STATUS_CRITICAL

    def _calculate_trend(self, key: str, current_value: float) -> str:
        """Calculate trend for a metric."""
        now = dt_util.utcnow()

        # Add current value to history
        self.history[key].append((now, current_value))

        # Remove old entries (older than TREND_WINDOW)
        cutoff = now - timedelta(seconds=TREND_WINDOW)
        self.history[key] = [
            (ts, val) for ts, val in self.history[key] if ts > cutoff
        ]

        # Need at least 2 data points
        if len(self.history[key]) < 2:
            return TREND_STABLE

        # Calculate linear regression slope
        timestamps = [(ts - now).total_seconds() for ts, _ in self.history[key]]
        values = [val for _, val in self.history[key]]

        n = len(timestamps)
        sum_x = sum(timestamps)
        sum_y = sum(values)
        sum_xy = sum(x * y for x, y in zip(timestamps, values))
        sum_xx = sum(x * x for x in timestamps)

        denominator = n * sum_xx - sum_x * sum_x
        if denominator == 0:
            return TREND_STABLE

        slope = (n * sum_xy - sum_x * sum_y) / denominator

        # Determine trend based on slope
        threshold = 0.1
        if slope > threshold:
            return TREND_RISING
        elif slope < -threshold:
            return TREND_FALLING
        return TREND_STABLE

    def _get_weather_data(self) -> dict[str, float]:
        """Get weather data for ventilation recommendation.

        Tries multiple attribute keys to support different HA weather integrations.
        Standard weather entities use 'temperature' and 'humidity'.
        Some integrations also expose 'current_temperature'.
        """
        weather_data = {}

        if not self.weather_entity:
            return weather_data

        state = self.hass.states.get(self.weather_entity)
        if not state or state.state in ("unknown", "unavailable"):
            return weather_data

        attrs = state.attributes

        # Temperature — try multiple keys
        for temp_key in ("temperature", "current_temperature"):
            val = attrs.get(temp_key)
            if val is not None:
                try:
                    weather_data["temperature"] = float(val)
                    break
                except (ValueError, TypeError):
                    pass

        # Humidity — try multiple keys
        for hum_key in ("humidity", "current_humidity"):
            val = attrs.get(hum_key)
            if val is not None:
                try:
                    weather_data["humidity"] = float(val)
                    break
                except (ValueError, TypeError):
                    pass

        return weather_data

    def _get_quiet_hours(self, room: dict) -> tuple[int, int]:
        """Get the (start, end) quiet hours for a room.

        Falls back to the hub-level default if the room has no override.
        """
        start = room.get(CONF_ROOM_QUIET_HOURS_START, self.quiet_hours_start)
        end = room.get(CONF_ROOM_QUIET_HOURS_END, self.quiet_hours_end)
        return start, end

    def _is_quiet_hours(self, room: dict) -> bool:
        """Check whether it is currently quiet hours for a room."""
        start, end = self._get_quiet_hours(room)
        hour = dt_util.now().hour
        return hour >= start or hour < end

    def _calculate_dehumidifier_recommendation(self, room_data: dict, room: dict) -> str:
        """Calculate dehumidifier recommendation for a single room.

        Returns DEHUMIDIFIER_YES / NO / OPTIONAL based on:
        - mold_risk (high/critical  → yes)
        - humidity trend + level    → yes if rising above threshold
        - outdoor windows open      → no (natural ventilation preferred)
        - quiet hours suppression   → no if mold_risk is low and it is quiet hours
        """
        humidity = room_data.get("humidity")
        mold_risk = room_data.get("mold_risk", MOLD_RISK_LOW)
        outdoor_open = room_data.get("outdoor_windows_open", 0)
        humidity_max = self._get_humidity_max()

        # If outdoor windows are open, natural ventilation is already happening
        if outdoor_open > 0:
            return DEHUMIDIFIER_NO

        # Mold risk is high or critical — always recommend dehumidifier
        if mold_risk in (MOLD_RISK_HIGH, MOLD_RISK_CRITICAL):
            return DEHUMIDIFIER_YES

        # Quiet hours suppression (configurable, default 23:00–06:00), only
        # suppress when mold_risk is low
        if self._is_quiet_hours(room) and mold_risk == MOLD_RISK_LOW:
            return DEHUMIDIFIER_NO

        # Humidity is above threshold
        if humidity is not None and humidity > humidity_max:
            # Moderate mold risk on top of high humidity → definite yes
            if mold_risk == MOLD_RISK_MODERATE:
                return DEHUMIDIFIER_YES
            # Humidity above threshold but mold risk low → optional
            return DEHUMIDIFIER_OPTIONAL

        # Moderate mold risk even without humidity breach → optional
        if mold_risk == MOLD_RISK_MODERATE:
            return DEHUMIDIFIER_OPTIONAL

        return DEHUMIDIFIER_NO

    def _calculate_ventilation_recommendation(self, data: dict) -> dict:
        """Calculate ventilation recommendation."""
        recommendation = {
            "status": VENTILATION_NO,
            "reason": [],
            "rooms": [],
            "outdoor_temp": None,
            "outdoor_humidity": None,
        }

        # Check if any outdoor windows are open
        if data.get("open_windows"):
            recommendation["status"] = VENTILATION_OPTIONAL
            recommendation["reason"].append("Vinduer allerede \u00e5bne")
            return recommendation

        # Analyze indoor climate issues
        issues = []
        problem_rooms = []

        humidity_max = self._get_humidity_max()

        for room_name, room_data in data.get("rooms", {}).items():
            room_issues = []

            if "humidity" in room_data and room_data["humidity"] > humidity_max:
                room_issues.append("H\u00f8j fugtighed")

            if "co2" in room_data and room_data["co2"] > self.co2_max:
                room_issues.append("H\u00f8j CO2")

            if "voc" in room_data and room_data["voc"] > self.voc_max:
                room_issues.append("H\u00f8j VOC")

            if room_issues:
                issues.extend(room_issues)
                problem_rooms.append(room_name)

        # Always fetch weather data so outdoor conditions are shown in panel
        # regardless of whether there are indoor issues or not
        weather = self._get_weather_data()
        if weather:
            recommendation["outdoor_temp"] = weather.get("temperature")
            recommendation["outdoor_humidity"] = weather.get("humidity")

        if not issues:
            recommendation["status"] = VENTILATION_NO
            recommendation["reason"].append("Indeklima er OK")
            return recommendation

        # There are indoor issues — now decide whether to recommend ventilation
        temp     = weather.get("temperature", 20) if weather else 20
        humidity = weather.get("humidity",    50) if weather else 50

        if weather:
            if temp < 5:
                recommendation["status"] = VENTILATION_OPTIONAL
                recommendation["reason"].extend(issues)
                recommendation["reason"].append("For koldt ude")
            elif humidity > humidity_max:
                recommendation["status"] = VENTILATION_NO
                recommendation["reason"].extend(issues)
                recommendation["reason"].append("For fugtigt ude")
            else:
                recommendation["status"] = VENTILATION_YES
                recommendation["reason"].extend(issues)
        else:
            # No weather data — recommend based on indoor issues only
            recommendation["status"] = VENTILATION_YES
            recommendation["reason"].extend(issues)

        recommendation["rooms"] = problem_rooms
        return recommendation

    def _calculate_air_circulation(self, total_internal_doors: int) -> str:
        """Calculate air circulation status based on open internal doors."""
        if total_internal_doors >= 3:
            return CIRCULATION_GOOD
        elif total_internal_doors >= 1:
            return CIRCULATION_MODERATE
        return CIRCULATION_POOR

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from sensors."""
        try:
            result = await self._async_do_update()
            # Clear coordinator-failed issue on successful update
            clear_coordinator_failed_issue(self.hass, self.entry.entry_id)
            return result
        except UpdateFailed:
            raise
        except Exception as err:
            raise_coordinator_failed_issue(self.hass, self.entry.entry_id, str(err))
            raise UpdateFailed(f"Unexpected error: {err}") from err

    # ── Module-level lookup tables (defined once, not per call) ─────────────
    _MOLD_SCORE: dict[str, int] = {
        "low": 0,
        "moderate": 1,
        "high": 2,
        "critical": 3,
    }
    _MOLD_FROM_SCORE: list[str] = ["low", "moderate", "high", "critical"]
    _DEHUM_SCORE: dict[str, int] = {"no": 0, "optional": 1, "yes": 2}
    _DEHUM_FROM_SCORE: list[str] = ["no", "optional", "yes"]

    async def _async_do_update(self) -> dict[str, Any]:
        """Internal update implementation."""
        data = {
            "rooms": {},
            "averages": {},
            "severity": 0,
            "status": STATUS_GOOD,
            "open_windows": [],
            "open_internal_doors": [],
            "air_circulation": CIRCULATION_POOR,
            "trends": {},
            "ventilation": {},
        }

        all_humidity: list[float] = []
        all_temperature: list[float] = []
        all_co2: list[float] = []
        all_voc: list[float] = []
        all_formaldehyde: list[float] = []
        all_pressure: list[float] = []
        all_severity: list[float] = []
        all_mold_risk_scores: list[int] = []

        total_outdoor_windows_open = 0
        total_internal_doors_open = 0

        # Process each room
        for room in self.rooms:
            room_name = room.get("name")
            try:
                room_data = self._process_room(room, data)
            except Exception as err:  # noqa: BLE001
                _LOGGER.warning(
                    "Indeklima: error processing room '%s' — skipping: %s",
                    room_name,
                    err,
                )
                continue

            all_severity.append(room_data.get("severity", 0.0))
            if "humidity" in room_data:
                all_humidity.append(room_data["humidity"])
            if "temperature" in room_data:
                all_temperature.append(room_data["temperature"])
            if "co2" in room_data:
                all_co2.append(room_data["co2"])
            if "voc" in room_data:
                all_voc.append(room_data["voc"])
            if "formaldehyde" in room_data:
                all_formaldehyde.append(room_data["formaldehyde"])
            if "pressure" in room_data:
                all_pressure.append(room_data["pressure"])
            all_mold_risk_scores.append(
                self._MOLD_SCORE.get(room_data.get("mold_risk", MOLD_RISK_LOW), 0)
            )
            total_outdoor_windows_open += room_data.get("outdoor_windows_open", 0)
            total_internal_doors_open += room_data.get("internal_doors_open", 0)
            data["rooms"][room_name] = room_data


        # Calculate global averages
        def _avg(lst: list[float]) -> float:
            return sum(lst) / len(lst)

        if all_humidity:
            data["averages"]["humidity"] = _avg(all_humidity)
        if all_temperature:
            data["averages"]["temperature"] = _avg(all_temperature)
        if all_co2:
            data["averages"]["co2"] = _avg(all_co2)
        if all_voc:
            data["averages"]["voc"] = _avg(all_voc)
        if all_formaldehyde:
            data["averages"]["formaldehyde"] = _avg(all_formaldehyde)
        if all_pressure:
            data["averages"]["pressure"] = _avg(all_pressure)

        # Calculate global severity
        if all_severity:
            global_severity = sum(all_severity) / len(all_severity)

            # Apply air circulation bonus
            if total_internal_doors_open > 0:
                global_severity *= CIRCULATION_BONUS  # 5% reduction

            data["severity"] = round(global_severity, 1)
            data["status"] = self._get_status_from_severity(global_severity)

        # Calculate air circulation
        data["air_circulation"] = self._calculate_air_circulation(total_internal_doors_open)

        # Calculate global mold risk (worst-room level)
        if all_mold_risk_scores:
            data["mold_risk"] = self._MOLD_FROM_SCORE[max(all_mold_risk_scores)]
        else:
            data["mold_risk"] = MOLD_RISK_LOW

        # Calculate global dehumidifier recommendation (worst-room: yes > optional > no)
        dehum_scores = [
            self._DEHUM_SCORE.get(r.get("dehumidifier_recommendation", DEHUMIDIFIER_NO), 0)
            for r in data["rooms"].values()
        ]
        data["dehumidifier_recommendation"] = (
            self._DEHUM_FROM_SCORE[max(dehum_scores)] if dehum_scores else DEHUMIDIFIER_NO
        )

        # Calculate trends
        if all_humidity:
            data["trends"]["humidity"] = self._calculate_trend(
                "humidity", sum(all_humidity) / len(all_humidity)
            )
        if all_co2:
            data["trends"]["co2"] = self._calculate_trend(
                "co2", sum(all_co2) / len(all_co2)
            )
        if all_severity:
            data["trends"]["severity"] = self._calculate_trend(
                "severity", data["severity"]
            )

        # Calculate ventilation recommendation
        data["ventilation"] = self._calculate_ventilation_recommendation(data)

        return data

    def _process_room(self, room: dict, data: dict) -> dict[str, Any]:
        """Process a single room and return its room_data dict.

        Isolated so a bad sensor in one room cannot abort the full update cycle.
        """
        room_name = room.get("name")
        room_data: dict[str, Any] = {}

        # ── Scalar sensor groups ─────────────────────────────────────────────
        for conf_key, data_key in (
            (CONF_HUMIDITY_SENSORS, "humidity"),
            (CONF_TEMPERATURE_SENSORS, "temperature"),
            (CONF_CO2_SENSORS, "co2"),
            (CONF_VOC_SENSORS, "voc"),
            (CONF_FORMALDEHYDE_SENSORS, "formaldehyde"),
            (CONF_PRESSURE_SENSORS, "pressure"),
        ):
            if sensors := room.get(conf_key):
                values = self._get_sensor_values(sensors, room_name)
                if values:
                    room_data[data_key] = sum(values) / len(values)
                    room_data[f"{data_key}_sensors_count"] = len(values)

        # ── Dedicated mold sensors (optional) ─────────────────────────────────
        if mold_sensors := room.get(CONF_MOLD_SENSORS):
            values = self._get_sensor_values(mold_sensors, room_name)
            if values:
                room_data["mold_humidity"] = sum(values) / len(values)
                room_data["mold_sensors_count"] = len(values)

        mold_humidity = room_data.get("mold_humidity", room_data.get("humidity"))
        room_data["mold_risk"] = self._calculate_mold_risk(
            mold_humidity, room_data.get("temperature")
        )

        # ── Window / door sensors ─────────────────────────────────────────────
        room_outdoor_open = 0
        room_internal_open = 0
        for window in room.get(CONF_WINDOW_SENSORS, []):
            if isinstance(window, str):
                entity_id = window
                is_outdoor = True
            elif isinstance(window, dict):
                entity_id = window.get(CONF_WINDOW_ENTITY)
                is_outdoor = window.get(CONF_WINDOW_IS_OUTDOOR, True)
            else:
                continue
            if not entity_id:
                continue
            state = self.hass.states.get(entity_id)
            if state and state.state == "on":
                if is_outdoor:
                    room_outdoor_open += 1
                    if room_name not in data["open_windows"]:
                        data["open_windows"].append(room_name)
                else:
                    room_internal_open += 1
                    if room_name not in data["open_internal_doors"]:
                        data["open_internal_doors"].append(room_name)
        room_data["outdoor_windows_open"] = room_outdoor_open
        room_data["internal_doors_open"] = room_internal_open

        # ── Severity & status ─────────────────────────────────────────────────
        severity = self._calculate_severity(room_data)
        room_data["severity"] = severity
        room_data["status"] = self._get_status_from_severity(severity)

        # ── Critical-status timestamp tracking (ALL rooms, independent of LED) ──
        # Reflects the room's true, real-time severity status -- no hysteresis.
        if room_data["status"] == STATUS_CRITICAL:
            if self._room_critical_since.get(room_name) is None:
                self._room_critical_since[room_name] = dt_util.utcnow()
            room_data["kritisk_siden"] = self._room_critical_since[room_name].isoformat()
        else:
            self._room_critical_since[room_name] = None

        # ── Dehumidifier recommendation ───────────────────────────────────────
        has_dehumidifier = bool(room.get(CONF_DEHUMIDIFIER))
        room_data["has_dehumidifier"] = has_dehumidifier
        room_data["dehumidifier_recommendation"] = (
            self._calculate_dehumidifier_recommendation(room_data, room)
            if has_dehumidifier
            else DEHUMIDIFIER_NO
        )

        # ── Dehumidifier auto-control (actual switch on/off) ────────────────────
        if has_dehumidifier:
            self._maybe_auto_control_dehumidifier(room, room_data)
        room_data["dehumidifier_mode"] = self._dehumidifier_state.get(
            room_name, {}
        ).get("mode", DEHUM_MODE_OFF)

        # ── LED critical-alert refresh (every cycle, independent of mode changes) ──
        # A blinking RED alarm always overrides the manual/auto colour. Hysteresis
        # (DEHUM_LED_RECOVERY_CYCLES consecutive non-critical cycles) prevents
        # flicker right around the threshold. The threshold is per-room
        # configurable via CONF_ROOM_LED_CRITICAL_SEVERITY -- LED-only, does NOT
        # affect the room's official status/severity classification.
        led_entity = room.get(CONF_DEHUMIDIFIER_LED)
        if led_entity:
            state_entry = self._dehumidifier_state.setdefault(
                room_name, {"mode": DEHUM_MODE_OFF, "unsub_timer": None}
            )
            led_threshold = room.get(
                CONF_ROOM_LED_CRITICAL_SEVERITY, DEFAULT_LED_CRITICAL_SEVERITY
            )
            is_led_critical = room_data["severity"] >= led_threshold

            if is_led_critical:
                state_entry["recovery_count"] = 0
                if not state_entry.get("led_alarm_active"):
                    state_entry["led_alarm_active"] = True
                    state_entry["led_color"] = "red"
                    self._async_start_led_alarm_blink(room)
            elif state_entry.get("led_alarm_active"):
                state_entry["recovery_count"] = state_entry.get("recovery_count", 0) + 1
                if state_entry["recovery_count"] >= DEHUM_LED_RECOVERY_CYCLES:
                    state_entry["led_alarm_active"] = False
                    state_entry["recovery_count"] = 0
                    self._async_stop_led_alarm_blink(room_name)
                    current_mode = state_entry.get("mode", DEHUM_MODE_OFF)
                    desired_color = self._mode_to_led_color(current_mode)
                    self._async_apply_led_color(room, desired_color)
                    state_entry["led_color"] = desired_color
                # else: still within the hysteresis window -- keep blinking
            else:
                # Not in alarm and not critical -- normal mode-colour refresh
                current_mode = state_entry.get("mode", DEHUM_MODE_OFF)
                desired_color = self._mode_to_led_color(current_mode)
                if state_entry.get("led_color") != desired_color:
                    self._async_apply_led_color(room, desired_color)
                    state_entry["led_color"] = desired_color

            # Expose alarm state on room_data so the frontend can mirror it
            # (the physical LED itself is not visible remotely)
            room_data["led_alarm_active"] = state_entry.get("led_alarm_active", False)

        return room_data

    # ── Dehumidifier control: auto cycle, manual button, LED feedback ───────

    def _maybe_auto_control_dehumidifier(self, room: dict, room_data: dict) -> None:
        """Automatically start the dehumidifier if recommended.

        Never overrides an active manual session, and never auto-starts
        during quiet hours (already handled by the recommendation itself
        returning NO, but this keeps the control path explicit).
        """
        room_name = room.get("name")
        current = self._dehumidifier_state.get(room_name, {"mode": DEHUM_MODE_OFF})

        if current.get("mode") == DEHUM_MODE_MANUAL:
            return

        recommendation = room_data.get("dehumidifier_recommendation", DEHUMIDIFIER_NO)
        if recommendation == DEHUMIDIFIER_YES and current.get("mode") != DEHUM_MODE_AUTO:
            self.hass.async_create_task(
                self._async_start_dehumidifier(room, DEHUM_MODE_AUTO)
            )

    def async_setup_dehumidifier_listeners(self) -> None:
        """Register state-change listeners for configured button entities."""
        for room in self.rooms:
            button_entity = room.get(CONF_DEHUMIDIFIER_BUTTON)
            if not button_entity:
                continue
            unsub = async_track_state_change_event(
                self.hass, [button_entity], self._make_button_handler(room)
            )
            self._button_unsubs.append(unsub)

    def async_unload_dehumidifier_listeners(self) -> None:
        """Cancel all button listeners, pending auto-off timers, and LED blink timers."""
        for unsub in self._button_unsubs:
            unsub()
        self._button_unsubs = []

        for state in self._dehumidifier_state.values():
            if state.get("unsub_timer"):
                state["unsub_timer"]()

        for unsub in self._led_blink_unsubs.values():
            unsub()
        self._led_blink_unsubs = {}

    def _make_button_handler(self, room: dict):
        """Build a state-change callback bound to a specific room."""

        @ha_callback
        def _handler(event: Event[EventStateChangedData]) -> None:
            self.hass.async_create_task(self._async_handle_button_press(room))

        return _handler

    async def _async_handle_button_press(self, room: dict) -> None:
        """Handle a physical button press/click: toggle the dehumidifier.

        Any state change on the configured button entity counts as a click —
        this supports both real button/event entities and click-count
        sensors that reset to null/unknown after each press.
        """
        switch_entity = room.get(CONF_DEHUMIDIFIER)
        if not switch_entity:
            return

        state = self.hass.states.get(switch_entity)
        is_on = bool(state and state.state == "on")

        if is_on:
            await self._async_stop_dehumidifier(room)
        else:
            await self._async_start_dehumidifier(room, DEHUM_MODE_MANUAL)

    async def _async_start_dehumidifier(self, room: dict, mode: str) -> None:
        """Turn the dehumidifier switch on, (re)start the auto-off timer, and update the LED."""
        switch_entity = room.get(CONF_DEHUMIDIFIER)
        if not switch_entity:
            return
        room_name = room.get("name")

        domain = switch_entity.split(".")[0]
        await self.hass.services.async_call(
            domain, "turn_on", {"entity_id": switch_entity}, blocking=False
        )

        # Cancel any existing timer before starting a new one
        existing = self._dehumidifier_state.get(room_name, {})
        if existing.get("unsub_timer"):
            existing["unsub_timer"]()

        duration_minutes = room.get(
            CONF_DEHUMIDIFIER_ON_DURATION, DEFAULT_DEHUMIDIFIER_ON_DURATION
        )

        @ha_callback
        def _on_timer_finished(_now) -> None:
            self.hass.async_create_task(self._async_stop_dehumidifier(room))

        unsub_timer = async_call_later(
            self.hass, duration_minutes * 60, _on_timer_finished
        )

        self._dehumidifier_state[room_name] = {"mode": mode, "unsub_timer": unsub_timer}
        self._async_set_led(room, mode)

    async def _async_stop_dehumidifier(self, room: dict) -> None:
        """Turn the dehumidifier switch off, cancel any timer, and update the LED."""
        switch_entity = room.get(CONF_DEHUMIDIFIER)
        room_name = room.get("name")

        existing = self._dehumidifier_state.get(room_name, {})
        if existing.get("unsub_timer"):
            existing["unsub_timer"]()

        if switch_entity:
            state = self.hass.states.get(switch_entity)
            if state and state.state == "on":
                domain = switch_entity.split(".")[0]
                await self.hass.services.async_call(
                    domain, "turn_off", {"entity_id": switch_entity}, blocking=False
                )

        self._dehumidifier_state[room_name] = {"mode": DEHUM_MODE_OFF, "unsub_timer": None}
        self._async_set_led(room, DEHUM_MODE_OFF)

    # ── LED colour mapping ───────────────────────────────────────────────────
    _LED_COLORS: dict[str, dict] = {
        "blue": {"rgb_color": [0, 100, 255], "brightness_pct": 76},
        "yellow": {"rgb_color": [255, 255, 133], "brightness_pct": 76},
        "red": {"rgb_color": [255, 0, 0], "brightness_pct": 100},
    }

    def _mode_to_led_color(self, mode: str) -> str:
        """Map a dehumidifier control mode to its base LED colour (before alarm override)."""
        if mode == DEHUM_MODE_MANUAL:
            return "blue"
        if mode == DEHUM_MODE_AUTO:
            return "yellow"
        return "off"

    def _async_set_led(self, room: dict, mode: str) -> None:
        """Update the configured LED entity to reflect manual/auto/off state.

        If a critical-alert blink is currently active for this room, the alarm
        always takes priority: this call only updates the stored control mode
        and leaves the LED itself alone (the blink timer owns it until the
        hysteresis window clears the alarm).
        """
        led_entity = room.get(CONF_DEHUMIDIFIER_LED)
        if not led_entity:
            return

        room_name = room.get("name")
        state_entry = self._dehumidifier_state.setdefault(
            room_name, {"mode": mode, "unsub_timer": None}
        )

        if state_entry.get("led_alarm_active"):
            return

        color = self._mode_to_led_color(mode)
        self._async_apply_led_color(room, color)
        state_entry["led_color"] = color

    def _async_apply_led_color(self, room: dict, color: str) -> None:
        """Issue the actual light service call for a resolved LED colour."""
        led_entity = room.get(CONF_DEHUMIDIFIER_LED)
        if not led_entity:
            return

        if color == "off":
            self.hass.async_create_task(
                self.hass.services.async_call(
                    "light", "turn_off", {"entity_id": led_entity}, blocking=False
                )
            )
            return

        service_data = {"entity_id": led_entity, **self._LED_COLORS[color]}
        self.hass.async_create_task(
            self.hass.services.async_call("light", "turn_on", service_data, blocking=False)
        )

    def _async_start_led_alarm_blink(self, room: dict) -> None:
        """Start a self-rescheduling red/off blink for a room's LED while in alarm.

        Uses a recursive async_call_later chain rather than a fixed-interval
        helper so it naturally stops rescheduling once cancelled via
        _async_stop_led_alarm_blink (no separate 'still active' check needed
        inside the callback -- cancelling the unsub prevents the next call).
        """
        room_name = room.get("name")
        led_entity = room.get(CONF_DEHUMIDIFIER_LED)
        if not led_entity:
            return

        # Cancel any pre-existing blink timer for this room first (safety)
        self._async_stop_led_alarm_blink(room_name)

        blink_on = {"value": True}  # start lit
        self._async_apply_led_color(room, "red")

        @ha_callback
        def _toggle(_now) -> None:
            blink_on["value"] = not blink_on["value"]
            self._async_apply_led_color(room, "red" if blink_on["value"] else "off")
            self._led_blink_unsubs[room_name] = async_call_later(
                self.hass, DEHUM_LED_BLINK_INTERVAL, _toggle
            )

        self._led_blink_unsubs[room_name] = async_call_later(
            self.hass, DEHUM_LED_BLINK_INTERVAL, _toggle
        )

    def _async_stop_led_alarm_blink(self, room_name: str) -> None:
        """Cancel a room's blink timer, if any."""
        unsub = self._led_blink_unsubs.pop(room_name, None)
        if unsub:
            unsub()
