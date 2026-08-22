# Agent Guide

See [README.md](README.md) for the library's scope, supported hardware, public API, and usage examples.

## Environment and Commands

- Use Python 3.12 or newer. For a normal editable development install, run `python -m pip install -e .` and install `pytest`, `pytest-asyncio`, `ruff`, and `build` as needed.
- The real-device CLI needs its backend extra: `python -m pip install -e ".[cli]"`. Run it with `python script/query.py HOST_OR_SERIAL_DEVICE`; it talks to hardware, unlike the test suite.
- Run a focused test first: `python -m pytest tests/test_device.py` or `python -m pytest tests/test_write.py -k temperature`.
- Run all tests with `python -m pytest`. Tests use `modbus_connection`'s in-memory mock and need no device, socket, or Modbus server.
- Format with `./script/format.sh`. Run the full formatting, lint, compile, test, and package-build sequence with `./script/libcheck.sh`.
- `script/libtest.sh` and therefore `script/libcheck.sh` expect a local `modbus-connection` source tree at `/config/dev/modbus-connection/src`. Set `MODBUS_CONNECTION_SRC=/path/to/modbus-connection/src` when it lives elsewhere. In an installed environment, use `python -m pytest` directly.

## Architecture and Conventions

- `src/flexit_modbus/flexit.py` owns the top-level `Flexit` facade and derived cross-subsystem behavior. `subsystems/setpoints.py` owns writable holding registers; `subsystems/measurements.py` owns read-only input registers.
- Define register decoding and metadata through the helpers in `data_model.py`; do not duplicate scaling, signedness, validation, or metadata at call sites. Keep consumer-neutral metadata in `metadata.py`.
- CI66 register numbers are 0-based protocol addresses. Temperatures are signed register values scaled by `0.1`. Preserve `None` for failed reads and unknown enum values.
- Keep all device I/O asynchronous and let callers inject a `ModbusUnit`; this library does not create or own the transport.
- A register change should update the owning subsystem and focused mock-backed tests. Extend `tests/conftest.py` with raw register words, then assert decoded values, writes, validation, metadata, or derived activity as appropriate.
- Use the existing fully typed Python 3.12 style. Ruff enforces `E`, `F`, `W`, `I`, `UP`, and `B`; avoid unrelated formatting or API changes.

## Contribution Flow

- Normal pull requests target `develop`. Only the repository's own `develop` branch may target `main`; see [.github/workflows/enforce-develop.yml](.github/workflows/enforce-develop.yml).
- Before handing off a change, run the narrowest relevant tests, then `python -m ruff check .` and `python -m ruff format --check .`. Run `./script/libcheck.sh` when the required local dependency checkout is available.