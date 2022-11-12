"""Support for tracking an Audi."""
import logging

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
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
            if data.get("sensor_type") == "device_tracker":
                entities.append(AudiDeviceTracker(coordinator, vin, name))

    async_add_entities(entities)


class AudiDeviceTracker(AudiEntity, TrackerEntity):
    """Represent a tracked device."""

    def __init__(self, coordinator, vin, attr):
        """Set up Locative entity."""
        super().__init__(coordinator, vin)
        entity = coordinator.data[vin].states[attr]
        self._attribute = attr
        self._attr_unique_id = f"{vin}_{attr}"
        self._attr_unit_of_measurement = entity.get("unit")
        self._attr_icon = entity.get("icon")
        self._attr_device_class = entity.get("device_class")

    @property
    def latitude(self):
        """Return latitude value of the device."""
        value = self.coordinator.data[self._unique_id].states[self._attribute]["value"]
        return value["latitude"]

    @property
    def longitude(self):
        """Return longitude value of the device."""
        value = self.coordinator.data[self._unique_id].states[self._attribute]["value"]
        return value["longitude"]

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS

    @callback
    def _handle_coordinator_update(self) -> None:
        """Get the state and update it."""
        value = self.coordinator.data[self._unique_id].states[self._attribute]["value"]
        self._attr_extra_state_attributes = {
            "timestamp": value["timestamp"],
            "parktime": value["parktime"],
        }
        super()._handle_coordinator_update()
