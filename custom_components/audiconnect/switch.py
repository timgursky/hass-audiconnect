"""Support for Audi Connect switches."""
from __future__ import annotations

import logging

from audiconnectpy import AudiException

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiSwitchDescription

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiSwitchDescription, ...] = (
    AudiSwitchDescription(
        icon="mdi:heating-coil",
        key="preheater_state",
        turn_mode="async_set_pre_heating",
        value_fn=lambda x: x is not None,
        translation_key="preheater_state",
    ),
    AudiSwitchDescription(
        icon="mdi:ev-station",
        key="charging_state",
        value_fn=lambda x: x != "off",
        turn_mode="async_set_charger",
        translation_key="charging_state",
    ),
    AudiSwitchDescription(
        icon="mdi:air-conditioner",
        key="climatisation_state",
        turn_mode="async_set_climater",
        value_fn=lambda x: x != "off",
        translation_key="climatisation_state",
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
                self.coordinator.api.vehicles.get(self.vin),
                self.entity_description.turn_mode,
            )(True)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    async def async_turn_off(self):
        """Turn the switch off."""
        try:
            await getattr(
                self.coordinator.api.vehicles.get(self.vin),
                self.entity_description.turn_mode,
            )(False)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn off : %s", error)
