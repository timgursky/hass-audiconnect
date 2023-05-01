"""Support for tracking an Audi."""
from __future__ import annotations

import logging

from homeassistant.components.device_tracker import SourceType
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiTrackerDescription

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiTrackerDescription, ...] = (
    AudiTrackerDescription(
        key="position",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up device tracker."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            for description in SENSOR_TYPES:
                if description.key == name:
                    entities.append(AudiDeviceTracker(coordinator, vin, description))

    async_add_entities(entities)


class AudiDeviceTracker(AudiEntity, TrackerEntity):
    """Represent a tracked device."""

    @property
    def latitude(self):
        """Return latitude value of the device."""
        return self.coordinator.data[self.vin].states[self.uid]["latitude"]

    @property
    def longitude(self):
        """Return longitude value of the device."""
        return self.coordinator.data[self.vin].states[self.uid]["longitude"]

    @property
    def source_type(self):
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS

    @property
    def extra_state_attributes(self):
        """Return extra attributes."""
        attr = self.coordinator.data[self.vin].states[self.uid]
        return {"timestamp": attr["timestamp"], "parktime": attr["parktime"]}
