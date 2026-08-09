"""Neutral enumerations for the Flexit CI66 datapoints."""

from __future__ import annotations

from enum import IntEnum


class FanMode(IntEnum):
    """The fan-speed setting written to / read from holding register 8 (HR17).

    A raw value outside this range decodes to ``None`` (the CI66 adapter
    reports an out-of-range code as unknown rather than a defined speed).
    """

    OFF = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class SystemActivity(IntEnum):
    """The unit's derived overall activity, in the order it is resolved.

    Precedence, matching the CI66 adapter's own behavior: heating takes
    priority over cooling, which takes priority over heat recovery, which
    takes priority over plain ventilation (fan only).
    """

    OFF = 0
    FAN = 1
    HEAT_RECOVERY = 2
    COOLING = 3
    HEATING = 4
