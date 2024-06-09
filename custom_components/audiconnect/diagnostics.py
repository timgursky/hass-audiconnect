"""Diagnostics support for Audi Connect."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import suppress
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.core import HomeAssistant

from . import AudiConfigEntry

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
    "customTitle",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: AudiConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    async def diag(func: Callable[..., Any], *args: Any) -> None:
        with suppress(Exception):
            rsp = await func(*args)
            return (
                rsp
                if isinstance(rsp, dict | list | set | float | int | str | tuple)
                else vars(rsp)
            )

    information_vehicles = {
        "async_get_information_vehicles": await diag(
            coordinator.api.async_get_information_vehicles
        )
    }

    vehicles = {}
    for idx, vehicle in enumerate(coordinator.data):
        functions = {
            "async_get_capabilities": await diag(vehicle.async_get_capabilities),
            "async_get_selectivestatus": await diag(vehicle.async_get_selectivestatus),
        }
        vehicle_dict = vehicle.to_dict()
        vehicle_dict.update(**functions)
        vehicle_dict.pop("location", None)
        vehicles.update({idx: vehicle_dict})

    return {
        "entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "information_vehicles": async_redact_data(information_vehicles, TO_REDACT),
        "vehicles": async_redact_data(vehicles, TO_REDACT),
    }
