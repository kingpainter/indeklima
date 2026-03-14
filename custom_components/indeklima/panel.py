# File Name: panel.py
# Version: 2.4.0
# Description: Panel and Lovelace card registration for Indeklima.
#              Registers the sidebar panel (admin only) and the custom Lovelace
#              card as static HTTP paths.
#
# Pattern based on PC User Statistics panel.py v2.4.1 — includes the
# _panel_registered flag fix: flag is cleared in async_unregister_panel()
# so the next setup always re-registers fresh.

from __future__ import annotations

import os
import logging

from homeassistant.components import panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant

from .const import DOMAIN, __version__

_LOGGER = logging.getLogger(__name__)

PANEL_URL         = f"/api/{DOMAIN}-panel"
CARDS_URL         = f"/api/{DOMAIN}-cards"
LOGO_URL          = f"/api/{DOMAIN}-logo"
LOGO_FILENAME     = "indeklima-logo.png"
PANEL_ICON        = "mdi:air-filter"
PANEL_NAME        = "indeklima-panel"
PANEL_TITLE       = "Indeklima"
PANEL_FOLDER      = "frontend"
PANEL_FILENAME    = "indeklima-panel.js"
CARDS_FILENAME    = "indeklima-cards.js"
CUSTOM_COMPONENTS = "custom_components"


async def async_register_panel(hass: HomeAssistant) -> None:
    """Register the sidebar panel and Lovelace card resource."""

    # Guard against double registration within the same HA session
    if hass.data[DOMAIN].get("_panel_registered", False):
        _LOGGER.debug("Indeklima panel already registered, skipping")
        return

    root_dir     = os.path.join(hass.config.path(CUSTOM_COMPONENTS), DOMAIN)
    frontend_dir = os.path.join(root_dir, PANEL_FOLDER)
    panel_file   = os.path.join(frontend_dir, PANEL_FILENAME)
    cards_file   = os.path.join(frontend_dir, CARDS_FILENAME)

    # Cache busting based on file mtime
    try:
        panel_cache_bust = int(os.path.getmtime(panel_file))
    except OSError:
        _LOGGER.warning("Panel JS file not found: %s", panel_file)
        panel_cache_bust = 0

    try:
        cards_cache_bust = int(os.path.getmtime(cards_file))
    except OSError:
        _LOGGER.warning("Cards JS file not found: %s", cards_file)
        cards_cache_bust = 0

    # ── Register static HTTP paths ─────────────────────────────────────────
    logo_file    = os.path.join(frontend_dir, LOGO_FILENAME)
    static_paths = [StaticPathConfig(PANEL_URL, panel_file, cache_headers=False)]
    if os.path.exists(cards_file):
        static_paths.append(StaticPathConfig(CARDS_URL, cards_file, cache_headers=False))
    if os.path.isfile(logo_file):
        static_paths.append(StaticPathConfig(LOGO_URL, logo_file, cache_headers=False))
        _LOGGER.info("Logo static path registered: %s", LOGO_URL)
        _LOGGER.info("Cards static path registered: %s → %s", CARDS_URL, cards_file)
    else:
        _LOGGER.warning("Cards JS file not found: %s", cards_file)

    await hass.http.async_register_static_paths(static_paths)
    _LOGGER.info("Panel static path registered: %s → %s", PANEL_URL, panel_file)

    # ── Register custom sidebar panel ──────────────────────────────────────
    await panel_custom.async_register_panel(
        hass,
        webcomponent_name=PANEL_NAME,
        frontend_url_path=DOMAIN,
        module_url=f"{PANEL_URL}?v={__version__}&m={panel_cache_bust}",
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        require_admin=True,
        config={},
    )

    # Flag must be cleared in async_unregister_panel()
    hass.data[DOMAIN]["_panel_registered"] = True
    _LOGGER.info("Indeklima panel '%s' registered in sidebar at /%s", PANEL_TITLE, DOMAIN)

    # ── Register card as Lovelace resource ────────────────────────────────
    if os.path.exists(cards_file):
        await _async_register_lovelace_resource(
            hass,
            url=f"{CARDS_URL}?v={__version__}&m={cards_cache_bust}",
            url_base=CARDS_URL,
        )


async def _async_register_lovelace_resource(
    hass: HomeAssistant,
    url: str,
    url_base: str,
) -> None:
    """Add or update the cards JS as a Lovelace resource."""
    import asyncio
    try:
        resources = hass.data.get("lovelace_resources")

        if resources is None:
            lovelace = hass.data.get("lovelace")
            if lovelace is None:
                _LOGGER.warning(
                    "Lovelace not available — add '%s' manually as a JS module resource", url
                )
                return
            resources = getattr(lovelace, "resources", None)

        if resources is None:
            _LOGGER.warning(
                "Cannot find Lovelace resources store — add '%s' manually as a JS module resource",
                url,
            )
            return

        # Wait until resources collection is loaded (up to 10 seconds)
        for _ in range(10):
            if getattr(resources, "loaded", True):
                break
            await asyncio.sleep(1)

        existing = [
            r for r in resources.async_items()
            if r["url"].startswith(url_base)
        ]

        if existing:
            resource = existing[0]
            if resource["url"] != url:
                await resources.async_update_item(
                    resource["id"],
                    {"res_type": "module", "url": url},
                )
                _LOGGER.info("Updated Indeklima cards Lovelace resource to: %s", url)
            else:
                _LOGGER.debug("Indeklima cards Lovelace resource already up to date")
        else:
            await resources.async_create_item({"res_type": "module", "url": url})
            _LOGGER.info(
                "Registered Indeklima cards Lovelace resource: %s — "
                "custom:indeklima-room-card and custom:indeklima-hub-card "
                "are now available in the card picker",
                url,
            )

    except Exception as err:
        _LOGGER.error("Failed to register Lovelace resource: %s", err)


def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove the panel from the sidebar and clear the registration flag.

    The _panel_registered flag MUST be cleared here. If it survives into
    the next async_setup_entry() call, async_register_panel() skips
    registration entirely — and the following unload then tries to remove
    a panel that was never registered.
    """
    from homeassistant.components import frontend

    if hass.data.get(DOMAIN, {}).get("_panel_registered", False):
        frontend.async_remove_panel(hass, DOMAIN)
        _LOGGER.debug("Indeklima panel removed from sidebar")
    else:
        _LOGGER.debug("Indeklima panel was not registered, skipping removal")

    # Always clear the flag so the next setup registers fresh
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["_panel_registered"] = False


async def async_unregister_cards_resource(hass: HomeAssistant) -> None:
    """Remove the cards Lovelace resource (called on integration unload)."""
    try:
        resources = hass.data.get("lovelace_resources")

        if resources is None:
            lovelace = hass.data.get("lovelace")
            if not lovelace:
                return
            resources = getattr(lovelace, "resources", None)

        if resources is None:
            return

        if not getattr(resources, "loaded", True):
            return

        existing = [
            r for r in resources.async_items()
            if r["url"].startswith(CARDS_URL)
        ]
        for resource in existing:
            await resources.async_delete_item(resource["id"])
            _LOGGER.info("Removed Indeklima cards resource: %s", resource["url"])

    except Exception as err:
        _LOGGER.debug("Could not remove Indeklima cards resource: %s", err)
