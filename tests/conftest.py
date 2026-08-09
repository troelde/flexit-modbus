"""Fixtures: a ``Flexit`` device over modbus-connection's in-memory mock backend.

The mock backend and its fixtures ship with ``modbus-connection``. They are
imported explicitly below so the test suite does not depend on pytest
entry-point autoloading. There is no real server, socket, or backend here —
just an address-keyed store loaded with CI66-shaped register values.
"""

from __future__ import annotations

import pytest
from modbus_connection.mock import MockModbusUnit
from modbus_connection.pytest_plugin import (
    mock_modbus_connection as mock_modbus_connection,
    mock_modbus_unit as mock_modbus_unit,
)

from flexit_modbus import Flexit


def _u16(signed_value: int) -> int:
    """Encode a signed 16-bit int as its unsigned register word."""
    return signed_value & 0xFFFF


# Raw register words keyed by their (protocol) address; decoded view inline.
HOLDING: dict[int, int] = {
    8: 210,  # setpoints.target_temperature -> 21.0 °C
    17: 2,  # setpoints.fan_mode -> MEDIUM
}

INPUT: dict[int, int] = {
    9: 190,  # measurements.supply_air_temperature -> 19.0 °C
    11: _u16(-30),  # measurements.outdoor_air_temperature -> -3.0 °C
    8: 45,  # measurements.filter_running_hours -> 45 h (unsigned)
    14: 0,  # measurements.heat_exchanger_regulation -> 0 %
    15: 0,  # measurements.electric_heater_regulation -> 0 %
    13: 0,  # measurements.cooling_regulation -> 0 %
    27: 0,  # measurements.filter_alarm -> False
    28: 0,  # measurements.electric_heater_enabled -> False
    48: 2,  # measurements.actual_air_speed -> 2
}


@pytest.fixture
def flexit(mock_modbus_unit: MockModbusUnit) -> Flexit:
    """A ``Flexit`` device over the mock unit, preloaded with device values."""
    mock_modbus_unit.holding.update(HOLDING)
    mock_modbus_unit.input.update(INPUT)
    return Flexit(mock_modbus_unit)


@pytest.fixture
def unit(mock_modbus_unit: MockModbusUnit) -> MockModbusUnit:
    """The mock unit the ``flexit`` fixture reads and writes through.

    Request it alongside ``flexit`` to assert on the register store a write
    landed in, rather than reaching for the unit a component holds.
    """
    return mock_modbus_unit
