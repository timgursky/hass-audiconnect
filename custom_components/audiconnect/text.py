"""Support for Audi Connect switches."""
import logging

from homeassistant.components.text import DOMAIN as domain_sensor, TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .audiconnectpy import AudiException
from .const import DOMAIN
from .entity import AudiEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            if data.get("sensor_type") == domain_sensor:
                entities.append(AudiText(coordinator, vin, name))

    async_add_entities(entities)


class AudiText(AudiEntity, TextEntity):
    """Representation of a Audi switch."""

    def __init__(self, coordinator, vin, uid):
        """Initialize."""
        super().__init__(coordinator, vin, uid)

    @property
    def native_value(self):
        """Native value."""
        return self.coordinator.data[self.vin].states[self.uid].get("value")

    @property
    def native_min(self):
        """Native min."""
        option = self.coordinator.data[self.vin].states[self.uid].get("options", [0])
        return option[0]

    @property
    def native_max(self):
        """Native max."""
        option = self.coordinator.data[self.vin].states[self.uid].get("options", [100])
        return option[0]

    async def async_set_value(self, value: str) -> None:
        """Set the text value."""
        try:
            await getattr(self.coordinator.api.services, self.entity["turn_mode"])(
                self.vin, value
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to set value: %s", error)
