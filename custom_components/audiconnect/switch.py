"""Support for Audi Connect switches."""
import logging

from homeassistant.components.switch import DOMAIN as domain_sensor, ToggleEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_DEVICE_CLASS, ATTR_ICON
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
                entities.append(AudiSwitch(coordinator, vin, name))

    async_add_entities(entities)


class AudiSwitch(AudiEntity, ToggleEntity):
    """Representation of a Audi switch."""

    def __init__(self, coordinator, vin, attribute):
        """Initialize."""
        super().__init__(coordinator, vin)
        self._entity = coordinator.data[vin].states[attribute]
        self._attribute = attribute
        self._attr_name = self.format_name(attribute)
        self._attr_unique_id = f"{vin}_{attribute}"
        self._attr_unit_of_measurement = self._entity.get("unit")
        self._attr_icon = self._entity.get(ATTR_ICON)
        self._attr_device_class = self._entity.get(ATTR_DEVICE_CLASS)

    @property
    def is_on(self):
        """Return sensor state."""
        return self.coordinator.data[self._unique_id].states[self._attribute]["value"]

    async def async_turn_on(self):
        """Turn the switch on."""
        try:
            await getattr(self.coordinator.api, self._entity["turn_mode"])(
                self._unique_id, True
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    async def async_turn_off(self):
        """Turn the switch off."""
        try:
            await getattr(self.coordinator.api, self._entity["turn_mode"])(
                self._unique_id, False
            )
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn off : %s", error)
