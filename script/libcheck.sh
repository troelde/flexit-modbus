#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python}"

cd "$ROOT_DIR"

if ! "$PYTHON_BIN" -m ruff --version >/dev/null 2>&1; then
    "$PYTHON_BIN" -m pip install \
        --root-user-action=ignore \
        "ruff>=0.15,<0.16"
fi

if ! "$PYTHON_BIN" -c "import build" >/dev/null 2>&1; then
    "$PYTHON_BIN" -m pip install \
        --root-user-action=ignore \
        build
fi

echo "==> Checking formatting"
"$PYTHON_BIN" -m ruff format --check .

echo "==> Running Ruff"
"$PYTHON_BIN" -m ruff check .

echo "==> Compiling sources"
"$PYTHON_BIN" -m compileall -q src tests

echo "==> Running tests"
"$ROOT_DIR/script/libtest.sh"

echo "==> Building package"
rm -rf "$ROOT_DIR/dist"
"$PYTHON_BIN" -m build

echo "==> All checks passed"