"""Diagnostics support for Audi Connect."""
from __future__ import annotations

from contextlib import suppress
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

TO_REDACT = {
    "username",
    "password",
    "encryption_password",
    "encryption_salt",
    "host",
    "api_key",
    "serial",
    "system_serial",
    "ip4_addr",
    "ip6_addr",
    "pin",
    "vin",
    "lon",
    "lat",
    "latitude",
    "longitude",
    "csid",
    "userId",
    "country",
    "deviceId",
    "imei",
    "country",
    "requestId",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    services = coordinator.api._audi_service
    _datas = {}
    for k, v in coordinator.data.items():
        _datas.update({k: vars(v)})
        capabilities = (
            charger
        ) = (
            climater
        ) = (
            operations_list
        ) = (
            preheater
        ) = (
            stored_position
        ) = (
            stored_position_v2
        ) = (
            stored_vehicle
        ) = (
            stored_vehicle_v2
        ) = timer = tripdata = vehicle_data = vehicle_information = {}
        with suppress(Exception):
            capabilities = await services.async_get_capabilities(k)
        with suppress(Exception):
            charger = await services.async_get_charger(k)
        with suppress(Exception):
            climater = await services.async_get_climater(k)
        with suppress(Exception):
            operations_list = await services.async_get_operations_list(k)
        with suppress(Exception):
            preheater = await services.async_get_preheater(k)
        with suppress(Exception):
            stored_position = await services.async_get_stored_position(k)
        with suppress(Exception):
            stored_position_v2 = await services.async_get_stored_positionV2(k)
        with suppress(Exception):
            stored_vehicle = await services.async_get_stored_vehicle_data(k)
        with suppress(Exception):
            stored_vehicle_v2 = await services.async_get_stored_vehicle_dataV2(k)
        with suppress(Exception):
            timer = await services.async_get_timer(k)
        with suppress(Exception):
            tripdata = await services.async_get_tripdata(k)
        with suppress(Exception):
            vehicle_data = await services.async_get_vehicle_data(k)
        with suppress(Exception):
            vehicle_information = await services.async_get_vehicle_information(k)
        _datas[k].update(
            {
                "capabilites": capabilities
                if isinstance(capabilities, dict)
                else vars(capabilities),
                "charger": charger if isinstance(charger, dict) else vars(charger),
                "climater": climater if isinstance(climater, dict) else vars(climater),
                "operations_list": operations_list
                if isinstance(operations_list, dict)
                else vars(operations_list),
                "preheater": preheater
                if isinstance(preheater, dict)
                else vars(preheater),
                "stored_position": stored_position
                if isinstance(stored_position, dict)
                else vars(stored_position),
                "stored_position_v2": stored_position_v2
                if isinstance(stored_position_v2, dict)
                else vars(stored_position_v2),
                "stored_vehicle": stored_vehicle
                if isinstance(stored_vehicle, dict)
                else vars(stored_vehicle),
                "stored_vehicle_v2": stored_vehicle_v2
                if isinstance(stored_vehicle_v2, dict)
                else vars(stored_vehicle_v2),
                "timer": timer if isinstance(timer, dict) else vars(timer),
                "tripdata": tripdata if isinstance(tripdata, dict) else vars(tripdata),
                "vehicle_data": vehicle_data
                if isinstance(vehicle_data, dict)
                else vars(vehicle_data),
                "vehicle_information": vehicle_information
                if isinstance(vehicle_information, dict)
                else vars(vehicle_information),
            }
        )

    return {
        "entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "data": async_redact_data(_datas, TO_REDACT),
    }
