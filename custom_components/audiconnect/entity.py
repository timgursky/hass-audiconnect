"""Audi entity vehicle."""
from __future__ import annotations

import logging

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, URL_WEBSITE
from .coordinator import AudiDataUpdateCoordinator
from .helpers import (
    AudiSensorDescription,
    AudiSwitchDescription,
    AudiBinarySensorDescription,
    AudiNumberDescription,
    AudiSelectDescription,
    AudiLockDescription,
    AudiTrackerDescription,
)

_LOGGER = logging.getLogger(__name__)


class AudiEntity(CoordinatorEntity[AudiDataUpdateCoordinator], Entity):
    """Base class for all entities."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: AudiDataUpdateCoordinator,
        vin: str,
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
        vehicle = coordinator.data[vin]
        self.entity = vehicle.states[description.key]
        self.entity_description = description
        self.vin = vin
        self.uid = description.key
        self._attr_unique_id = f"{vin}_{description.key}"
        self._attr_name = description.key.capitalize().replace("_", " ")
        self._attr_device_info = {
            "identifiers": {(DOMAIN, vin)},
            "manufacturer": MANUFACTURER,
            "name": vehicle.title,
            "model": vehicle.model,
            "configuration_url": URL_WEBSITE,
        }
        self._attr_extra_state_attributes = {
            "model": vehicle.model,
            "model_year": vehicle.model_year,
            "title": vehicle.title,
            "csid": vehicle.csid,
            "vin": vin,
        }
