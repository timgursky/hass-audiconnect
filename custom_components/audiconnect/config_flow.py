"""Config flow for Audi connect integration."""
from __future__ import annotations

import logging
from typing import Any

from audiconnectpy import AudiConnect, AudiException, AuthorizationError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_create_clientsession

from .const import CONF_COUNTRY, COUNTRY_CODE, DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
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
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                self._async_abort_entries_match(
                    {
                        CONF_USERNAME: user_input[CONF_USERNAME],
                    },
                )
                connection = AudiConnect(
                    async_create_clientsession(self.hass),
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                    user_input[CONF_COUNTRY],
                    user_input.get(CONF_PIN),
                )
                if await connection.async_login() is False:
                    raise AuthorizationError(
                        "Unexpected error communicating with the Audi server"
                    )
            except AuthorizationError:
                errors["base"] = "invalid_auth"
            except AudiException:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="Audi connect", data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
