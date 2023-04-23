"""Support for Audi Connect sensors."""
import logging

from homeassistant.components.sensor import DOMAIN as domain_sensor, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            if data.get("sensor_type") == domain_sensor:
                entities.append(AudiSensor(coordinator, vin, name))

    async_add_entities(entities)


class AudiSensor(AudiEntity, SensorEntity):
    """Representation of a Audi sensor."""

    def __init__(self, coordinator, vin, uid):
        """Initialize."""
        super().__init__(coordinator, vin, uid)

    @property
    def state(self):
        """Return sensor state."""
        return self.coordinator.data[self.vin].states[self.uid].get("value")
