"""Writable setpoints: target temperature and fan mode."""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit

from flexit_modbus import FanMode, Flexit, FlexitValueValidationError


async def test_set_target_temperature_writes_scaled_value(
    flexit: Flexit, unit: MockModbusUnit
) -> None:
    await flexit.async_set_target_temperature(22.5)
    assert unit.holding[8] == 225


async def test_set_target_temperature_reflected_after_next_update(
    flexit: Flexit, unit: MockModbusUnit
) -> None:
    await flexit.async_set_target_temperature(18.0)
    await flexit.async_update()
    assert flexit.target_temperature == 18.0


@pytest.mark.parametrize("value", [9.9, 30.1, 0, 45])
async def test_set_target_temperature_rejects_out_of_range(
    flexit: Flexit, value: float
) -> None:
    with pytest.raises(FlexitValueValidationError):
        await flexit.async_set_target_temperature(value)


@pytest.mark.parametrize("value", [10.0, 30.0, 21.5])
async def test_set_target_temperature_accepts_boundary_values(
    flexit: Flexit, unit: MockModbusUnit, value: float
) -> None:
    await flexit.async_set_target_temperature(value)
    assert unit.holding[8] == round(value * 10)


async def test_set_fan_mode_writes_enum_value(
    flexit: Flexit, unit: MockModbusUnit
) -> None:
    await flexit.async_set_fan_mode(FanMode.HIGH)
    assert unit.holding[17] == FanMode.HIGH.value


async def test_fan_mode_out_of_range_decodes_to_none(
    flexit: Flexit, unit: MockModbusUnit
) -> None:
    unit.holding[17] = 9  # not a valid FanMode member
    await flexit.async_update()
    assert flexit.fan_mode is None
