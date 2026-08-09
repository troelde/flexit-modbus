"""Enum shape and ordering."""

from __future__ import annotations

from flexit_modbus import FanMode, SystemActivity


def test_fan_mode_values() -> None:
    assert FanMode.OFF == 0
    assert FanMode.LOW == 1
    assert FanMode.MEDIUM == 2
    assert FanMode.HIGH == 3


def test_system_activity_precedence_order() -> None:
    # Higher value == higher precedence, matching the ``activity`` resolution.
    assert SystemActivity.HEATING > SystemActivity.COOLING
    assert SystemActivity.COOLING > SystemActivity.HEAT_RECOVERY
    assert SystemActivity.HEAT_RECOVERY > SystemActivity.FAN
    assert SystemActivity.FAN > SystemActivity.OFF
