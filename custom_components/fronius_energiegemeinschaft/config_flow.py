"""Config flow for Fronius Energiegemeinschaft integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api_client import FroniusEnergyClient
from .const import (
    DOMAIN,
    CONF_PRICE_GRID_CONSUMPTION,
    CONF_PRICE_COMMUNITY_CONSUMPTION,
    CONF_PRICE_GRID_FEED_IN,
    CONF_PRICE_COMMUNITY_FEED_IN,
    DEFAULT_PRICE_GRID_CONSUMPTION,
    DEFAULT_PRICE_COMMUNITY_CONSUMPTION,
    DEFAULT_PRICE_GRID_FEED_IN,
    DEFAULT_PRICE_COMMUNITY_FEED_IN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)

def get_pricing_schema(defaults: dict | None = None) -> vol.Schema:
    """Get pricing schema with optional defaults."""
    if defaults is None:
        defaults = {}

    return vol.Schema(
        {
            vol.Required(
                CONF_PRICE_GRID_CONSUMPTION,
                default=defaults.get(CONF_PRICE_GRID_CONSUMPTION, DEFAULT_PRICE_GRID_CONSUMPTION)
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
            vol.Required(
                CONF_PRICE_COMMUNITY_CONSUMPTION,
                default=defaults.get(CONF_PRICE_COMMUNITY_CONSUMPTION, DEFAULT_PRICE_COMMUNITY_CONSUMPTION)
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
            vol.Required(
                CONF_PRICE_GRID_FEED_IN,
                default=defaults.get(CONF_PRICE_GRID_FEED_IN, DEFAULT_PRICE_GRID_FEED_IN)
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
            vol.Required(
                CONF_PRICE_COMMUNITY_FEED_IN,
                default=defaults.get(CONF_PRICE_COMMUNITY_FEED_IN, DEFAULT_PRICE_COMMUNITY_FEED_IN)
            ): vol.All(vol.Coerce(float), vol.Range(min=0, max=100)),
        }
    )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    client = FroniusEnergyClient(data[CONF_USERNAME], data[CONF_PASSWORD], hass)

    try:
        await client.login()
        communities = await client.get_communities()

        if not communities:
            raise InvalidAuth("No communities found")

        # Return info that you want to store in the config entry.
        return {"title": f"Fronius Energiegemeinschaft ({data[CONF_USERNAME]})"}
    except Exception as err:
        _LOGGER.error("Failed to validate credentials: %s", err)
        raise InvalidAuth from err
    finally:
        await client.close()


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fronius Energiegemeinschaft."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._user_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Store credentials and proceed to pricing step
                self._user_data = user_input
                return await self.async_step_pricing()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_pricing(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the pricing configuration step."""
        if user_input is not None:
            # Combine user credentials and pricing data
            data = {**self._user_data, **user_input}
            title = f"Fronius Energiegemeinschaft ({self._user_data[CONF_USERNAME]})"
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(
            step_id="pricing", data_schema=get_pricing_schema()
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Fronius Energiegemeinschaft."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current values from config entry
        current_values = {
            CONF_PRICE_GRID_CONSUMPTION: self.config_entry.options.get(
                CONF_PRICE_GRID_CONSUMPTION,
                self.config_entry.data.get(
                    CONF_PRICE_GRID_CONSUMPTION, DEFAULT_PRICE_GRID_CONSUMPTION
                ),
            ),
            CONF_PRICE_COMMUNITY_CONSUMPTION: self.config_entry.options.get(
                CONF_PRICE_COMMUNITY_CONSUMPTION,
                self.config_entry.data.get(
                    CONF_PRICE_COMMUNITY_CONSUMPTION, DEFAULT_PRICE_COMMUNITY_CONSUMPTION
                ),
            ),
            CONF_PRICE_GRID_FEED_IN: self.config_entry.options.get(
                CONF_PRICE_GRID_FEED_IN,
                self.config_entry.data.get(
                    CONF_PRICE_GRID_FEED_IN, DEFAULT_PRICE_GRID_FEED_IN
                ),
            ),
            CONF_PRICE_COMMUNITY_FEED_IN: self.config_entry.options.get(
                CONF_PRICE_COMMUNITY_FEED_IN,
                self.config_entry.data.get(
                    CONF_PRICE_COMMUNITY_FEED_IN, DEFAULT_PRICE_COMMUNITY_FEED_IN
                ),
            ),
        }

        return self.async_show_form(
            step_id="init", data_schema=get_pricing_schema(current_values)
        )


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
