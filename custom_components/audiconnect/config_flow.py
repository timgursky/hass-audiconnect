"""Config flow for Audi connect integration."""
from __future__ import annotations

import logging
from typing import Any

from audiconnectpy import AudiConnect, AudiException, AuthorizationError
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

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


CONF_VEHICLE = "vehicle"
CONF_SAVE = "save"
API_LEVEL_CLIMATISATION = "api_level_climatisation"
API_LEVEL_VENTILATION = "api_level_ventilation"
API_LEVEL_CHARGER = "api_level_charger"


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Audi connect."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get option flow."""
        return OptionsFlowHandler(config_entry)

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


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle option."""

    def __init__(self, config_entry) -> None:
        """Initialize the options flow."""
        self.config_entry = config_entry
        self._sel = None
        self._data = {}

    async def async_step_init(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            if user_input.get(CONF_SAVE):
                return self.async_create_entry(title="", data=self._data)
            self._sel = user_input[CONF_VEHICLE]
            return await self.async_step_apilevel()

        dev_reg = dr.async_get(self.hass)
        entries = dr.async_entries_for_config_entry(dev_reg, self.config_entry.entry_id)
        dev_ids = {
            identifier[1]: entry.name
            for entry in entries
            for identifier in entry.identifiers
            if identifier[0] == DOMAIN
        }

        data_schema = vol.Schema(
            {
                vol.Required(CONF_VEHICLE): SelectSelector(
                    SelectSelectorConfig(
                        mode=SelectSelectorMode.DROPDOWN,
                        options=[
                            SelectOptionDict(value=vin, label=name)
                            for vin, name in dev_ids.items()
                        ],
                    )
                ),
                vol.Optional(CONF_SAVE, default=False): bool,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=data_schema, last_step=True
        )

    async def async_step_apilevel(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            self._data.update({self._sel: user_input})
            return await self.async_step_init()

        api_level = self.config_entry.options.get(self._sel, {})

        data_schema = vol.Schema(
            {
                vol.Required(
                    API_LEVEL_CLIMATISATION,
                    default=api_level.get(API_LEVEL_CLIMATISATION, "2"),
                ): SelectSelector(
                    SelectSelectorConfig(
                        mode=SelectSelectorMode.DROPDOWN,
                        options=[
                            SelectOptionDict(value="2", label="Level 2"),
                            SelectOptionDict(value="3", label="Level 3"),
                        ],
                    )
                ),
                vol.Required(
                    API_LEVEL_VENTILATION,
                    default=api_level.get(API_LEVEL_VENTILATION, "1"),
                ): SelectSelector(
                    SelectSelectorConfig(
                        mode=SelectSelectorMode.DROPDOWN,
                        options=[
                            SelectOptionDict(value="1", label="Level 1"),
                            SelectOptionDict(value="2", label="Level 2"),
                        ],
                    )
                ),
                vol.Required(
                    API_LEVEL_CHARGER,
                    default=api_level.get(API_LEVEL_CHARGER, "1"),
                ): SelectSelector(
                    SelectSelectorConfig(
                        mode=SelectSelectorMode.DROPDOWN,
                        options=[
                            SelectOptionDict(value="1", label="Level 1"),
                            SelectOptionDict(value="2", label="Level 2"),
                        ],
                    )
                ),
            }
        )

        return self.async_show_form(step_id="apilevel", data_schema=data_schema)
