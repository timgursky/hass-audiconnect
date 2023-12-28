"""Support for Audi Connect locks."""
from __future__ import annotations

import logging

from audiconnectpy import AudiException

from homeassistant.components.binary_sensor import BinarySensorDeviceClass as dc
from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiLockDescription

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiLockDescription, ...] = (
    AudiLockDescription(
        key="any_door_unlocked",
        device_class=dc.LOCK,
        turn_mode="async_set_lock",
        translation_key="any_door_unlocked",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up lock."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name in vehicle.states:
            for description in SENSOR_TYPES:
                if description.key == name:
                    entities.append(AudiLock(coordinator, vin, description))

    async_add_entities(entities)


class AudiLock(AudiEntity, LockEntity):
    """Represents a car lock."""

    @property
    def is_locked(self):
        """Return lock status."""
        return self.coordinator.data[self.vin].states.get(self.uid, False) is False

    async def async_lock(self):
        """Lock the car."""
        try:
            await getattr(
                self.coordinator.api.vehicles.get(self.vin),
                self.entity_description.turn_mode,
            )(True)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    async def async_unlock(self):
        """Unlock the car."""
        try:
            await getattr(
                self.coordinator.api.vehicles.get(self.vin),
                self.entity_description.turn_mode,
            )(False)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)
