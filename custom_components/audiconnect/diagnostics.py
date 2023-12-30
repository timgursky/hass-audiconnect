"""Diagnostics support for Audi Connect."""
from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import Any

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
    "mappingVin",
    "password",
    "phone",
    "pin",
    "requestId",
    "serial",
    "system_serial",
    "userId",
    "username",
    "vin",
    "firstName",
    "lastName",
    "dateOfBirth",
    "nickname",
    "placeOfBirth",
    "carnetEnrollmentCountry",
    "spin",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
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
    for vehicle in coordinator.data.values():
        i += 1
        _datas.update({i: vars(vehicle)})
        await diag(vehicle.async_get_vehicle_details)
        await diag(vehicle.async_get_vehicle)
        await diag(vehicle.async_get_stored_position)
        await diag(vehicle.async_get_destinations)
        await diag(vehicle.async_get_history)
        await diag(vehicle.async_get_vehicule_users)
        await diag(vehicle.async_get_charger)
        await diag(vehicle.async_get_tripdata, "cyclic")
        await diag(vehicle.async_get_tripdata, "longTerm")
        await diag(vehicle.async_get_tripdata, "shortTerm")
        await diag(vehicle.async_get_operations_list)
        await diag(vehicle.async_get_climater)
        await diag(vehicle.async_get_preheater)
        await diag(vehicle.async_get_climater_timer)
        await diag(vehicle.async_get_capabilities)
        await diag(vehicle.async_get_honkflash)
        # await diag(vehicle.async_get_personal_data)
        await diag(vehicle.async_get_real_car_data)
        await diag(vehicle.async_get_mbb_status)
        await diag(vehicle.async_get_identity_data)
        await diag(vehicle.async_get_users)
        await diag(vehicle.async_get_fences)
        await diag(vehicle.async_get_fences_config)
        await diag(vehicle.async_get_speed_alert)
        await diag(vehicle.async_get_speed_config)

    return {
        "entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "data": async_redact_data(_datas, TO_REDACT),
    }
