"""The derived ``activity`` property and its precedence."""

from __future__ import annotations

from modbus_connection.mock import MockModbusUnit

from flexit_modbus import Flexit, SystemActivity


async def _set_measurements(
    unit: MockModbusUnit,
    *,
    heating: int = 0,
    cooling: int = 0,
    heat_recovery: int = 0,
    air_speed: int = 0,
) -> None:
    unit.input.update(
        {
            9: 0,
            11: 0,
            8: 0,
            15: heating,
            13: cooling,
            14: heat_recovery,
            27: 0,
            28: 0,
            48: air_speed,
        }
    )


async def test_activity_off_when_nothing_running(unit: MockModbusUnit) -> None:
    await _set_measurements(unit)
    device = Flexit(unit)
    await device.async_update()
    assert device.activity == SystemActivity.OFF


async def test_activity_fan_when_only_air_speed(unit: MockModbusUnit) -> None:
    await _set_measurements(unit, air_speed=3)
    device = Flexit(unit)
    await device.async_update()
    assert device.activity == SystemActivity.FAN


async def test_activity_heat_recovery_takes_precedence_over_fan(
    unit: MockModbusUnit,
) -> None:
    await _set_measurements(unit, heat_recovery=50, air_speed=3)
    device = Flexit(unit)
    await device.async_update()
    assert device.activity == SystemActivity.HEAT_RECOVERY


async def test_activity_cooling_takes_precedence_over_heat_recovery(
    unit: MockModbusUnit,
) -> None:
    await _set_measurements(unit, cooling=40, heat_recovery=50, air_speed=3)
    device = Flexit(unit)
    await device.async_update()
    assert device.activity == SystemActivity.COOLING


async def test_activity_heating_takes_precedence_over_everything(
    unit: MockModbusUnit,
) -> None:
    await _set_measurements(unit, heating=60, cooling=40, heat_recovery=50, air_speed=3)
    device = Flexit(unit)
    await device.async_update()
    assert device.activity == SystemActivity.HEATING


async def test_activity_is_none_before_any_update(unit: MockModbusUnit) -> None:
    await _set_measurements(unit)
    device = Flexit(unit)
    # No async_update() yet: every measurement reads as its unread default,
    # None, so the derived activity must also be None rather than "off".
    assert device.activity is None
