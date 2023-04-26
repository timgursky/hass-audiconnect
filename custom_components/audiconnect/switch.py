"""Support for Audi Connect switches."""
import logging

from homeassistant.components.switch import DOMAIN as domain_sensor, SwitchEntity
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
    """Set up the switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            if data.get("sensor_type") == domain_sensor:
                entities.append(AudiSwitch(coordinator, vin, name))

    async_add_entities(entities)


class AudiSwitch(AudiEntity, SwitchEntity):
    """Representation of a Audi switch."""

    @property
    def is_on(self):
        """Return sensor state."""
        return self.coordinator.data[self.vin].states[self.uid].get("value")

    async def async_turn_on(self):
        """Turn the switch on."""
        try:
            await getattr(self.coordinator.api.services, self.entity["turn_mode"])(
                self.vin, True
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    async def async_turn_off(self):
        """Turn the switch off."""
        try:
            await getattr(self.coordinator.api.services, self.entity["turn_mode"])(
                self.vin, False
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn off : %s", error)
