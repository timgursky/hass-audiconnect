"""Diagnostics support for Audi Connect."""

from __future__ import annotations
import re
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
    "latitude",
    "longitude",
    "csid",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    _datas = {}
    for k, v in hass.data[DOMAIN][entry.entry_id].data.items():
        _datas.update({k: vars(v)})

    regex = rf"(.*) ([A-Z]+) \((.*)\) \[(.*{DOMAIN}.*)\] (.*)"
    f = open(hass.data["logging"], "r")
    logs = re.findall(regex, f.read(), re.MULTILINE)

    return {
        "entry": {
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
        },
        "data": async_redact_data(_datas, TO_REDACT),
        "logs": logs,
    }
