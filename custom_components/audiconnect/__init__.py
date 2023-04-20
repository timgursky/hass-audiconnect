"""The Audi connect integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr
import homeassistant.helpers.config_validation as cv

from .const import CONF_ACTION, CONF_VIN, DOMAIN
from .coordinator import AudiDataUpdateCoordinator

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SWITCH,
    Platform.LOCK,
]

SERVICE_REFRESH_VEHICLE_DATA = "refresh_data"
SERVICE_REFRESH_VEHICLE_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_VIN): cv.string,
    }
)

SERVICE_EXECUTE_VEHICLE_ACTION = "execute_vehicle_action"
SERVICE_EXECUTE_VEHICLE_ACTION_SCHEMA = vol.Schema(
    {vol.Required(CONF_VIN): cv.string, vol.Required(CONF_ACTION): cv.string}
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Audi connect from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = AudiDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    async def async_refresh_vehicle_data(call: ServiceCall) -> None:
        device_id = call.data.get(CONF_VIN).lower()
        device = dr.async_get(hass).async_get(device_id)
        vin = dict(device.identifiers).get(DOMAIN)
        await coordinator.api.async_refresh_vehicle_data(vin)
        await coordinator.async_request_refresh()

    async def async_execute_vehicle_action(call: ServiceCall) -> None:
        device_id = call.data.get(CONF_VIN).lower()
        device = dr.async_get(hass).async_get(device_id)
        vin = dict(device.identifiers).get(DOMAIN)
        action = call.data.get(CONF_ACTION).lower()

        match action:
            case "lock":
                await coordinator.api.async_set_lock(vin, True)
            case "unlock":
                await coordinator.api.async_set_lock(vin, False)
            case "start_climatisation":
                await coordinator.api.async_set_climatisation(vin, True)
            case "stop_climatisation":
                await coordinator.api.async_set_climatisation(vin, False)
            case "start_charger":
                await coordinator.api.async_set_battery_charger(vin, True, False)
            case "start_timed_charger":
                await coordinator.api.async_set_battery_charger(vin, True, True)
            case "stop_charger":
                await coordinator.api.async_set_battery_charger(vin, False, False)
            case "start_preheater":
                await coordinator.api.async_set_pre_heater(vin, True)
            case "stop_preheater":
                await coordinator.api.async_set_pre_heater(vin, False)
            case "start_window_heating":
                await coordinator.api.async_set_window_heating(vin, True)
            case "stop_window_heating":
                await coordinator.api.async_set_window_heating(vin, False)

        await coordinator.async_request_refresh()

    hass.services.async_register(
        DOMAIN,
        SERVICE_REFRESH_VEHICLE_DATA,
        async_refresh_vehicle_data,
        schema=SERVICE_REFRESH_VEHICLE_DATA_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_EXECUTE_VEHICLE_ACTION,
        async_execute_vehicle_action,
        schema=SERVICE_EXECUTE_VEHICLE_ACTION_SCHEMA,
    )

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Reload device tracker if change option."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: dr.DeviceEntry
) -> bool:
    """Remove config entry from a device."""
    return True
