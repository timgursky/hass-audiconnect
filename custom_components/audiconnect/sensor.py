"""Support for Audi Connect sensors."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorDeviceClass as dc, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import AudiEntity
from .helpers import AudiSensorDescription

_LOGGER = logging.getLogger(__name__)


SENSOR_TYPES: tuple[AudiSensorDescription, ...] = (
    AudiSensorDescription(
        key="last_access",
        icon="mdi:clock",
        native_unit_of_measurement="datetime",
        device_class=dc.TIMESTAMP,
        translation_key="last_access",
    ),
    AudiSensorDescription(
        icon="mdi:air-conditioner",
        key="climatisation_state",
        translation_key="climatisation_state",
    ),
    AudiSensorDescription(
        icon="mdi:update",
        key="last_update_time",
        device_class=dc.TIMESTAMP,
        translation_key="last_update_time",
    ),
    AudiSensorDescription(
        icon="mdi:ev-station",
        key="charging_state",
        translation_key="charging_state",
    ),
    AudiSensorDescription(
        icon="mdi:speedometer",
        native_unit_of_measurement="km",
        key="utc_time_and_kilometer_status",
        device_class=dc.DISTANCE,
        translation_key="utc_time_and_kilometer_status",
    ),
    AudiSensorDescription(
        icon="mdi:oil",
        native_unit_of_measurement="km",
        key="maintenance_interval_distance_to_oil_change",
        device_class=dc.DISTANCE,
        value_fn=lambda x: abs(int(x)),
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval_distance_to_oil_change",
    ),
    AudiSensorDescription(
        icon="mdi:temperature-celsius",
        native_unit_of_measurement="°C",
        key="climatisation_target_temp",
        value_fn=lambda x: round((int(x) - 2730) / 10, 1),
        device_class=dc.TEMPERATURE,
        translation_key="climatisation_target_temp",
    ),
    AudiSensorDescription(
        icon="mdi:oil",
        native_unit_of_measurement="d",
        key="maintenance_interval_time_to_oil_change",
        device_class=dc.DURATION,
        value_fn=lambda x: abs(int(x)),
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval_time_to_oil_change",
    ),
    AudiSensorDescription(
        icon="mdi:room-service-outline",
        native_unit_of_measurement="km",
        key="maintenance_interval_distance_to_inspection",
        device_class=dc.DISTANCE,
        value_fn=lambda x: abs(int(x)),
        translation_key="maintenance_interval_distance_to_inspection",
    ),
    AudiSensorDescription(
        icon="mdi:room-service-outline",
        native_unit_of_measurement="d",
        key="maintenance_interval_time_to_inspection",
        device_class=dc.DURATION,
        value_fn=lambda x: abs(int(x)),
        entity_registry_enabled_default=False,
        translation_key="maintenance_interval_time_to_inspection",
    ),
    AudiSensorDescription(
        icon="mdi:oil",
        native_unit_of_measurement="%",
        key="oil_level_dipsticks_percentage",
        translation_key="oil_level_dipsticks_percentage",
    ),
    AudiSensorDescription(
        key="adblue_range",
        icon="mdi:cup-water",
        entity_registry_enabled_default=False,
        native_unit_of_measurement="km",
        device_class=dc.DISTANCE,
        translation_key="adblue_range",
    ),
    AudiSensorDescription(
        device_class=dc.TEMPERATURE,
        native_unit_of_measurement="°C",
        key="temperature_outside",
        translation_key="temperature_outside",
    ),
    AudiSensorDescription(
        key="bem_ok",
        device_class="problem",
        entity_registry_enabled_default=False,
        translation_key="bem_ok",
    ),
    AudiSensorDescription(
        icon="mdi:speedometer",
        device_class=dc.DISTANCE,
        native_unit_of_measurement="km",
        key="total_range",
        translation_key="total_range",
    ),
    AudiSensorDescription(
        icon="mdi:gas-station",
        native_unit_of_measurement="%",
        key="tank_level_in_percentage",
        translation_key="tank_level_in_percentage",
    ),
    AudiSensorDescription(
        native_unit_of_measurement="Min",
        key="preheater_duration",
        icon="mdi:clock",
        device_class=dc.DURATION,
        translation_key="preheater_duration",
    ),
    AudiSensorDescription(
        native_unit_of_measurement="Min",
        key="preheater_remaining",
        icon="mdi:clock",
        device_class=dc.DURATION,
        translation_key="preheater_remaining",
    ),
    AudiSensorDescription(
        icon="mdi:electron-framework",
        key="actual_charge_rate",
        value_fn=lambda x: float(x) / 10,
        translation_key="actual_charge_rate",
    ),
    AudiSensorDescription(
        key="actual_charge_rate_unit",
        value_fn=lambda x: x.replace("_per_", "/"),
        translation_key="actual_charge_rate_unit",
    ),
    AudiSensorDescription(
        icon="mdi:flash",
        device_class=dc.POWER,
        native_unit_of_measurement="kW",
        key="charging_power",
        value_fn=lambda x: int(x) / 1000,
        translation_key="charging_power",
    ),
    AudiSensorDescription(
        icon="mdi:engine",
        key="primary_engine_type",
        translation_key="primary_engine_type",
    ),
    AudiSensorDescription(
        icon="mdi:engine",
        key="secondary_engine_type",
        translation_key="secondary_engine_type",
    ),
    AudiSensorDescription(
        key="hybrid_range",
        native_unit_of_measurement="km",
        translation_key="hybrid_range",
        device_class=dc.DISTANCE,
    ),
    AudiSensorDescription(
        icon="mdi:gas-station-outline",
        key="primary_engine_range",
        native_unit_of_measurement="km",
        translation_key="primary_engine_range",
        device_class=dc.DISTANCE,
    ),
    AudiSensorDescription(
        icon="mdi:gas-station-outline",
        key="secondary_engine_range",
        native_unit_of_measurement="km",
        device_class=dc.DISTANCE,
        translation_key="secondary_engine_range",
    ),
    AudiSensorDescription(
        icon="mdi:ev-station",
        key="state_of_charge",
        native_unit_of_measurement="%",
        device_class=dc.POWER_FACTOR,
        translation_key="state_of_charge",
    ),
    AudiSensorDescription(
        icon="mdi:battery-charging",
        key="remaining_charging_time",
        value_fn=lambda x: "n/a"
        if int(x) == 65535
        else f"{divmod(x, 60)[0]:02d}:{divmod(x, 60)[1]:02d}",
        native_unit_of_measurement="Min",
        device_class=dc.DURATION,
        translation_key="remaining_charging_time",
    ),
    AudiSensorDescription(
        icon="mdi:temperature-celsius",
        key="outdoor_temperature",
        native_unit_of_measurement="°C",
        device_class=dc.TEMPERATURE,
        value_fn=lambda x: round(float(x) / 10 - 273, 1),
        translation_key="outdoor_temperature",
    ),
    AudiSensorDescription(
        icon="mdi:car-door",
        key="doors_trunk_status",
        translation_key="doors_lock_status",
    ),
    AudiSensorDescription(
        icon="mdi:car",
        key="overall_status",
        translation_key="overall_status",
    ),    
    AudiSensorDescription(
        key="trip_short_current",
        translation_key="trip_short_current",
        value_fn=lambda x: x.get("timestamp"),
        native_unit_of_measurement="datetime",
        device_class=dc.TIMESTAMP,
    ),
    AudiSensorDescription(
        key="trip_short_reset",
        translation_key="trip_short_reset",
        value_fn=lambda x: x.get("timestamp"),
        native_unit_of_measurement="datetime",
        device_class=dc.TIMESTAMP,
    ),
    AudiSensorDescription(
        key="trip_long_current",
        translation_key="trip_long_current",
        value_fn=lambda x: x.get("timestamp"),
        native_unit_of_measurement="datetime",
        device_class=dc.TIMESTAMP,
    ),
    AudiSensorDescription(
        key="trip_long_reset",
        translation_key="trip_long_reset",
        value_fn=lambda x: x.get("timestamp"),
        native_unit_of_measurement="datetime",
        device_class=dc.TIMESTAMP,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name in vehicle.states:
            for description in SENSOR_TYPES:
                if description.key == name:
                    if description.key in [
                        "trip_short_current",
                        "trip_long_current",
                        "trip_short_reset",
                        "trip_long_reset",
                    ]:
                        entities.append(AudiTripSensor(coordinator, vin, description))
                    else:
                        entities.append(AudiSensor(coordinator, vin, description))

    async_add_entities(entities)


class AudiSensor(AudiEntity, SensorEntity):
    """Representation of a Audi sensor."""

    @property
    def state(self):
        """Return sensor state."""
        value = self.coordinator.data[self.vin].states.get(self.uid)
        if value and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value


class AudiTripSensor(AudiEntity, SensorEntity):
    """Representation of a Audi sensor."""

    @property
    def state(self):
        """Return sensor state."""
        value = self.coordinator.data[self.vin].states.get(self.uid)
        if value and self.entity_description.value_fn:
            return self.entity_description.value_fn(value)
        return value

    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return self.coordinator.data[self.vin].states.get(self.uid)
