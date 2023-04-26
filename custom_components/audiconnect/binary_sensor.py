"""Support for Audi Connect sensors."""
import logging

from homeassistant.components.binary_sensor import (
    DOMAIN as domain_sensor,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up binary sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            if data.get("sensor_type") == domain_sensor:
                entities.append(AudiSensor(coordinator, vin, name))

    async_add_entities(entities)


class AudiSensor(AudiEntity, BinarySensorEntity):
    """Representation of an Audi sensor."""

    @property
    def is_on(self):
        """Return is on."""
        return self.coordinator.data[self.vin].states[self.uid]["value"]
