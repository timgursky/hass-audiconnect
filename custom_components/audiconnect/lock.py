"""Support for Audi Connect locks."""
import logging

from homeassistant.components.lock import LockEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .audiconnectpy import AudiException
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
            if data.get("sensor_type") == "lock":
                entities.append(AudiLock(coordinator, vin, name))

    async_add_entities(entities)


class AudiLock(AudiEntity, LockEntity):
    """Represents a car lock."""

    def __init__(self, coordinator, vin, attr):
        """Initialize."""
        super().__init__(coordinator, vin)
        self._entity = coordinator.data[vin].states[attr]
        self._attribute = attr
        self._attr_name = self.format_name(attr)
        self._attr_unique_id = f"{vin}_{attr}"
        self._attr_unit_of_measurement = self._entity.get("unit")
        self._attr_icon = self._entity.get("icon")
        self._attr_device_class = self._entity.get("device_class")

    async def async_lock(self, **kwargs):
        """Lock the car."""
        try:
            await getattr(self.coordinator.api, self._entity["turn_mode"])(
                self._unique_id, True
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    async def async_unlock(self, **kwargs):
        """Unlock the car."""
        try:
            await getattr(self.coordinator.api, self._entity["turn_mode"])(
                self._unique_id, False
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Get the state and update it."""
        value = self.coordinator.data[self._unique_id].states[self._attribute]["value"]
        self._attr_is_locked = value is False
        super()._handle_coordinator_update()
