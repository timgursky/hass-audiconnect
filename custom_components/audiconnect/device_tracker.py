"""Support for tracking an Audi."""

from __future__ import annotations

import logging

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AudiConfigEntry
from .entity import AudiEntity
from .helpers import AudiTrackerDescription

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiTrackerDescription, ...] = (
    AudiTrackerDescription(key="position", name="Position", translation_key="position"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: AudiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up device tracker."""
    coordinator = entry.runtime_data
    entities = [
        AudiDeviceTracker(coordinator, vehicle, description)
        for description in SENSOR_TYPES
        for vehicle in coordinator.data
    ]
    async_add_entities(entities)


class AudiDeviceTracker(AudiEntity, TrackerEntity):
    """Represent a tracked device."""

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return self.vehicle.position.latitude

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return self.vehicle.position.longitude

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        return {"parktime": self.vehicle.position.last_access}
