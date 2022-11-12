"""Audi connecgt coordinator."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .audiconnectpy import AudiConnect, AudiException
from .const import CONF_COUNTRY, DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = 10


class AudiDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch datas."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Class to manage fetching Heatzy data API."""
        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=SCAN_INTERVAL)
        )
        self.api = AudiConnect(
            async_create_clientsession(hass),
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            entry.data[CONF_COUNTRY],
            entry.data[CONF_PIN],
        )

    async def _async_update_data(self) -> dict:
        """Update data."""
        try:
            await self.api.async_update(None)
            if not self.api.is_connected:
                raise UpdateFailed("Unable to connect")
            return self.api.vehicles
        except AudiException as error:
            raise UpdateFailed(error) from error
