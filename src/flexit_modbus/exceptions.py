"""Exceptions raised by flexit-modbus."""

from __future__ import annotations


class FlexitValueValidationError(ValueError):
    """Raised when a value is outside its allowed domain for a write."""
