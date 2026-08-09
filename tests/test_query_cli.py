"""CLI argument parsing smoke tests (no real connection is made)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

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
