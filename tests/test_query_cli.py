"""CLI argument parsing smoke tests (no real connection is made)."""

from __future__ import annotations

import importlib.util
import sys
from argparse import Namespace
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from modbus_connection import ModbusError
from modbus_connection.mock import MockModbusConnection, MockModbusUnit

from flexit_modbus import Flexit

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "script" / "query.py"


def _load_query_module():
    spec = importlib.util.spec_from_file_location("flexit_query_cli", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def query_module():
    return _load_query_module()


def test_parses_tcp_target(query_module) -> None:
    args = query_module._parse_args(["192.168.1.50"])
    assert args.target == "192.168.1.50"
    assert args.transport == "tcp"
    assert args.unit == 1


def test_parses_serial_transport(query_module) -> None:
    args = query_module._parse_args(
        ["/dev/ttyUSB0", "--transport", "serial", "--unit", "2"]
    )
    assert args.target == "/dev/ttyUSB0"
    assert args.transport == "serial"
    assert args.unit == 2


def test_help_exits_cleanly(query_module) -> None:
    with pytest.raises(SystemExit) as exc:
        query_module._parse_args(["--help"])
    assert exc.value.code == 0


async def test_print_renders_off_activity(
    query_module,
    flexit: Flexit,
    unit: MockModbusUnit,
    capsys: pytest.CaptureFixture[str],
) -> None:
    unit.input[48] = 0
    await flexit.async_update()
    query_module._print(flexit)
    assert "Derived activity: off" in capsys.readouterr().out


async def test_run_reads_prints_counts_and_closes(
    query_module,
    flexit: Flexit,
    unit: MockModbusUnit,
    mock_modbus_connection: MockModbusConnection,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    async def connect_from_args(args: Namespace) -> MockModbusConnection:
        return mock_modbus_connection

    monkeypatch.setattr(query_module, "connect_from_args", connect_from_args)
    unit.input[48] = 0

    assert await query_module._run(Namespace(unit=1)) == 0
    output = capsys.readouterr().out
    assert "Setpoints" in output
    assert "Measurements" in output
    assert "Derived activity: off" in output
    assert "3 Modbus reads" in output
    assert not mock_modbus_connection.connected


async def test_run_connection_error_returns_failure(
    query_module,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    async def connect_from_args(args: Namespace) -> MockModbusConnection:
        raise ModbusError("connection unavailable")

    monkeypatch.setattr(query_module, "connect_from_args", connect_from_args)

    assert await query_module._run(Namespace(unit=1)) == 1
    assert "Could not connect: connection unavailable" in capsys.readouterr().err


async def test_run_read_error_returns_failure_and_closes(
    query_module,
    mock_modbus_connection: MockModbusConnection,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    async def connect_from_args(args: Namespace) -> MockModbusConnection:
        return mock_modbus_connection

    class FailingFlexit:
        def __init__(self, unit) -> None:
            pass

        async def async_update(self) -> None:
            raise ModbusError("read failed")

    close = AsyncMock(wraps=mock_modbus_connection.close)
    monkeypatch.setattr(query_module, "connect_from_args", connect_from_args)
    monkeypatch.setattr(query_module, "Flexit", FailingFlexit)
    monkeypatch.setattr(mock_modbus_connection, "close", close)

    assert await query_module._run(Namespace(unit=1)) == 1
    assert "Error reading device: read failed" in capsys.readouterr().err
    close.assert_awaited_once_with()
