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
        icon="mdi:oil", key="warning_oil_change", value_fn=lambda x: x == 1
    ),
    AudiBinarySensorDescription(
        icon="mdi:oil",
        key="oil_display",
        value_fn=lambda x: x == 1,
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        icon="mdi:oil",
        key="oil_level_valid",
        value_fn=lambda x: x == 1,
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        icon="mdi:lightbulb",
        key="light_status",
        value_fn=lambda x: x != 2,
        device_class="safety",
    ),
    AudiBinarySensorDescription(
        icon="mdi:lightbulb", key="braking_status", value_fn=lambda x: x != 2
    ),
    AudiBinarySensorDescription(
        key="lock_state_left_front_door",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="lock_state_left_rear_door",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="lock_state_right_front_door",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="lock_state_right_rear_door",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="lock_state_trunk_lid",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="lock_state_hood",
        value_fn=lambda x: x != 2,
        device_class="lock",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="state_sun_roof_motor_cover",
        value_fn=lambda x: x != 2,
        device_class="cover",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="open_state_left_front_door",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="open_state_left_rear_door",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="open_state_right_front_door",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="open_state_right_rear_door",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="open_state_trunk_lid",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="open_state_hood",
        value_fn=lambda x: x != 3,
        device_class="door",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="state_left_front_window",
        value_fn=lambda x: x != 3,
        device_class="window",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="state_left_rear_window",
        value_fn=lambda x: x != 3,
        device_class="window",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="state_right_front_window",
        value_fn=lambda x: x != 3,
        device_class="window",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="state_right_rear_window",
        value_fn=lambda x: x != 3,
        device_class="window",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="state_spoiler",
        value_fn=lambda x: x != 3,
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="tyre_pressure_left_front_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="tyre_pressure_left_rear_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="tyre_pressure_right_front_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="tyre_pressure_right_rear_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_visible_default=False,
    ),
    AudiBinarySensorDescription(
        key="tyre_pressure_spare_tyre_difference",
        value_fn=lambda x: x != 1,
        device_class="problem",
        entity_registry_visible_default=False,
    ),
    # Meta sensors
    AudiBinarySensorDescription(key="any_window_open", device_class="window"),
    AudiBinarySensorDescription(key="any_door_open", device_class="door"),
    AudiBinarySensorDescription(key="any_tyre_problem", device_class="problem"),
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
