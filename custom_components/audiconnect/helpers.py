"""Helpers for component."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntityDescription
from homeassistant.components.lock import LockEntityDescription
from homeassistant.components.number import NumberEntityDescription
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.sensor import SensorEntityDescription
from homeassistant.components.switch import SwitchEntityDescription
from homeassistant.helpers.typing import StateType


@dataclass(frozen=True)
class AudiTurnMixin:
    """Mixin for Audi sensor."""

    turn_mode: str


@dataclass(frozen=True)
class AudiSensorDescription(SensorEntityDescription):
    """Describes a sensor."""

    value_fn: Callable[..., StateType] | None = None


@dataclass(frozen=True)
class AudiBinarySensorDescription(BinarySensorEntityDescription):
    """Describes a binary sensor."""

    value_fn: Callable[..., StateType] | None = None


@dataclass(frozen=True)
class AudiSelectDescription(SelectEntityDescription, AudiTurnMixin):
    """Describes a select input."""

    value_fn: Callable[..., StateType] | None = None


@dataclass(frozen=True)
class AudiNumberDescription(NumberEntityDescription, AudiTurnMixin):
    """Describes a number input."""

    value_fn: Callable[..., StateType] | None = None


@dataclass(frozen=True)
class AudiSwitchDescription(SwitchEntityDescription, AudiTurnMixin):
    """Describes a switch."""

    value_fn: Callable[..., StateType] | None = None


@dataclass(frozen=True)
class AudiLockDescription(LockEntityDescription, AudiTurnMixin):
    """Describes a lock."""

    value_fn: Callable[..., StateType] | None = None


@dataclass(frozen=True)
class AudiTrackerDescription(SensorEntityDescription):
    """Describes a tracker."""

    value_fn: Callable[..., StateType] | None = None
