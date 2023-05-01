"""Helpers for component."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from homeassistant.helpers.typing import StateType
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.components.lock import LockEntityDescription


@dataclass
class AuditTurnMixin:
    """Mixin for Audi sensor."""

    turn_mode: str


@dataclass
class AuditValueFnMixin:
    """Mixin for Audi sensor."""

    value_fn: Callable[..., StateType] | None = None


@dataclass
class AudiSensorDescription(AuditValueFnMixin, SensorEntityDescription):
    """Describes a sensor."""


@dataclass
class AudiBinarySensorDescription(AuditValueFnMixin, BinarySensorEntityDescription):
    """Describes a sensor."""


@dataclass
class AudiSelectDescription(AuditValueFnMixin, SelectEntityDescription, AuditTurnMixin):
    """Describes a sensor."""


@dataclass
class AudiNumberDescription(AuditValueFnMixin, NumberEntityDescription, AuditTurnMixin):
    """Describes a sensor."""


@dataclass
class AudiSwitchDescription(AuditValueFnMixin, SwitchEntityDescription, AuditTurnMixin):
    """Describes a sensor."""


@dataclass
class AudiLockDescription(AuditValueFnMixin, LockEntityDescription, AuditTurnMixin):
    """Describes a sensor."""


@dataclass
class AudiTrackerDescription(AuditValueFnMixin, SensorEntityDescription):
    """Describes a sensor."""
