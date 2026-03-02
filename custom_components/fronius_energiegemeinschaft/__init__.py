"""The Fronius Energiegemeinschaft integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    UPDATE_INTERVAL,
    DATA_COORDINATOR,
    DATA_CLIENT,
    DATA_PRICING,
    CONF_PRICE_GRID_CONSUMPTION,
    CONF_PRICE_COMMUNITY_CONSUMPTION,
    CONF_PRICE_GRID_FEED_IN,
    CONF_PRICE_COMMUNITY_FEED_IN,
    DEFAULT_PRICE_GRID_CONSUMPTION,
    DEFAULT_PRICE_COMMUNITY_CONSUMPTION,
    DEFAULT_PRICE_GRID_FEED_IN,
    DEFAULT_PRICE_COMMUNITY_FEED_IN,
)
from .api_client import FroniusEnergyClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


def _merge_energy_data(current: dict, previous: dict) -> dict:
    """Merge energy data from two months (current wins on overlap).

    Keeps the 'total' and 'meta' from the current month.
    Merges 'data' so daily entries from both months are available.
    """
    merged = dict(current)
    current_data = current.get("data", {})
    prev_data = previous.get("data", {})

    if not isinstance(current_data, dict) or not isinstance(prev_data, dict):
        return merged

    merged_data = {}
    all_rc_keys = set(list(current_data.keys()) + list(prev_data.keys()))
    for rc_key in all_rc_keys:
        curr_rc = current_data.get(rc_key, {})
        prev_rc = prev_data.get(rc_key, {})
        if isinstance(curr_rc, dict) and isinstance(prev_rc, dict):
            merged_data[rc_key] = {**prev_rc, **curr_rc}  # current overwrites prev on same key
        else:
            merged_data[rc_key] = curr_rc or prev_rc

    merged["data"] = merged_data
    return merged


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fronius Energiegemeinschaft from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

    # Get pricing from options (preferred) or data (fallback for upgrades)
    pricing = {
        "grid_consumption": entry.options.get(
            CONF_PRICE_GRID_CONSUMPTION,
            entry.data.get(CONF_PRICE_GRID_CONSUMPTION, DEFAULT_PRICE_GRID_CONSUMPTION),
        ),
        "community_consumption": entry.options.get(
            CONF_PRICE_COMMUNITY_CONSUMPTION,
            entry.data.get(
                CONF_PRICE_COMMUNITY_CONSUMPTION, DEFAULT_PRICE_COMMUNITY_CONSUMPTION
            ),
        ),
        "grid_feed_in": entry.options.get(
            CONF_PRICE_GRID_FEED_IN,
            entry.data.get(CONF_PRICE_GRID_FEED_IN, DEFAULT_PRICE_GRID_FEED_IN),
        ),
        "community_feed_in": entry.options.get(
            CONF_PRICE_COMMUNITY_FEED_IN,
            entry.data.get(CONF_PRICE_COMMUNITY_FEED_IN, DEFAULT_PRICE_COMMUNITY_FEED_IN),
        ),
    }

    client = FroniusEnergyClient(username, password, hass)

    # Test login
    try:
        await client.login()
    except Exception as err:
        _LOGGER.error("Failed to login: %s", err)
        return False

    async def async_update_data():
        """Fetch data from API."""
        try:
            now = datetime.now()
            current_month = now.strftime("%Y-%m")
            prev_month = (now.replace(day=1) - timedelta(days=1)).strftime("%Y-%m")

            # Get communities
            communities = await client.get_communities()

            # Get community energy data for all communities (current + previous month)
            community_data = {}
            for community in communities:
                community_id = community["id"]
                energy_current = await client.get_community_energy_data(
                    community_id, view="month", time=current_month
                )
                energy_prev = await client.get_community_energy_data(
                    community_id, view="month", time=prev_month
                )
                energy_data = _merge_energy_data(energy_current, energy_prev)

                # Log data structure for debugging
                data_section = energy_data.get("data", {})
                for rc_key, rc_val in (data_section.items() if isinstance(data_section, dict) else []):
                    _LOGGER.debug(
                        "Community %s rc_key=%s data type=%s entries=%s",
                        community_id, rc_key, type(rc_val).__name__,
                        len(rc_val) if rc_val else 0,
                    )
                    break

                community_data[community_id] = {
                    "info": community,
                    "energy": energy_data,
                }

            # Get counter points
            counter_points_raw = await client.get_counter_points()
            _LOGGER.debug(
                "Counter points raw response type=%s value=%s",
                type(counter_points_raw).__name__,
                str(counter_points_raw)[:500],
            )
            # Handle both list and dict ({"data": [...]}) response formats
            if isinstance(counter_points_raw, dict):
                counter_points = counter_points_raw.get("data", [])
            elif isinstance(counter_points_raw, list):
                counter_points = counter_points_raw
            else:
                counter_points = []

            # Get counter point energy data (current + previous month)
            counter_point_data = {}
            for counter_point in counter_points:
                cp_id = counter_point["id"]
                energy_current = await client.get_counter_point_energy_data(
                    cp_id, view="month", time=current_month
                )
                energy_prev = await client.get_counter_point_energy_data(
                    cp_id, view="month", time=prev_month
                )
                energy_data = _merge_energy_data(energy_current, energy_prev)

                # Log full structure for debugging counter point data
                _LOGGER.debug(
                    "CounterPoint %s energy keys=%s total_keys=%s data_type=%s data_sample=%s",
                    cp_id,
                    list(energy_data.keys()),
                    list(energy_data.get("total", {}).keys()),
                    type(energy_data.get("data")).__name__,
                    str(energy_data.get("data", {}))[:300],
                )

                counter_point_data[cp_id] = {
                    "info": counter_point,
                    "energy": energy_data,
                }

            return {
                "communities": community_data,
                "counter_points": counter_point_data,
            }
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=UPDATE_INTERVAL),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_CLIENT: client,
        DATA_PRICING: pricing,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        # Close the API client session
        client = hass.data[DOMAIN][entry.entry_id][DATA_CLIENT]
        await client.close()

        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
