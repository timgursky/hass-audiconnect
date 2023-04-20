"""Support for tracking an Audi."""
import logging

from homeassistant.components.device_tracker import DOMAIN as domain_sensor, SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
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
    """Set up device tracker."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            if data.get("sensor_type") == domain_sensor:
                entities.append(AudiDeviceTracker(coordinator, vin, name))

    async_add_entities(entities)


class AudiDeviceTracker(AudiEntity, TrackerEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator, vin, attribute):
        """Set up Locative entity."""
        super().__init__(coordinator, vin)
        entity = coordinator.data[vin].states[attribute]
        self._attribute = attribute
        self._attr_unique_id = f"{vin}_{attribute}"
        self._attr_unit_of_measurement = entity.get("unit")
        self._attr_icon = entity.get(ATTR_ICON)
        self._attr_device_class = entity.get(ATTR_DEVICE_CLASS)

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return self.coordinator.data[self._unique_id].states[self._attribute]["value"][
            "latitude"
        ]

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return self.coordinator.data[self._unique_id].states[self._attribute]["value"][
            "longitude"
        ]

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        value = self.coordinator.data[self._unique_id].states[self._attribute]["value"]
        return {
            "timestamp": value["timestamp"],
            "parktime": value["parktime"],
        }
