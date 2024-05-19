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
        icon="mdi:ev-station",
        key="charging",
        value=("charging", "charging_status", "charging_state"),
        turn_mode="async_set_battery_charger",
        translation_key="charging",
        entity_registry_enabled_default=False,
    ),
    AudiSwitchDescription(
        icon="mdi:air-conditioner",
        key="climatisation",
        value=("climatisation", "climatisation_status", "climatisation_state"),
        turn_mode="async_set_climater",
        translation_key="climatisation",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        AudiSwitch(coordinator, vehicle, description)
        for description in SENSOR_TYPES
        for vehicle in coordinator.data
    ]

    async_add_entities(entities)


class AudiSwitch(AudiEntity, SwitchEntity):
    """Representation of a Audi switch."""

    @property
    def is_on(self):
        """Return sensor state."""
        return self.getattr(self.entity_description.value)

    async def async_turn_on(self):
        """Turn the switch on."""
        try:
            await getattr(self.vehicle, self.entity_description.turn_mode)(True)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn on : %s", error)

    async def async_turn_off(self):
        """Turn the switch off."""
        try:
            await getattr(self.vehicle, self.entity_description.turn_mode)(False)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to turn off : %s", error)
