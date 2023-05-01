"""Support for Audi Connect switches."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from audiconnectpy import AudiException
from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiSwitchDescription

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiSwitchDescription, ...] = (
    AudiSwitchDescription(
        key="preheater_state",
        turn_mode="async_pre_heating",
        value_fn=lambda x: x is not None,
    ),
    AudiSwitchDescription(
        key="preheater_active",
        turn_mode="async_pre_heating",
        value_fn=lambda x: x != "off",
    ),
    AudiSwitchDescription(
        key="charging_mode",
        turn_mode="async_charger",
    ),
    AudiSwitchDescription(
        icon="mdi:air-conditioner",
        key="climatisation_state",
        turn_mode="async_climater",
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
                    entities.append(AudiSwitch(coordinator, vin, description))

    async_add_entities(entities)


class AudiSwitch(AudiEntity, SwitchEntity):
    """Representation of a Audi switch."""

    @property
    def is_on(self):
        """Return sensor state."""
        value = self.coordinator.data[self.vin].states.get(self.uid)
        if value and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value

    async def async_turn_on(self):
        """Turn the switch on."""
        try:
            await getattr(
                self.coordinator.api.services, self.entity_description.turn_mode
            )(self.vin, True)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    async def async_turn_off(self):
        """Turn the switch off."""
        try:
            await getattr(
                self.coordinator.api.services, self.entity_description.turn_mode
            )(self.vin, False)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn off : %s", error)
