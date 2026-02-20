"""Config flow for Fronius Energiegemeinschaft integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .api_client import FroniusEnergyClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
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
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
