"""Support for Audi Connect locks."""
import logging

from homeassistant.components.lock import DOMAIN as domain_sensor, LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from audiconnectpy import AudiException
from .const import DOMAIN
from .entity import AudiEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up lock."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            if data.get("sensor_type") == domain_sensor:
                entities.append(AudiLock(coordinator, vin, name))

    async_add_entities(entities)


class AudiLock(AudiEntity, LockEntity):
    """Represents a car lock."""

    def __init__(self, coordinator, vin, uid):
        """Initialize."""
        super().__init__(coordinator, vin, uid)

    @property
    def is_locked(self):
        """Return lock status."""
        return (
            self.coordinator.data[self.vin].states[self.uid].get("value", False)
            is False
        )

    async def async_lock(self):
        """Lock the car."""
        try:
            await getattr(self.coordinator.api.services, self.entity["turn_mode"])(
                self.vin, True
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    async def async_unlock(self):
        """Unlock the car."""
        try:
            await getattr(self.coordinator.api.services, self.entity["turn_mode"])(
                self.vin, False
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)
