"""Writable operator setpoints (CI66 holding registers, FC03/FC16)."""

from __future__ import annotations

from ..data_model import FlexitComponent, enum_register, temperature
from ..enums import FanMode

MIN_TEMPERATURE = 10.0
MAX_TEMPERATURE = 30.0


class Setpoints(FlexitComponent):
    """The operator-writable holding registers on the CI66 adapter."""

    register_space = "holding"

    target_temperature = temperature(
        8,
        writable=True,
        min_value=MIN_TEMPERATURE,
        max_value=MAX_TEMPERATURE,
        description="Requested supply/room setpoint temperature",
    )
    fan_mode = enum_register(
        17,
        FanMode,
        writable=True,
        description="Fan speed setting (off/low/medium/high)",
    )
