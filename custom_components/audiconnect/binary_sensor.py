"""Support for Audi Connect sensors."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass as dc,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import AudiConfigEntry
from .entity import AudiEntity
from .helpers import AudiBinarySensorDescription

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES: tuple[AudiBinarySensorDescription, ...] = (
    AudiBinarySensorDescription(
        key="oil_level",
        icon="mdi:oil",
        name="Oil level",
        value="oil_level.oil_level_status.value",
        value_fn=lambda x: x is False,
        device_class=dc.PROBLEM,
        translation_key="oil_level",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AudiBinarySensorDescription(
        key="lights_right",
        icon="mdi:car-light-alert",
        name="Light: right",
        value="vehicle_lights.lights_status.lights.right",
        device_class=dc.LIGHT,
        entity_registry_enabled_default=False,
        translation_key="lights_right",
    ),
    AudiBinarySensorDescription(
        key="lights_left",
        icon="mdi:car-light-alert",
        name="Light: left",
        value="vehicle_lights.lights_status.lights.left",
        device_class=dc.LIGHT,
        entity_registry_enabled_default=False,
        translation_key="lights_left",
    ),
    AudiBinarySensorDescription(
        key="lights",
        icon="mdi:car-light-alert",
        name="Lights",
        value="vehicle_lights.lights_status.lights.status",
        device_class=dc.LIGHT,
        translation_key="lights",
    ),
    AudiBinarySensorDescription(
        key="door_lock_left_front",
        icon="mdi:car-door-lock",
        name="Door: lock left front",
        value="access.access_status.doors.locked.left_front",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="door_lock_left_front",
    ),
    AudiBinarySensorDescription(
        key="door_lock_right_front",
        icon="mdi:car-door-lock",
        name="Door: lock right front",
        value="access.access_status.doors.locked.right_front",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="door_lock_right_front",
    ),
    AudiBinarySensorDescription(
        key="door_lock_left_rear",
        icon="mdi:car-door-lock",
        name="Door: lock left rear",
        value="access.access_status.doors.locked.left_rear",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="door_lock_left_rear",
    ),
    AudiBinarySensorDescription(
        key="door_lock_right_rear",
        icon="mdi:car-door-lock",
        name="Door: lock right rear",
        value="access.access_status.doors.locked.right_rear",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="door_lock_right_rear",
    ),
    AudiBinarySensorDescription(
        key="trunk_lock",
        name="Trunk lock",
        value="access.access_status.doors.locked.trunk",
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="trunk_lock",
    ),
    AudiBinarySensorDescription(
        key="door_open_left_front",
        icon="mdi:car-door",
        name="Door: open left front",
        value="access.access_status.doors.opened.left_front",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="door_open_left_front",
    ),
    AudiBinarySensorDescription(
        key="door_open_right_front",
        icon="mdi:car-door",
        name="Door: open right front",
        value="access.access_status.doors.opened.right_front",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="door_open_right_front",
    ),
    AudiBinarySensorDescription(
        key="door_open_left_rear",
        icon="mdi:car-door",
        name="Door: open left rear",
        value="access.access_status.doors.opened.left_rear",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="door_open_left_rear",
    ),
    AudiBinarySensorDescription(
        key="door_open_right_rear",
        icon="mdi:car-door",
        name="Door: open right rear",
        value="access.access_status.doors.opened.right_rear",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="door_open_right_rear",
    ),
    AudiBinarySensorDescription(
        key="trunk_open",
        name="Trunk open",
        value="access.access_status.doors.opened.trunk",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="trunk_open",
    ),
    AudiBinarySensorDescription(
        key="bonnet_open",
        name="Bonnet open",
        value="access.access_status.doors.opened.bonnet",
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="bonnet_open",
    ),
    AudiBinarySensorDescription(
        key="door_open_any",
        name="Doors",
        value="access.access_status.doors.opened.any_doors_status",
        device_class=dc.DOOR,
        translation_key="door_open_any",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="sun_roof",
        name="Sun roof",
        value="access.access_status.windows.sun_roof",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="sun_roof",
    ),
    AudiBinarySensorDescription(
        key="roof_cover",
        name="Roof cover",
        value="access.access_status.windows.roof_cover",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="roof_cover",
    ),
    AudiBinarySensorDescription(
        key="window_left_front",
        name="Window: left front",
        value="access.access_status.windows.left_front",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="window_left_front",
    ),
    AudiBinarySensorDescription(
        key="window_right_front",
        name="Window: right front",
        value="access.access_status.windows.right_front",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="window_right_front",
    ),
    AudiBinarySensorDescription(
        key="window_left_rear",
        name="Window: left rear",
        value="access.access_status.windows.left_rear",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="window_left_rear",
    ),
    AudiBinarySensorDescription(
        key="window_right_rear",
        name="Window: right rear",
        value="access.access_status.windows.right_rear",
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="window_right_rear",
    ),
    AudiBinarySensorDescription(
        key="window_open_any",
        name="Windows",
        value="access.access_status.windows.any_windows_status",
        device_class=dc.WINDOW,
        translation_key="window_open_any",
    ),
    AudiBinarySensorDescription(
        icon="mdi:power-plug",
        key="plug_auto_unlock",
        name="Plug: auto unlock",
        value="charging.charge_settings.auto_unlock_plug_when_charged",
        translation_key="plug_auto_unlock",
        entity_registry_enabled_default=False,
    ),
    AudiBinarySensorDescription(
        icon="mdi:power-plug",
        key="plug_auto_unlock_ac",
        name="Plug: auto unlock ac",
        value="charging.charge_settings.auto_unlock_plug_when_charged_ac",
        translation_key="plug_auto_unlock_ac",
        entity_registry_enabled_default=False,
    ),
    AudiBinarySensorDescription(
        key="charging_state",
        name="Charging state",
        value="charging.charging_status.charging_state",
        device_class=dc.BATTERY_CHARGING,
        translation_key="charging_state",
        entity_registry_enabled_default=False,
    ),
    AudiBinarySensorDescription(
        key="plug_lock_state",
        icon="mdi:power-plug",
        name="Plug: lock",
        value="charging.plug_status.plug_lock_state",
        device_class=dc.LOCK,
        translation_key="plug_lock_state",
        entity_registry_enabled_default=False,
    ),
    AudiBinarySensorDescription(
        key="overall_status",
        icon="mdi:car",
        name="Overall status",
        device_class=dc.SAFETY,
        value="access.access_status.overall_status",
        value_fn=lambda x: x != "safe",
        translation_key="overall_status",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: AudiConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up binary sensor."""
    coordinator = entry.runtime_data
    entities = [
        AudiBinarySensor(coordinator, vehicle, description)
        for description in SENSOR_TYPES
        for vehicle in coordinator.data
    ]
    async_add_entities(entities)


class AudiBinarySensor(AudiEntity, BinarySensorEntity):
    """Representation of an Audi sensor."""

    @property
    def is_on(self):
        """Return is on."""
        value = self.getattr(self.entity_description.value)
        if value and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value
