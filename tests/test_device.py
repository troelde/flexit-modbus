"""Reading the whole device and checking decoded values."""

from __future__ import annotations

from modbus_connection.mock import MockModbusUnit

from flexit_modbus import FanMode, Flexit


async def test_async_update_decodes_setpoints(flexit: Flexit) -> None:
    await flexit.async_update()
    assert flexit.target_temperature == 21.0
    assert flexit.fan_mode == FanMode.MEDIUM


async def test_async_update_decodes_measurements(flexit: Flexit) -> None:
    await flexit.async_update()
    assert flexit.measurements.supply_air_temperature == 19.0
    assert flexit.measurements.outdoor_air_temperature == -3.0
    assert flexit.measurements.filter_running_hours == 45
    assert flexit.measurements.filter_alarm is False
    assert flexit.measurements.electric_heater_enabled is False
    assert flexit.measurements.actual_air_speed == 2


async def test_filter_running_hours_is_unsigned(
    flexit: Flexit, unit: MockModbusUnit
) -> None:
    # A large unsigned value that would be negative if misread as signed.
    unit.input[8] = 60000
    await flexit.async_update()
    assert flexit.measurements.filter_running_hours == 60000


async def test_filter_alarm_and_heater_enabled_decode_to_bool(
    flexit: Flexit, unit: MockModbusUnit
) -> None:
    unit.input[27] = 1
    unit.input[28] = 1
    await flexit.async_update()
    assert flexit.measurements.filter_alarm is True
    assert flexit.measurements.electric_heater_enabled is True


async def test_pooled_reads_are_gap_planned(unit: MockModbusUnit) -> None:
    from modbus_connection.cli_helper import CountingUnit

    unit.holding.update({8: 210, 17: 2})
    unit.input.update({9: 190, 11: 0, 8: 45, 14: 0, 15: 0, 13: 0, 27: 0, 28: 0, 48: 0})
    counting = CountingUnit(unit)
    device = Flexit(counting)
    await device.async_update()
    # Gap-based planning merges nearby addresses into blocks (default max_gap):
    # one holding block (8, 17) and two input blocks (8-28, then 48, split by
    # the >16-address gap) — far fewer than one request per field.
    assert counting.reads == 3
