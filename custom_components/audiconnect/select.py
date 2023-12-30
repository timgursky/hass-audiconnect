"""Support for Audi Connect switches."""
from __future__ import annotations

import logging

from audiconnectpy import AudiException

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiSelectDescription

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiSelectDescription, ...] = (
    AudiSelectDescription(
        key="climatisation_heater_src",
        icon="mdi:air-conditioner",
        turn_mode="async_set_climater",
        options=["electric", "auxiliary", "automatic"],
        translation_key="climatisation_heater_src",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name in vehicle.states:
            for description in SENSOR_TYPES:
                if description.key == name:
                    entities.append(AudiSelect(coordinator, vin, description))

    async_add_entities(entities)


class AudiSelect(AudiEntity, SelectEntity):
    """Representation of a Audi select."""

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
                self.coordinator.api.vehicles.get(self.vin),
                self.entity_description.turn_mode,
            )(True, option)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to select on : %s", error)
