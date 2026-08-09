# `flexit-modbus` Python library

[![CI](https://github.com/home-assistant-libs/flexit-modbus/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/home-assistant-libs/flexit-modbus/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/flexit-modbus.svg)](https://pypi.org/project/flexit-modbus/)
[![Python](https://img.shields.io/pypi/pyversions/flexit-modbus.svg)](https://pypi.org/project/flexit-modbus/)
[![License](https://img.shields.io/github/license/home-assistant-libs/flexit-modbus.svg)](LICENSE)

`flexit-modbus` is an asynchronous Python library for reading from and
writing to a **Flexit air handling unit fitted with a CI66 Modbus adapter**
over Modbus.

## Purpose and scope of this library

The library `flexit-modbus`:

- is intended for operational monitoring and basic control (target
  temperature, fan speed) of an already commissioned Flexit unit. It does
  _NOT_ attempt to reproduce every menu, parameter, or register the unit
  supports — only the datapoints exposed by the CI66 adapter's Modbus map
  that are useful for day-to-day monitoring and control.
- contains the CI66 adapter's data model. It knows the available holding and
  input registers, their data types and metadata, and the rules required for
  safe reads and writes (e.g. the 10-30 °C setpoint range).
- does _NOT_ create or own the Modbus transport. Applications utilizing the
  library provide a
  [`modbus_connection.ModbusUnit`](https://github.com/home-assistant-libs/modbus-connection)
  and may use any backend supported by `modbus-connection` (pymodbus,
  tmodbus, ...).

## Data provided by the library

`flexit-modbus` provides:

- the current and target supply-air temperature, and the outdoor air
  temperature,
- the fan mode (off/low/medium/high) and the actual air-speed reading,
- electric heater and cooling regulation levels (0-100%) and whether the
  electric heater is currently enabled,
- mechanical heat-recovery regulation level,
- filter running hours and the filter alarm state,
- a derived overall activity (heating, cooling, heat recovery, fan, or off),
  following the unit's own precedence,
- neutral datapoint metadata such as unit, min/max, step, and writable state,
- validated writes for the target temperature (10-30 °C) and fan mode.

## Supported hardware

| Device                                | Adapter | Comments                        |
| :------------------------------------ | :-----: | :------------------------------- |
| Flexit air handling units (Nordic AC) |  CI66   | Modbus RTU via the CI66 adapter |

Other Flexit units using the same CI66 Modbus register map are expected to
work, since the adapter (not the ventilation unit itself) defines the
Modbus interface used here.

## Usage

```python
from modbus_connection import ModbusTcpParams
from modbus_connection.pymodbus import PymodbusConnection

from flexit_modbus import Flexit, FanMode

connection = PymodbusConnection(ModbusTcpParams(host="192.168.1.50", port=502))
await connection.connect()

device = Flexit(connection.for_unit(1))
await device.async_update()

print(device.target_temperature, device.measurements.supply_air_temperature)
print(device.activity)

await device.async_set_target_temperature(21.5)
await device.async_set_fan_mode(FanMode.HIGH)
```

A command-line query tool is also provided; install the `cli` extra and run:

```console
$ pip install flexit-modbus[cli]
$ python script/query.py tcp 192.168.1.50 --unit 1
```

## Testing and validation

The test suite runs entirely against the in-memory mock backend that ships
with `modbus-connection` — no real CI66 adapter or Modbus server is needed.

## Documentation, development and contribution guidelines

See `script/format.sh`, `script/libcheck.sh`, and `script/libtest.sh` for the
local development workflow (formatting, linting, and running tests). Pull
requests are made against the `develop` branch; `main` tracks released
versions only.
