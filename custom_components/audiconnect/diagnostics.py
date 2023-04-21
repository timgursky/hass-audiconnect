"""Diagnostics support for Audi Connect."""
from __future__ import annotations

from contextlib import suppress
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {
    "api_key",
    "country",
    "csid",
    "deviceId",
    "encryption_password",
    "encryption_salt",
    "host",
    "imei",
    "ip4_addr",
    "ip6_addr",
    "lat",
    "latitude",
    "lon",
    "longitude",
    "password",
    "pin",
    "requestId",
    "serial",
    "system_serial",
    "userId",
    "username",
    "vin",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    services = coordinator.api._audi_service
    _datas = {}

    async def exec(vin, func):
        rslt = {}
        with suppress(Exception):
            rsp = await services.func(vin)
            rslt = rsp if isinstance(rsp, dict) else vars(rsp)

        _datas.update({func.__name__: rslt})

    for k, v in coordinator.data.items():
        _datas.update({k: vars(v)})
        await exec(services.async_get_capabilities, k)
        await exec(services.async_get_charger, k)
        await exec(services.async_get_climater, k)
        await exec(services.async_get_operations_list, k)
        await exec(services.async_get_preheater, k)
        await exec(services.async_get_stored_position, k)
        await exec(services.async_get_stored_vehicle_data, k)
        await exec(services.async_get_timer, k)
        await exec(services.async_get_tripdata, k)
        await exec(services.async_get_vehicle_data, k)
        await exec(services.async_get_vehicle_information, k)

    return {
        "entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "data": async_redact_data(_datas, TO_REDACT),
    }
