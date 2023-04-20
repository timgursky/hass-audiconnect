"""Audi entity vehicle."""
import logging

from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, URL_WEBSITE
from .coordinator import AudiDataUpdateCoordinator


_LOGGER = logging.getLogger(__name__)


class AudiEntity(CoordinatorEntity[AudiDataUpdateCoordinator], Entity):
    """Base class for all entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: AudiDataUpdateCoordinator, vin: str) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._unique_id = vin
        self._vehicle = coordinator.data[vin]
        self._attr_name = self._vehicle.title
        self._attr_device_info = {
            "identifiers": {(DOMAIN, vin)},
            "manufacturer": MANUFACTURER,
            "name": self._vehicle.title,
            "model": self._vehicle.model,
            "configuration_url": URL_WEBSITE,
        }
        self._attr_extra_state_attributes = {
            "model": f"{self._vehicle.model}",
            "model_year": self._vehicle.model_year,
            "title": self._vehicle.title,
            "csid": self._vehicle.csid,
            "vin": self._unique_id,
        }

    @staticmethod
    def format_name(name):
        """Format beautiful name."""
        return name.capitalize().replace("_", " ")
