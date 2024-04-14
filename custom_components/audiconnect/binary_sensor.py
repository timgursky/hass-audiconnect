"""Support for Audi Connect sensors."""
from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass as dc,
)
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiBinarySensorDescription

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES: tuple[AudiBinarySensorDescription, ...] = (
    AudiBinarySensorDescription(
        icon="mdi:oil",
        key="warning_oil_change",
        value_fn=lambda x: x == 1,
        translation_key="warning_oil_change",
    ),
    AudiBinarySensorDescription(
        icon="mdi:oil",
        key="oil_display",
        value_fn=lambda x: x == 1,
        entity_registry_enabled_default=False,
        translation_key="oil_display",
    ),
    AudiBinarySensorDescription(
        icon="mdi:oil",
        key="oil_level_valid",
        value_fn=lambda x: x == 1,
        entity_registry_enabled_default=False,
        translation_key="oil_level_valid",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-light-alert",
        key="lights_status",
        translation_key="lights_status",
    ),
    AudiBinarySensorDescription(
        icon="mdi:lightbulb",
        key="braking_status",
        value_fn=lambda x: x is True,
        translation_key="braking_status",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-light-alert",
        key="lights_right",
        entity_registry_enabled_default=False,
        translation_key="lights_right",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-light-alert",
        key="lights_left",
        entity_registry_enabled_default=False,
        translation_key="lights_left",
    ),
    AudiBinarySensorDescription(
        icon="mdi:power-plug",
        key="plug_state",
        device_class=dc.PLUG,
        value_fn=lambda x: True if x == "connected" else False,
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="lock_left_front_door",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="lock_left_front_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="lock_left_rear_door",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="lock_left_rear_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="lock_right_front_door",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="lock_right_front_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="lock_right_rear_door",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="lock_right_rear_door",
    ),
    AudiBinarySensorDescription(
        key="lock_trunk",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="lock_trunk",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_sun_roof",
        device_class="cover",
        entity_registry_enabled_default=False,
        translation_key="open_sun_roof",
    ),
    AudiBinarySensorDescription(
        key="open_roof_cover",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="open_roof_cover",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_left_front_door",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="open_left_front_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_left_rear_door",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="open_left_rear_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_right_front_door",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="open_right_front_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_right_rear_door",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="open_right_rear_door",
    ),
    AudiBinarySensorDescription(
        key="open_trunk",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="open_trunk",
    ),
    AudiBinarySensorDescription(
        key="open_bonnet",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="open_bonnet",
    ),
    AudiBinarySensorDescription(
        key="open_left_front_window",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="state_left_front_window",
    ),
    AudiBinarySensorDescription(
        key="open_left_rear_window",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="state_left_rear_window",
    ),
    AudiBinarySensorDescription(
        key="open_right_front_window",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="state_right_front_window",
    ),
    AudiBinarySensorDescription(
        key="open_right_rear_window",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="state_right_rear_window",
    ),
    AudiBinarySensorDescription(
        key="state_spoiler",
        value_fn=lambda x: x != 3,
        entity_registry_enabled_default=False,
        translation_key="state_spoiler",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_left_front_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class=dc.PROBLEM,
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_left_front_tyre_difference",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_left_rear_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class=dc.PROBLEM,
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_left_rear_tyre_difference",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_right_front_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class=dc.PROBLEM,
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_right_front_tyre_difference",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_right_rear_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class=dc.PROBLEM,
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_right_rear_tyre_difference",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_spare_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class=dc.PROBLEM,
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_spare_tyre_difference",
    ),
    AudiBinarySensorDescription(
        key="energy_flow", value_fn=lambda x: x != "off", translation_key="energy_flow"
    ),
    AudiBinarySensorDescription(
        icon="mdi:power-plug",
        key="plug_lock",
        device_class=dc.LOCK,
        value_fn=lambda x: False if x == "locked" else True,
    ),
    AudiBinarySensorDescription(
        key="preheater_active",
        value_fn=lambda x: x != "off",
        translation_key="preheater_active",
    ),
    AudiBinarySensorDescription(
        key="charging_mode",
        value_fn=lambda x: x != "off",
        translation_key="charging_mode",
    ),
    # Meta sensors
    AudiBinarySensorDescription(
        key="open_any_window",
        device_class=dc.WINDOW,
        translation_key="open_any_window",
    ),
    AudiBinarySensorDescription(
        key="open_any_door",
        device_class=dc.DOOR,
        icon="mdi:car-door",
        translation_key="open_any_door",
    ),
    AudiBinarySensorDescription(
        key="any_tyre_problem",
        icon="mdi:car-tire-alert",
        translation_key="any_tyre_problem",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up binary sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name in vehicle.states:
            for description in SENSOR_TYPES:
                if description.key == name:
                    entities.append(AudiBinarySensor(coordinator, vin, description))

    async_add_entities(entities)


class AudiBinarySensor(AudiEntity, BinarySensorEntity):
    """Representation of an Audi sensor."""

    @property
    def is_on(self):
        """Return is on."""
        value = self.coordinator.data[self.vin].states.get(self.uid)
        if value and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value
