#!/usr/bin/env python3

"""Query a Flexit AC unit over Modbus and print every value.

Connects over Modbus (TCP, UDP, TLS, or a serial/USB port), reads the whole
device once, and dumps every sub-system's values to the terminal. Handy for
checking a real unit's CI66 adapter without any other application involved.

The library only needs the connection protocol; this script uses whichever
backend is installed (tmodbus or pymodbus), so install the ``cli`` extra
first.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
import time

from modbus_connection import ModbusError
from modbus_connection.cli_helper import (
    CountingUnit,
    add_connection_args,
    connect_from_args,
    print_component,
)

from flexit_modbus import Flexit

# (label, attribute name on Flexit) — the order in which sections are printed.
SECTIONS: list[tuple[str, str]] = [
    ("Setpoints", "setpoints"),
    ("Measurements", "measurements"),
]


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    add_connection_args(parser)
    parser.add_argument(
        "--unit",
        type=int,
        default=1,
        help="Modbus unit/station address (default: 1)",
    )
    return parser.parse_args(argv)


def _print(device: Flexit) -> None:
    for label, attr in SECTIONS:
        print()
        print_component(getattr(device, attr), title=label)
    print()
    print(
        f"Derived activity: {device.activity.name.lower() if device.activity else '—'}"
    )


async def _run(args: argparse.Namespace) -> int:
    try:
        connection = await connect_from_args(args)
    except ModbusError as err:
        print(f"Could not connect: {err}", file=sys.stderr)
        return 1
    counting = CountingUnit(connection.for_unit(args.unit))
    try:
        device = Flexit(counting)
        start = time.monotonic()
        await device.async_update()
        elapsed = time.monotonic() - start
    except ModbusError as err:
        print(f"Error reading device: {err}", file=sys.stderr)
        return 1
    finally:
        await connection.close()
    _print(device)
    print(f"\nQueried in {elapsed * 1000:.0f} ms ({counting.reads} Modbus reads)")
    return 0


def main() -> int:
    return asyncio.run(_run(_parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
