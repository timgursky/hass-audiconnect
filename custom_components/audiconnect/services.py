"""Helper module."""

from __future__ import annotations

import logging

from audiconnectpy import AudiException
from audiconnectpy.vehicle import Vehicle
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

    def search_vehicle(vin: str) -> Vehicle:
        """Return vehicle object."""
        for vehicle in coordinator.api.vehicles:
            if vehicle.vin == vin:
                return vehicle

    async def async_refresh_data(call: ServiceCall) -> None:
        device_id = call.data.get(CONF_VIN).lower()
        device = dr.async_get(hass).async_get(device_id)
        vin = dict(device.identifiers).get(DOMAIN)
        vehicle = search_vehicle(vin)
        await vehicle.async_refresh_vehicle_data()
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
        vehicle = search_vehicle(vin)
        try:
            match action:
                case "lock":
                    await vehicle.async_set_lock(mode)
                case "climater":
                    await vehicle.async_set_climater(mode)
                case "charger":
                    await vehicle.async_set_battery_charger(mode)
                case "pre_heating":
                    await vehicle.async_set_pre_heating(mode)
                case "window_heating":
                    await vehicle.async_set_window_heating(mode)
                case "ventilation":
                    await vehicle.async_set_ventilation(mode)
        except AudiException as error:
            _LOGGER.error(error)
        else:
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
