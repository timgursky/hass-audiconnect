"""Support for Audi Connect switches."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from audiconnectpy import AudiException
from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiSelectDescription


_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiSelectDescription, ...] = (
    AudiSelectDescription(
        key="climatisation_heater_src",
        icon="mdi:air-conditioner",
        turn_mode="set_heater_source",
        options=["electric", "auxiliary", "automatic"],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            for description in SENSOR_TYPES:
                if description.key == name:
                    entities.append(AudiSelect(coordinator, vin, description))

    async_add_entities(entities)


class AudiSelect(AudiEntity, SelectEntity):
    """Representation of a Audi switch."""

    @property
    def current_option(self):
        """Return sensor state."""
        value = self.coordinator.data[self.vin].states.get(self.uid)
        if value and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            await getattr(
                self.coordinator.api.services, self.entity_description.turn_mode
            )(self.vin, option)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to selected option: %s", error)
