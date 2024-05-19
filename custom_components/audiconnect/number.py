"""Support for Audi Connect switches."""

from __future__ import annotations

import logging

from audiconnectpy import AudiException

from homeassistant.components.number import NumberDeviceClass as dc, NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiNumberDescription

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES: tuple[AudiNumberDescription, ...] = (
    AudiNumberDescription(
        icon="mdi:current-ac",
        native_unit_of_measurement="A",
        key="max_charge_current_ac",
        value=("charging", "charging_settings", "max_charge_current_ac"),
        turn_mode="async_set_charger_max",
        native_max_value=32,
        native_min_value=0,
        native_step=1,
        translation_key="max_charge_current_ac",
        device_class=dc.CURRENT,
    ),
    AudiNumberDescription(
        icon="mdi:temperature-celsius",
        native_unit_of_measurement="°C",
        key="climatisation_target_temperature",
        value=("climatisation", "climatisation_settings", "target_temperature_c"),
        turn_mode="async_set_climater_temp",
        device_class=dc.TEMPERATURE,
        native_max_value=40,
        native_min_value=7,
        native_step=0.1,
        translation_key="climatisation_target_temperature",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the switch."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AudiNumber(coordinator, vehicle, description)
        for description in SENSOR_TYPES
        for vehicle in coordinator.data
    ]
    async_add_entities(entities)


class AudiNumber(AudiEntity, NumberEntity):
    """Representation of a Audi switch."""

    @property
    def mode(self) -> str:
        """Mode."""
        return "box"

    @property
    def native_value(self) -> float:
        """Native value."""
        return self.getattr(self.entity_description.value)

    async def async_set_native_value(self, value: float) -> None:
        """Set the text value."""
        try:
            await getattr(
                self.vehicle,
                self.entity_description.turn_mode,
            )(value)
            await self.coordinator.async_request_refresh()
        except AudiException as error:
            _LOGGER.error("Error to set value: %s", error)
