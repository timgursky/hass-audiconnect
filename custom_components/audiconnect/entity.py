"""Audi entity vehicle."""

from __future__ import annotations

import logging
from operator import attrgetter

from audiconnectpy.vehicle import Vehicle

from homeassistant.core import callback
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, URL_WEBSITE
from .coordinator import AudiDataUpdateCoordinator
from .helpers import (
    AudiBinarySensorDescription,
    AudiLockDescription,
    AudiNumberDescription,
    AudiSelectDescription,
    AudiSensorDescription,
    AudiSwitchDescription,
    AudiTrackerDescription,
)

_LOGGER = logging.getLogger(__name__)


class AudiEntity(CoordinatorEntity[AudiDataUpdateCoordinator], Entity):
    """Base class for all entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AudiDataUpdateCoordinator,
        vehicle: Vehicle,
        description: AudiBinarySensorDescription
        | AudiLockDescription
        | AudiNumberDescription
        | AudiSelectDescription
        | AudiSwitchDescription
        | AudiSensorDescription
        | AudiTrackerDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.vehicle = vehicle
        self.entity_description = description

        self._attr_unique_id = f"{vehicle.vin}_{description.key}"
        self._attr_device_info = {
            "configuration_url": URL_WEBSITE,
            "hw_version": vehicle.infos.core.model_year,
            "identifiers": {(DOMAIN, vehicle.vin)},
            "manufacturer": MANUFACTURER,
            "model": vehicle.infos.media.long_name,
            "name": vehicle.infos.media.short_name,
        }

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for vehicle in self.coordinator.data:
            if vehicle.vin == self.vehicle.vin:
                break
        self.vehicle = vehicle
        self.async_write_ha_state()

    def getattr(self, value: str) -> str | float | int | bool | None:
        """Get recursive attribute."""
        try:
            return attrgetter(value)(self.vehicle)
        except AttributeError:
            return None
