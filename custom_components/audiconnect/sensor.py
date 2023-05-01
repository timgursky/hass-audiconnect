"""Support for Audi Connect sensors."""
from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
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
        device_class="timestamp",
    ),
    AudiSensorDescription(
        icon="mdi:speedometer",
        native_unit_of_measurement="km",
        key="utc_time_and_kilometer_status",
        device_class="distance",
    ),
    AudiSensorDescription(
        icon="mdi:oil",
        native_unit_of_measurement="km",
        key="maintenance_interval_distance_to_oil_change",
        device_class="distance",
        value_fn=lambda x: abs(int(x)),
        entity_registry_visible_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:speedometer",
        native_unit_of_measurement="km",
        key="climatisation_target_temp",
        device_class="distance",
    ),
    AudiSensorDescription(
        icon="mdi:oil",
        native_unit_of_measurement="d",
        key="maintenance_interval_time_to_oil_change",
        device_class="duration",
        value_fn=lambda x: abs(int(x)),
        entity_registry_visible_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:room-service-outline",
        native_unit_of_measurement="km",
        key="maintenance_interval_distance_to_inspection",
        device_class="distance",
        value_fn=lambda x: abs(int(x)),
    ),
    AudiSensorDescription(
        icon="mdi:room-service-outline",
        native_unit_of_measurement="d",
        key="maintenance_interval_time_to_inspection",
        device_class="duration",
        value_fn=lambda x: abs(int(x)),
        entity_registry_visible_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:oil",
        native_unit_of_measurement="%",
        key="oil_level_dipsticks_percentage",
    ),
    AudiSensorDescription(key="adblue_range"),
    AudiSensorDescription(
        device_class="temperature",
        native_unit_of_measurement="°C",
        key="temperature_outside",
    ),
    AudiSensorDescription(
        key="bem_ok",
        device_class="problem",
        entity_registry_visible_default=False,
    ),
    AudiSensorDescription(
        icon="mdi:gas-station",
        device_class="distance",
        native_unit_of_measurement="km",
        key="total_range",
    ),
    AudiSensorDescription(
        icon="mdi:gas-station",
        native_unit_of_measurement="%",
        key="tank_level_in_percentage",
    ),
    AudiSensorDescription(
        native_unit_of_measurement="Min",
        key="preheater_duration",
        icon="mdi:clock",
        device_class="duration",
    ),
    AudiSensorDescription(key="charging_state", icon="mdi:car-battery"),
    AudiSensorDescription(
        native_unit_of_measurement="Min",
        key="preheater_remaining",
        icon="mdi:clock",
        device_class="duration",
    ),
    AudiSensorDescription(
        icon="mdi:electron-framework",
        key="actual_charge_rate",
        value_fn=lambda x: float(x) / 10,
    ),
    AudiSensorDescription(
        key="actual_charge_rate_unit", value_fn=lambda x: x.replace("_per_", "/")
    ),
    AudiSensorDescription(
        icon="mdi:flash",
        device_class="power",
        native_unit_of_measurement="kW",
        key="charging_power",
        value_fn=lambda x: int(x) / 1000,
    ),
    AudiSensorDescription(key="energy_flow"),
    AudiSensorDescription(icon="mdi:engine", key="primary_engine_type"),
    AudiSensorDescription(icon="mdi:engine", key="secondary_engine_type"),
    AudiSensorDescription(key="hybrid_range", native_unit_of_measurement="km"),
    AudiSensorDescription(
        icon="mdi:gas-station-outline",
        key="primary_engine_range",
        native_unit_of_measurement="km",
    ),
    AudiSensorDescription(
        icon="mdi:gas-station-outline",
        key="secondary_engine_range",
        native_unit_of_measurement="km",
    ),
    AudiSensorDescription(
        icon="mdi:ev-station",
        key="state_of_charge",
        native_unit_of_measurement="%",
        device_class="power_factor",
    ),
    AudiSensorDescription(
        icon="mdi:power-plug", key="plug_state ", device_class="power_factor"
    ),
    AudiSensorDescription(icon="mdi:power-plug", key="plug_lock", device_class="lock"),
    AudiSensorDescription(
        icon="mdi:battery-charging",
        key="remaining_charging_time",
        value_fn=lambda x: "n/a"
        if int(x) == 65535
        else "{r[0]:02d}:{r[1]:02d}".format(r=divmod(x, 60)),
        native_unit_of_measurement="Min",
        device_class="duration",
    ),
    AudiSensorDescription(
        icon="mdi:temperature-celsius",
        key="outdoor_temperature",
        native_unit_of_measurement="°C",
        device_class="temperature",
        value_fn=lambda x: round(float(x) / 10 - 273, 1),
    ),
    # AudiSensorDescription(key="trip"),
    AudiSensorDescription(icon="mdi:car-door", key="doors_trunk_status"),
    AudiSensorDescription(
        icon="mdi:update", key="last_update_time", device_class="timestamp"
    ),
    # AudiSensorDescription(key="trip_short_reset"),
    # AudiSensorDescription(key="trip_short_current"),
    # AudiSensorDescription(key="trip_long_reset"),
    # AudiSensorDescription(key="trip_long_current"),
    # AudiSensorDescription(key="trip_cyclic_reset"),
    # AudiSensorDescription(key="trip_cyclic_current"),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for vin, vehicle in coordinator.data.items():
        for name, data in vehicle.states.items():
            for description in SENSOR_TYPES:
                if description.key == name:
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
