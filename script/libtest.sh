#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"
MODBUS_CONNECTION_SRC="${MODBUS_CONNECTION_SRC:-/config/dev/modbus-connection/src}"

if [[ ! -d "$MODBUS_CONNECTION_SRC/modbus_connection" ]]; then
    echo "modbus-connection source not found: $MODBUS_CONNECTION_SRC" >&2
    echo "Set MODBUS_CONNECTION_SRC to the directory containing modbus_connection/." >&2
    exit 2
fi

if ! "$PYTHON_BIN" -c "import pytest, pytest_asyncio" >/dev/null 2>&1; then
    "$PYTHON_BIN" -m pip install "pytest>=8" "pytest-asyncio>=0.24"
fi

export PYTHONPATH="$ROOT_DIR/src:$MODBUS_CONNECTION_SRC${PYTHONPATH:+:$PYTHONPATH}"

cd "$ROOT_DIR"

exec "$PYTHON_BIN" -m pytest "$@"