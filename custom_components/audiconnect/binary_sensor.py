"""Support for Audi Connect sensors."""
import logging

from homeassistant.components.binary_sensor import (
    DOMAIN as domain_sensor,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_CLASS, ATTR_ICON
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

    def __init__(self, coordinator, vin, attribute):
        """Initialize."""
        super().__init__(coordinator, vin)
        entity = coordinator.data[vin].states[attribute]
        self._attribute = attribute
        self._attr_name = self.format_name(attribute)
        self._attr_unique_id = f"{vin}_{attribute}"
        self._attr_unit_of_measurement = entity.get("unit")
        self._attr_icon = entity.get(ATTR_ICON)
        self._attr_device_class = entity.get(ATTR_DEVICE_CLASS)

    @property
    def is_on(self):
        """Return is on."""
        return self.coordinator.data[self._unique_id].states[self._attribute]["value"]
