"""Support for Audi Connect sensors."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
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
            if data.get("sensor_type") == "binary_sensor":
                entities.append(AudiSensor(coordinator, vin, name))

    async_add_entities(entities)


class AudiSensor(AudiEntity, BinarySensorEntity):
    """Representation of an Audi sensor."""

    def __init__(self, coordinator, vin, attr):
        """Initialize."""
        super().__init__(coordinator, vin)
        entity = coordinator.data[vin].states[attr]
        self._attribute = attr
        self._attr_name = self.format_name(attr)
        self._attr_unique_id = f"{vin}_{attr}"
        self._attr_unit_of_measurement = entity.get("unit")
        self._attr_icon = entity.get("icon")
        self._attr_device_class = entity.get("device_class")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Get the state and update it."""
        value = self.coordinator.data[self._unique_id].states[self._attribute]["value"]
        self._attr_is_on = value
        super()._handle_coordinator_update()
