"""Support for Audi Connect sensors."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass as dc, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiSensorDescription

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES: tuple[AudiSensorDescription, ...] = (
    AudiSensorDescription(
        icon="mdi:clock",
        key="last_update_time",
        value="last_access",
        native_unit_of_measurement="datetime",
        device_class=dc.TIMESTAMP,
        translation_key="last_update_time",
    ),
    AudiSensorDescription(
        icon="mdi:temperature-celsius",
        native_unit_of_measurement="°C",
        key="cliamtisation_target_temperature",
        value="climatisation.climatisation_settings.target_temperature_c",
        device_class=dc.TEMPERATURE,
        translation_key="cliamtisation_target_temperature",
    ),
    AudiSensorDescription(
        icon="mdi:oil",
        native_unit_of_measurement="km",
        key="maintenance_inspection_to_oil_change",
        value="vehicle_health_inspection.maintenance_status.oil_service_due_km",
        device_class=dc.DISTANCE,
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval_distance_to_oil_change",
    ),
    AudiSensorDescription(
        icon="mdi:oil",
        native_unit_of_measurement="d",
        key="maintenance_interval_to_oil_change",
        value="vehicle_health_inspection.maintenance_status.oil_service_due_days",
        device_class=dc.DURATION,
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval_time_to_oil_change",
    ),
    AudiSensorDescription(
        icon="mdi:room-service-outline",
        native_unit_of_measurement="km",
        key="maintenance_inspection",
        value="vehicle_health_inspection.maintenance_status.inspection_due_km",
        device_class=dc.DISTANCE,
        translation_key="maintenance_inspection",
    ),
    AudiSensorDescription(
        icon="mdi:room-service-outline",
        native_unit_of_measurement="d",
        key="maintenance_interval",
        value="vehicle_health_inspection.maintenance_status.inspection_due_days",
        device_class=dc.DURATION,
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval",
    ),
    AudiSensorDescription(
        icon="mdi:speedometer",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        key="total_range",
        value="measurements.odometer_status.odometer",
        translation_key="total_range",
    ),
    AudiSensorDescription(
        icon="mdi:speedometer",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        key="electric_range",
        value="measurements.range_status.electric_range",
        translation_key="electric_range",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:speedometer",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        key="gasoline_range",
        value="measurements.range_status.gasoline_range",
        translation_key="gasoline_range",
    ),
    AudiSensorDescription(
        icon="mdi:gas-station",
        native_unit_of_measurement="%",
        key="tank_level",
        value="measurements.fuel_level_status.current_fuel_level_pct",
        translation_key="tank_level",
    ),
    AudiSensorDescription(
        icon="mdi:engine",
        key="primary_engine_type",
        value="measurements.fuel_level_status.primary_engine_type",
        translation_key="primary_engine_type",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:engine",
        key="secondary_engine_type",
        value="measurements.fuel_level_status.secondary_engine_type",
        translation_key="secondary_engine_type",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:engine",
        key="battery_temperature_max",
        value="measurements.temperature_battery_status.temperature_hv_battery_max_k",
        device_class=dc.TEMPERATURE,
        native_unit_of_measurement="K",
        translation_key="battery_temperature_max",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AudiSensorDescription(
        icon="mdi:engine",
        key="battery_temperature_min",
        value="measurements.temperature_battery_status.temperature_hv_battery_min_k",
        device_class=dc.TEMPERATURE,
        native_unit_of_measurement="K",
        translation_key="battery_temperature_min",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AudiSensorDescription(
        icon="mdi:ev-station",
        key="battery_level",
        value="charging.battery_status.current_soc_pct",
        device_class=dc.BATTERY,
        translation_key="battery_level",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:ev-station",
        key="cruising_range_electric",
        value="charging.battery_status.cruising_range_electric_km",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        translation_key="cruising_range_electric",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        key="charge_rate",
        value="charging.charging_status.charge_rate_kmph",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        translation_key="charge_rate_kmph",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:flash",
        device_class=dc.POWER,
        native_unit_of_measurement="kW",
        key="charge_power_kw",
        value="charging.charging_status.charge_power_kw",
        translation_key="charge_power_kw",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:battery-charging",
        key="remaining_charging",
        value="charging.charging_status.remaining_charging_time",
        native_unit_of_measurement="min",
        device_class=dc.DURATION,
        translation_key="remaining_charging",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:car-info",
        key="charge_type",
        value="charging.charging_status.charge_type",
        native_unit_of_measurement="min",
        device_class=dc.DURATION,
        translation_key="charge_type",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:ev-station",
        key="battery_level_target",
        value="charging.charge_settings.target_soc_pct",
        native_unit_of_measurement="%",
        device_class=dc.POWER_FACTOR,
        translation_key="battery_level_target",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:led-on",
        key="plug_led_color",
        value="charging.plug_status.led_color",
        translation_key="plug_led_color",
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    AudiSensorDescription(
        icon="mdi:av-timer",
        key="remaining_climatisation",
        value="climatisation.climatisation_status.remaining_climatisation_time_min",
        native_unit_of_measurement="min",
        device_class=dc.DURATION,
        translation_key="remaining_climatisation",
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:gas-station-outline",
        key="primary_engine_range",
        value="fuel_status.range_status.primary_engine.remaining_range_km",
        native_unit_of_measurement="km",
        translation_key="primary_engine_range",
        device_class=dc.DISTANCE,
        entity_registry_enabled_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:gas-station-outline",
        key="secondary_engine_range",
        value="fuel_status.range_status.secondary_engine.remaining_range_km",
        native_unit_of_measurement="km",
        device_class=dc.DISTANCE,
        translation_key="secondary_engine_range",
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AudiSensor(coordinator, vehicle, description)
        for description in SENSOR_TYPES
        for vehicle in coordinator.data
    ]
    async_add_entities(entities)


class AudiSensor(AudiEntity, SensorEntity):
    """Representation of a Audi sensor."""

    @property
    def state(self):
        """Return sensor state."""
        value = self.getattr(self.entity_description.value)
        if value and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value
