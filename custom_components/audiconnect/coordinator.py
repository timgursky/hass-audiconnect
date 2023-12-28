"""Audi connecgt coordinator."""
from __future__ import annotations

from datetime import timedelta
import logging

from audiconnectpy import AudiConnect, AudiException

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

from .const import CONF_COUNTRY, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = 30


class AudiDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch datas."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Class to manage fetching Heatzy data API."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=SCAN_INTERVAL)
        )

        unit_system = (
            "imperial" if hass.config.units is US_CUSTOMARY_SYSTEM else "metric"
        )

        self.api = AudiConnect(
            async_create_clientsession(hass),
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            entry.data[CONF_COUNTRY],
            entry.data.get(CONF_PIN),
            unit_system,
        )

    async def _async_update_data(self) -> dict:
        """Update data."""
        try:
            await self.api.async_update()
            if not self.api.is_connected:
                raise UpdateFailed("Unable to connect")
        except AudiException as error:
            raise UpdateFailed(error) from error
        else:
            return self.api.vehicles
