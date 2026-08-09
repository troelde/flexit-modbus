"""Neutral Flexit CI66 datapoint metadata.

This mirrors the shape of a typical ``modbus-connection``-based device
library's metadata: enough to describe a datapoint's unit, numeric domain,
and enum options without depending on any particular consumer (there is
nothing Home-Assistant-specific here).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Literal

ValueKind = Literal["number", "enum", "boolean"]


@dataclass(frozen=True)
class NumberMetadata:
    """Metadata for numeric Flexit values."""

    min_value: float | int | None = None
    max_value: float | int | None = None
    step: float | int | None = None
    digits: int | None = None
    unit: str | None = None


@dataclass(frozen=True)
class OptionMetadata:
    """Metadata for one discrete enum option."""

    key: str
    value: int
    label: str | None = None


@dataclass(frozen=True)
class EnumMetadata:
    """Metadata for selectable / discrete register values."""

    enum_type: type[IntEnum]
    options: tuple[OptionMetadata, ...]


@dataclass(frozen=True)
class BooleanMetadata:
    """Metadata for boolean register values."""

    false_key: str = "off"
    true_key: str = "on"


@dataclass(frozen=True)
class DatapointMetadata:
    """Neutral metadata for one Flexit datapoint."""

    value_kind: ValueKind
    description: str | None = None
    writable: bool = False
    number: NumberMetadata | None = None
    enum: EnumMetadata | None = None
    boolean: BooleanMetadata | None = None


def step_from_digits(digits: int | None) -> float | int | None:
    """Return the natural UI/write step from decimal precision."""
    if digits is None:
        return None
    if digits <= 0:
        return 1
    return 10**-digits


def attach_metadata(field: Any, metadata: DatapointMetadata) -> Any:
    """Attach Flexit metadata to a modbus-connection field."""
    field.flexit_metadata = metadata
    return field
