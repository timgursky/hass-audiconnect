"""Support for Audi Connect sensors."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass as dc,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiBinarySensorDescription

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES: tuple[AudiBinarySensorDescription, ...] = (
    AudiBinarySensorDescription(
        icon="mdi:oil",
        key="oil_level",
        value=("oil_level", "oil_level_status", "value"),
        value_fn=lambda x: x is False,
        device_class=dc.PROBLEM,
        translation_key="oil_level",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-light-alert",
        key="lights_right",
        value=("vehicle_lights", "lights_status", "lights", "right"),
        device_class=dc.LIGHT,
        entity_registry_enabled_default=False,
        translation_key="lights_right",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-light-alert",
        key="lights_left",
        value=("vehicle_lights", "lights_status", "lights", "left"),
        device_class=dc.LIGHT,
        entity_registry_enabled_default=False,
        translation_key="lights_left",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-light-alert",
        key="lights",
        value=("vehicle_lights", "lights_status", "lights", "status"),
        device_class=dc.LIGHT,
        translation_key="lights",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="door_lock_left_front",
        value=("access", "access_status", "doors", "locked", "left_front"),
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="door_lock_left_front",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="door_lock_right_front",
        value=("access", "access_status", "doors", "locked", "right_front"),
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="door_lock_right_front",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="door_lock_left_rear",
        value=("access", "access_status", "doors", "locked", "left_rear"),
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="door_lock_left_rear",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door-lock",
        key="door_lock_right_rear",
        value=("access", "access_status", "doors", "locked", "right_rear"),
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="door_lock_right_rear",
    ),
    AudiBinarySensorDescription(
        key="trunk_lock",
        value=("access", "access_status", "doors", "locked", "trunk"),
        device_class=dc.LOCK,
        entity_registry_enabled_default=False,
        translation_key="trunk_lock",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="door_open_left_front",
        value=("access", "access_status", "doors", "opened", "left_front"),
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="door_open_left_front",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="door_open_right_front",
        value=("access", "access_status", "doors", "opened", "right_front"),
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="door_open_right_front",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="door_open_left_rear",
        value=("access", "access_status", "doors", "opened", "left_rear"),
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="door_open_left_rear",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="door_open_right_rear",
        value=("access", "access_status", "doors", "opened", "right_rear"),
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="door_open_right_rear",
    ),
    AudiBinarySensorDescription(
        key="trunk_open",
        value=("access", "access_status", "doors", "opened", "trunk"),
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="trunk_open",
    ),
    AudiBinarySensorDescription(
        key="bonnet_open",
        value=("access", "access_status", "doors", "opened", "bonnet"),
        device_class=dc.DOOR,
        entity_registry_enabled_default=False,
        translation_key="bonnet_open",
    ),
    AudiBinarySensorDescription(
        key="door_open_any",
        value=("access", "access_status", "doors", "opened", "any_doors_status"),
        device_class=dc.DOOR,
        translation_key="door_open_any",
    ),
    AudiBinarySensorDescription(
        icon="mdi:car-door",
        key="sun_roof",
        value=("access", "access_status", "windows", "sun_roof"),
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="sun_roof",
    ),
    AudiBinarySensorDescription(
        key="roof_cover",
        value=("access", "access_status", "windows", "roof_cover"),
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="roof_cover",
    ),
    AudiBinarySensorDescription(
        key="window_left_front",
        value=("access", "access_status", "windows", "left_front"),
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="window_left_front",
    ),
    AudiBinarySensorDescription(
        key="window_right_front",
        value=("access", "access_status", "windows", "right_front"),
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="window_right_front",
    ),
    AudiBinarySensorDescription(
        key="window_left_rear",
        value=("access", "access_status", "windows", "left_rear"),
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="window_left_rear",
    ),
    AudiBinarySensorDescription(
        key="window_right_rear",
        value=("access", "access_status", "windows", "right_rear"),
        device_class=dc.WINDOW,
        entity_registry_enabled_default=False,
        translation_key="window_right_rear",
    ),
    AudiBinarySensorDescription(
        key="window_open_any",
        value=("access", "access_status", "windows", "any_windows_status"),
        device_class=dc.WINDOW,
        translation_key="window_open_any",
    ),
    AudiBinarySensorDescription(
        icon="mdi:power-plug",
        key="plug_auto_unlock",
        value=("charging", "charge_settings", "auto_unlock_plug_when_charged"),
        translation_key="plug_auto_unlock",
        entity_registry_enabled_default=False,
    ),
    AudiBinarySensorDescription(
        icon="mdi:power-plug",
        key="plug_auto_unlock_ac",
        value=("charging", "charge_settings", "auto_unlock_plug_when_charged_ac"),
        translation_key="plug_auto_unlock_ac",
        entity_registry_enabled_default=False,
    ),
    AudiBinarySensorDescription(
        key="charging_state",
        value=("charging", "charging_status", "charging_state"),
        device_class=dc.BATTERY_CHARGING,
        translation_key="charging_state",
        entity_registry_enabled_default=False,
    ),
    AudiBinarySensorDescription(
        icon="mdi:power-plug",
        key="plug_lock_state",
        value=("charging", "plug_status", "plug_lock_state"),
        device_class=dc.LOCK,
        translation_key="plug_lock_state",
        entity_registry_enabled_default=False,
    ),
    AudiBinarySensorDescription(
        icon="mdi:car",
        key="overall_status",
        device_class=dc.SAFETY,
        value=("access", "access_status", "overall_status"),
        value_fn=lambda x: x != "safe",
        translation_key="overall_status",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up binary sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
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
