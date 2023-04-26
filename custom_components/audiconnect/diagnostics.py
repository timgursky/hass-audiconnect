"""Diagnostics support for Audi Connect."""
from __future__ import annotations

from contextlib import suppress
from typing import Any, Callable

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {
    "address",
    "api_key",
    "city",
    "country",
    "csid",
    "deviceId",
    "email",
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
    "mappingVin"
    "password",
    "phone",
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
    services = coordinator.api.services
    _datas = {}

    async def diag(func: Callable[..., Any], *args: Any) -> None:
        rslt = {}
        with suppress(Exception):
            rsp = await func(*args)
            rslt = (
                rsp
                if isinstance(rsp, dict | list | set | float | int | str | tuple)
                else vars(rsp)
            )

        _datas[i].update({func.__name__.replace("async_get_", ""): rslt})

    i = 0
    for k, v in coordinator.data.items():
        i += 1
        _datas.update({i: vars(v)})
        await diag(services.async_get_vehicle_details, k)
        await diag(services.async_get_vehicle, k)
        await diag(services.async_get_stored_position, k)
        await diag(services.async_get_destinations, k)
        await diag(services.async_get_history, k)
        await diag(services.async_get_vehicule_users, k)
        await diag(services.async_get_charger, k)
        await diag(services.async_get_tripdata, k, "cyclic")
        await diag(services.async_get_tripdata, k, "longTerm")
        await diag(services.async_get_tripdata, k, "shortTerm")
        await diag(services.async_get_operations_list, k)
        await diag(services.async_get_climater, k)
        await diag(services.async_get_preheater, k)
        await diag(services.async_get_climater_timer, k)
        await diag(services.async_get_capabilities, k)
        await diag(services.async_get_vehicle_information)
        await diag(services.async_get_honkflash, k)
        await diag(services.async_get_fences, k)
        await diag(services.async_get_fences_config, k)
        await diag(services.async_get_speed_alert, k)
        await diag(services.async_get_speed_config, k)

    return {
        "entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "data": async_redact_data(_datas, TO_REDACT),
    }
