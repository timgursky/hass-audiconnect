"""Audi connecgt coordinator."""

from __future__ import annotations

from datetime import timedelta
import logging

from audiconnectpy import AudiConnect, AudiException
from audiconnectpy.vehicle import Vehicle

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_PIN, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util.unit_system import US_CUSTOMARY_SYSTEM

from .const import (
    CONF_COUNTRY,
    CONF_MODEL,
    CONF_SCAN_INTERVAL,
    DEFAULT_MODEL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class AudiDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Class to manage fetching Heatzy data API."""
        unit_system = (
            "imperial" if hass.config.units is US_CUSTOMARY_SYSTEM else "metric"
        )
        self.options = entry.options
        self.api = AudiConnect(
            async_create_clientsession(hass),
            entry.data[CONF_USERNAME],
            entry.data[CONF_PASSWORD],
            entry.data[CONF_COUNTRY],
            entry.data.get(CONF_PIN),
            model=entry.data.get(CONF_MODEL, DEFAULT_MODEL),
            unit_system=unit_system,
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )

    async def _async_update_data(self) -> dict:
        """Update data."""
        try:
            await self.api.async_login()
        except AudiException as error:
            raise UpdateFailed(error) from error

        if self.api.is_connected:
            try:
                for vehicle in self.api.vehicles:
                    self._set_api_level(vehicle)
                    await vehicle.async_update()
            except AudiException as error:
                raise UpdateFailed(error) from error
            else:
                return self.api.vehicles
        else:
            raise UpdateFailed("Unable to connect")

    def _set_api_level(self, ojb: Vehicle) -> None:
        """Set API Level."""
        if api_levels := self.options.get(ojb.vin):
            for name, level in api_levels.items():
                ojb.set_api_level(name.replace("api_level_", ""), int(level))
