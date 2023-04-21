"""Helper module."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, device_registry as dr

from .const import CONF_ACTION, CONF_VIN, DOMAIN
from .coordinator import AudiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SERVICE_REFRESH_DATA = "refresh_data"
SCHEMA_REFRESH_DATA = vol.Schema(
    {
        vol.Required(CONF_VIN): cv.string,
    }
)

SERVICE_TURN_ON = "turn_on_action"
SERVICE_TURN_OFF = "turn_off_action"
SCHEMA_ACTION = vol.Schema(
    {vol.Required(CONF_VIN): cv.string, vol.Required(CONF_ACTION): cv.string}
)


async def async_setup_services(
    hass: HomeAssistant, coordinator: AudiDataUpdateCoordinator
):
    """Register services."""

    async def async_refresh_data(call: ServiceCall) -> None:
        device_id = call.data.get(CONF_VIN).lower()
        device = dr.async_get(hass).async_get(device_id)
        vin = dict(device.identifiers).get(DOMAIN)
        await coordinator.api.async_refresh_vehicle_data(vin)
        await coordinator.async_request_refresh()

    async def async_turn_off_action(call: ServiceCall) -> None:
        device_id = call.data[CONF_VIN].lower()
        action = call.data[CONF_ACTION]
        device = dr.async_get(hass).async_get(device_id)
        vin = dict(device.identifiers).get(DOMAIN)

        await async_actions(vin, action, False)

    async def async_turn_on_action(call: ServiceCall) -> None:
        device_id = call.data[CONF_VIN].lower()
        action = call.data[CONF_ACTION]
        device = dr.async_get(hass).async_get(device_id)
        vin = dict(device.identifiers).get(DOMAIN)

        await async_actions(vin, action, True)

    async def async_actions(vin: str, action: str, mode: bool):
        """Execute action."""
        match action:
            case "lock":
                await coordinator.api.async_switch_lock(vin, mode)
            case "climater":
                await coordinator.api.async_switch_climater(vin, mode)
            case "charger":
                await coordinator.api.async_switch_charger(vin, mode)
            case "pre_heating":
                await coordinator.api.async_switch_pre_heating(vin, mode)
            case "window_heating":
                await coordinator.api.async_switch_window_heating(vin, mode)
            case "ventilation":
                await coordinator.api.async_switch_ventilation(vin, mode)

        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN, SERVICE_REFRESH_DATA, async_refresh_data, schema=SCHEMA_REFRESH_DATA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_TURN_ON, async_turn_on_action, schema=SCHEMA_ACTION
    )
    hass.services.async_register(
        DOMAIN, SERVICE_TURN_OFF, async_turn_off_action, schema=SCHEMA_ACTION
    )
