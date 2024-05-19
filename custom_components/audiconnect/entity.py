"""Audi entity vehicle."""

from __future__ import annotations

import logging

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
        self.vin = vehicle.vin
        self.uid = description.key
        self.entity_description = description

        self._attr_unique_id = f"{vehicle.vin}_{description.key}"
        self._attr_name = description.key.capitalize().replace("_", " ")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, vehicle.vin)},
            "manufacturer": MANUFACTURER,
            "name": vehicle.infos.media.short_name,
            "model": vehicle.infos.media.long_name,
            "configuration_url": URL_WEBSITE,
        }
        self._attr_extra_state_attributes = {
            "model": vehicle.infos.media.long_name,
            "model_year": vehicle.infos.core.model_year,
            "title": vehicle.infos.media.short_name,
            "csid": vehicle.csid,
            "vin": vehicle.vin,
        }

        _LOGGER.debug(self.entity_description.key)
        _LOGGER.debug(self.entity_description.value)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        for vehicle in self.coordinator.data:
            if vehicle.vin == self.vin:
                break
        self.vehicle = vehicle
        self.async_write_ha_state()

    def getattr(self, values: tuple(str)) -> str | float | int | bool | None:
        """Get recursive attribute."""
        obj = self.vehicle
        value = None
        if values:
            for v in values:
                value = getattr(obj, v)
                if value is None:
                    break
                obj = value
        return value
