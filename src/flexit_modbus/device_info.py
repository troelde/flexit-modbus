"""Static device identity for a Flexit AC unit with a CI66 Modbus adapter.

The CI66 adapter does not expose an identity/serial register over Modbus, so
this is a small static description rather than something read from the device.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceInformation:
    """Static identity for a Flexit AC unit behind a CI66 adapter."""

    manufacturer: str = "Flexit"
    model: str = "Flexit AC unit (CI66 Modbus adapter)"
