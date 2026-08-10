"""The top-level ``Flexit`` device object."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection.model import ComponentGroup

from .device_info import DeviceInformation
from .enums import FanMode, SystemActivity
from .subsystems import Measurements, Setpoints

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

info = DeviceInformation()


class Flexit:
    """A Flexit AC unit behind a CI66 Modbus adapter.

    Construct with a ``modbus_connection.ModbusUnit``, call
    ``await device.async_update()``, then read values as plain attributes::

        device.setpoints.target_temperature
        device.measurements.supply_air_temperature
        device.activity

    Writes go through the owning component, e.g.
    ``await device.setpoints.write("fan_mode", FanMode.HIGH)``, or the
    convenience methods below.
    """

    info = info

    def __init__(self, unit: ModbusUnit) -> None:
        self.setpoints = Setpoints(unit)
        self.measurements = Measurements(unit)
        self._group = ComponentGroup(unit, [self.setpoints, self.measurements])

    async def async_update(self) -> None:
        """Read every sub-system in as few Modbus requests as possible."""
        await self._group.async_update()

    async def async_set_target_temperature(self, value: float) -> None:
        """Write a new target temperature (validated against 10-30 °C)."""
        await self.setpoints.write("target_temperature", value)

    async def async_set_fan_mode(self, fan_mode: FanMode) -> None:
        """Write a new fan mode."""
        await self.setpoints.write("fan_mode", fan_mode)

    @property
    def target_temperature(self) -> float | None:
        """The current target temperature setpoint, in °C."""
        return self.setpoints.target_temperature

    @property
    def fan_mode(self) -> FanMode | None:
        """The current fan mode, or ``None`` for an unrecognized code."""
        return self.setpoints.fan_mode

    @property
    def activity(self) -> SystemActivity | None:
        """The unit's derived overall activity.

        Precedence: heating, then cooling, then heat recovery, then plain
        ventilation (fan only), else off. Returns ``None`` if any of the
        underlying readings (heater, cooling, heat-recovery regulation, or
        actual air speed) could not be read.
        """
        heating = self.measurements.electric_heater_regulation
        cooling = self.measurements.cooling_regulation
        heat_recovery = self.measurements.heat_exchanger_regulation
        air_speed = self.measurements.actual_air_speed

        if None in (heating, cooling, heat_recovery, air_speed):
            return None
        if heating:
            return SystemActivity.HEATING
        if cooling:
            return SystemActivity.COOLING
        if heat_recovery:
            return SystemActivity.HEAT_RECOVERY
        if air_speed:
            return SystemActivity.FAN
        return SystemActivity.OFF
