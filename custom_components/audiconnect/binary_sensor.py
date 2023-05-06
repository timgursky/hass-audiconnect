"""Support for Audi Connect sensors."""
from __future__ import annotations
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity
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
        key="light_status",
        value_fn=lambda x: x != 2,
        translation_key="light_status",
    ),
    AudiBinarySensorDescription(
        icon="mdi:lightbulb",
        key="braking_status",
        value_fn=lambda x: x != 2,
        translation_key="braking_status",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="lock_state_left_front_door",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_enabled_default=False,
        translation_key="lock_state_left_front_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="lock_state_left_rear_door",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_enabled_default=False,
        translation_key="lock_state_left_rear_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="lock_state_right_front_door",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_enabled_default=False,
        translation_key="lock_state_right_front_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="lock_state_right_rear_door",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_enabled_default=False,
        translation_key="lock_state_right_rear_door",
    ),
    AudiBinarySensorDescription(
        key="lock_state_trunk_lid",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_enabled_default=False,
        translation_key="lock_state_trunk_lid",
    ),
    AudiBinarySensorDescription(
        key="lock_state_hood",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_enabled_default=False,
        translation_key="lock_state_hood",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="state_sun_roof_motor_cover",
        value_fn=lambda x: x != 2,
        device_class="cover",
        entity_registry_enabled_default=False,
        translation_key="state_sun_roof_motor_cover",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_state_left_front_door",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_enabled_default=False,
        translation_key="open_state_left_front_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_state_left_rear_door",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_enabled_default=False,
        translation_key="open_state_left_rear_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_state_right_front_door",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_enabled_default=False,
        translation_key="open_state_right_front_door",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="open_state_right_rear_door",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_enabled_default=False,
        translation_key="open_state_right_rear_door",
    ),
    AudiBinarySensorDescription(
        key="open_state_trunk_lid",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_enabled_default=False,
        translation_key="open_state_trunk_lid",
    ),
    AudiBinarySensorDescription(
        key="open_state_hood",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_enabled_default=False,
        translation_key="open_state_hood",
    ),
    AudiBinarySensorDescription(
        key="state_left_front_window",
        value_fn=lambda x: x != 3,
        device_class="window",
        entity_registry_enabled_default=False,
        translation_key="state_left_front_window",
    ),
    AudiBinarySensorDescription(
        key="state_left_rear_window",
        value_fn=lambda x: x != 3,
        device_class="window",
        entity_registry_enabled_default=False,
        translation_key="state_left_rear_window",
    ),
    AudiBinarySensorDescription(
        key="state_right_front_window",
        value_fn=lambda x: x != 3,
        device_class="window",
        entity_registry_enabled_default=False,
        translation_key="state_right_front_window",
    ),
    AudiBinarySensorDescription(
        key="state_right_rear_window",
        value_fn=lambda x: x != 3,
        device_class="window",
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
        device_class="problem",
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_left_front_tyre_difference",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_left_rear_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_left_rear_tyre_difference",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_right_front_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_right_front_tyre_difference",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_right_rear_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_right_rear_tyre_difference",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-tire-alert",
        key="tyre_pressure_spare_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_enabled_default=False,
        translation_key="tyre_pressure_spare_tyre_difference",
    ),
    AudiBinarySensorDescription(
        key="energy_flow", value_fn=lambda x: x != "off", translation_key="energy_flow"
    ),
    AudiBinarySensorDescription(
        icon="mdi:power-plug",
        key="plug_lock",
        device_class="lock",
        value_fn=lambda x: False if x == "unlocked" else True,
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
        key="any_window_open",
        device_class="window",
        translation_key="any_window_open",
    ),
    AudiBinarySensorDescription(
        key="any_door_open",
        device_class="door",
        icon="mdi:car-door",
        translation_key="any_door_open",
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
        for name, data in vehicle.states.items():
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
