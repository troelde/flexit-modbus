"""Flexit-specific field helpers layered on ``modbus_connection.model``.

The CI66 Modbus adapter is addressed directly by 0-based protocol register
numbers (unlike some manufacturer documentation styles that use offset
reference numbers); the addresses used here match the legacy integration
this library replaces.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import IntEnum
from typing import Any

from modbus_connection.model import (
    Component,
    boolean as _modbus_boolean,
    enum as _modbus_enum,
    gauge as _modbus_gauge,
    integer as _modbus_integer,
)

from .exceptions import FlexitValueValidationError
from .metadata import (
    BooleanMetadata,
    DatapointMetadata,
    EnumMetadata,
    NumberMetadata,
    OptionMetadata,
    attach_metadata,
    step_from_digits,
)

# The CI66 has no documented sentinel for "no sensor" like some other
# manufacturers; a failed read simply comes back as ``None`` from
# modbus-connection's own error handling, so no NaN value is declared here.


def _number_validator(
    *,
    min_value: float | int | None,
    max_value: float | int | None,
) -> Callable[[Any], Any]:
    """Return a write validator enforcing ``min_value``/``max_value``."""

    def validate(value: Any) -> Any:
        number = float(value)
        if min_value is not None and number < min_value:
            raise FlexitValueValidationError(
                f"Value {value} is below minimum {min_value}"
            )
        if max_value is not None and number > max_value:
            raise FlexitValueValidationError(
                f"Value {value} is above maximum {max_value}"
            )
        return value

    return validate


def _with_number_validator(
    writable: bool | Callable[[Any], Any],
    *,
    min_value: float | int | None,
    max_value: float | int | None,
) -> bool | Callable[[Any], Any]:
    """Return ``writable`` as-is, or wrapped with a range-validating callable."""
    if not writable:
        return False
    if callable(writable):
        return writable
    if min_value is None and max_value is None:
        return True
    return _number_validator(min_value=min_value, max_value=max_value)


def temperature(
    address: int,
    *,
    writable: bool = False,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    digits: int = 1,
    description: str | None = None,
) -> Any:
    """A signed, 0.1-scaled temperature register, in degrees Celsius."""
    effective_writable = _with_number_validator(
        writable, min_value=min_value, max_value=max_value
    )
    field = _modbus_gauge(
        address,
        0.1,
        signed=True,
        writable=effective_writable,
        unit="°C",
    )
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            description=description,
            writable=bool(writable),
            number=NumberMetadata(
                min_value=min_value,
                max_value=max_value,
                step=step_from_digits(digits),
                digits=digits,
                unit="°C",
            ),
        ),
    )


def percent(
    address: int,
    *,
    signed: bool = True,
    description: str | None = None,
) -> Any:
    """A signed, unscaled 0-100% regulation-level register."""
    field = _modbus_integer(address, signed=signed, unit="%")
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            description=description,
            number=NumberMetadata(
                min_value=0, max_value=100, step=1, digits=0, unit="%"
            ),
        ),
    )


def counter(
    address: int,
    *,
    unit: str | None = None,
    description: str | None = None,
) -> Any:
    """An unsigned counter register (e.g. running hours)."""
    field = _modbus_integer(address, signed=False, unit=unit)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            description=description,
            number=NumberMetadata(min_value=0, step=1, digits=0, unit=unit),
        ),
    )


def reading(
    address: int,
    *,
    unit: str | None = None,
    description: str | None = None,
) -> Any:
    """A signed, unscaled integer register (e.g. a raw speed reading)."""
    field = _modbus_integer(address, signed=True, unit=unit)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            description=description,
            number=NumberMetadata(step=1, digits=0, unit=unit),
        ),
    )


def flag(address: int, *, description: str | None = None) -> Any:
    """A 0/1 register decoding to a native ``bool``."""
    field = _modbus_boolean(address)
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="boolean",
            description=description,
            boolean=BooleanMetadata(),
        ),
    )


def enum_register[E: IntEnum](
    address: int,
    enum_type: type[E],
    *,
    writable: bool = False,
    description: str | None = None,
) -> Any:
    """A register mapped to an ``IntEnum``; an out-of-range code decodes to ``None``."""
    field = _modbus_enum(address, enum_type, writable=writable)
    options = tuple(
        OptionMetadata(key=member.name.lower(), value=int(member))
        for member in enum_type
    )
    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="enum",
            description=description,
            writable=writable,
            enum=EnumMetadata(enum_type=enum_type, options=options),
        ),
    )


class FlexitComponent(Component):
    """A Flexit CI66 sub-system: a fixed, small block of registers."""

    max_span = 50
