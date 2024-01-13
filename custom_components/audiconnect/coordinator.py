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

from .const import CONF_COUNTRY, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class AudiDataUpdateCoordinator(DataUpdateCoordinator):
    """Define an object to fetch datas."""

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
            unit_system,
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
            await self.api.async_update()
            if not self.api.is_connected:
                raise UpdateFailed("Unable to connect")
            self._set_api_level()
        except AudiException as error:
            raise UpdateFailed(error) from error
        else:
            return {
                vin: vehicle
                for vin, vehicle in self.api.vehicles.items()
                if vehicle.support_vehicle is True
            }

    def _set_api_level(self) -> None:
        """Set API Level."""
        if isinstance(self.api.vehicles, dict):
            for vin, Vehicle in self.api.vehicles.items():
                if api_levels := self.options.get(vin):
                    for name, level in api_levels.items():
                        Vehicle.set_api_level(
                            name.replace("api_level_", ""), int(level)
                        )
