"""Support for Audi Connect switches."""

from __future__ import annotations

import logging

from audiconnectpy import AudiException

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AudiConfigEntry
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
    hass: HomeAssistant, entry: AudiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch."""
    coordinator = entry.runtime_data
    entities = [
        AudiSelect(coordinator, vehicle, description)
        for description in SENSOR_TYPES
        for vehicle in coordinator.data
    ]
    async_add_entities(entities)


class AudiSelect(AudiEntity, SelectEntity):
    """Representation of a Audi select."""

    @property
    def current_option(self):
        """Return sensor state."""
        value = self.getattr(self.entity_description.value)
        if value is not None and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        try:
            await getattr(
                self.vehicle,
                self.entity_description.turn_mode,
            )(True, option)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to select on : %s", error)
