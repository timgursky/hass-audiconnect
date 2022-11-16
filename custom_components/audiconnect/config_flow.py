"""Config flow for Audi connect integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .audiconnectpy import AudiConnect, AudiException, AuthorizationError
from .const import CONF_COUNTRY, CONF_LEVEL, COUNTRY_CODE, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_COUNTRY, default="DE"): vol.In(COUNTRY_CODE),
        vol.Optional(CONF_PIN): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Audi connect."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(entry: config_entries.ConfigEntry):
        """Get option flow."""
        return OptionsFlowHandler(entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            self._async_abort_entries_match({CONF_USERNAME: user_input[CONF_USERNAME]})
            connection = AudiConnect(
                async_create_clientsession(self.hass),
                user_input[CONF_USERNAME],
                user_input[CONF_PASSWORD],
                user_input[CONF_COUNTRY],
                user_input[CONF_PIN],
            )
            if await connection.async_login() is False:
                raise AuthorizationError(
                    "Unexpected error communicating with the Audi server"
                )
        except AudiException:
            errors["base"] = "cannot_connect"
        except AuthorizationError:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title="Audi connect", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option."""

    def __init__(self, config_entry):
        """Initialize the options flow."""
        self.config_entry = config_entry
        self._level = self.config_entry.options.get(CONF_LEVEL, 0)

    async def async_step_init(self, user_input=None):
        """Handle a flow initialized by the user."""
        options_schema = vol.Schema(
            {
                vol.Required(CONF_LEVEL, default=self._level): vol.In(
                    {-1: "Normal", 1: "Advance", 2: "Expert"}
                ),
            },
        )
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init", data_schema=options_schema)
