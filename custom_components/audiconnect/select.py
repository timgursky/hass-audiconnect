"""Support for Audi Connect switches."""
import logging

from homeassistant.components.select import DOMAIN as domain_sensor, SelectEntity
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
                entities.append(AudiSelect(coordinator, vin, name))

    async_add_entities(entities)


class AudiSelect(AudiEntity, SelectEntity):
    """Representation of a Audi switch."""

    def __init__(self, coordinator, vin, uid):
        """Initialize."""
        super().__init__(coordinator, vin, uid)

    @property
    def current_option(self):
        """Return sensor state."""
        return self.coordinator.data[self.vin].states[self.uid].get("value")

    @property
    def options(self):
        """Options list."""
        return self.coordinator.data[self.vin].states[self.uid].get("options", [])

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            await getattr(self.coordinator.api.services, self.entity["turn_mode"])(
                self.vin, option
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to selected option: %s", error)
