"""flexit-modbus — read and control a Flexit AC unit over Modbus.

Construct ``Flexit(unit)`` with a ``modbus_connection.ModbusUnit``, call
``await device.async_update()``, then read its sub-systems as normal Python
objects::

    device.setpoints.target_temperature
    device.measurements.supply_air_temperature
    device.activity

Sub-systems live in ``subsystems``: ``Setpoints`` (writable holding
registers) and ``Measurements`` (read-only input registers). Neutral
datapoint metadata and the ``modbus_connection.model`` field wrappers live
in ``data_model`` and ``metadata``.
"""

from .data_model import FlexitComponent
from .device_info import DeviceInformation
from .enums import FanMode, SystemActivity
from .exceptions import FlexitValueValidationError
from .flexit import Flexit
from .metadata import (
    BooleanMetadata,
    DatapointMetadata,
    EnumMetadata,
    NumberMetadata,
    OptionMetadata,
)
from .subsystems import MAX_TEMPERATURE, MIN_TEMPERATURE, Measurements, Setpoints

__all__ = [
    "MAX_TEMPERATURE",
    "MIN_TEMPERATURE",
    "BooleanMetadata",
    "DatapointMetadata",
    "DeviceInformation",
    "EnumMetadata",
    "FanMode",
    "Flexit",
    "FlexitComponent",
    "FlexitValueValidationError",
    "Measurements",
    "NumberMetadata",
    "OptionMetadata",
    "Setpoints",
    "SystemActivity",
]
