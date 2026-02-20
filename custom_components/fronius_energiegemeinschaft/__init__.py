"""The Fronius Energiegemeinschaft integration."""
from __future__ import annotations

import logging
from datetime import timedelta

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
)
from .api_client import FroniusEnergyClient

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fronius Energiegemeinschaft from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]

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
            # Get communities
            communities = await client.get_communities()

            # Get community energy data for all communities
            community_data = {}
            for community in communities:
                community_id = community["id"]
                energy_data = await client.get_community_energy_data(
                    community_id, view="month"
                )
                community_data[community_id] = {
                    "info": community,
                    "energy": energy_data,
                }

            # Get counter points
            counter_points = await client.get_counter_points()

            # Get counter point energy data
            counter_point_data = {}
            for counter_point in counter_points:
                cp_id = counter_point["id"]
                energy_data = await client.get_counter_point_energy_data(
                    cp_id, view="month"
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
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
