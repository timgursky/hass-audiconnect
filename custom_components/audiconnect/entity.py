"""Audi entity vehicle."""
import logging

from homeassistant.const import ATTR_DEVICE_CLASS, ATTR_ICON, ATTR_UNIT_OF_MEASUREMENT
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, URL_WEBSITE
from .coordinator import AudiDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class AudiEntity(CoordinatorEntity[AudiDataUpdateCoordinator], Entity):
    """Base class for all entities."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: AudiDataUpdateCoordinator, vin: str, uid: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        vehicle = coordinator.data[vin]
        self.entity = vehicle.states[uid]
        self.vin = vin
        self.uid = uid
        self._attr_unique_id = f"{vin}_{uid}"
        self._attr_name = uid.capitalize().replace("_", " ")
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
        self._attr_unit_of_measurement = self.entity.get(ATTR_UNIT_OF_MEASUREMENT)
        self._attr_icon = self.entity.get(ATTR_ICON)
        self._attr_device_class = self.entity.get(ATTR_DEVICE_CLASS)
