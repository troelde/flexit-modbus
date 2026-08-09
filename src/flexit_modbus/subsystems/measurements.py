"""Read-only sensor and status values (CI66 input registers, FC04)."""

from __future__ import annotations

from ..data_model import FlexitComponent, counter, flag, percent, reading, temperature


class Measurements(FlexitComponent):
    """The read-only input registers on the CI66 adapter."""

    register_space = "input"

    supply_air_temperature = temperature(
        9, description="Measured supply air temperature"
    )
    outdoor_air_temperature = temperature(
        11, description="Measured outdoor air temperature"
    )
    filter_running_hours = counter(
        8, unit="h", description="Filter running hours (unsigned)"
    )
    heat_exchanger_regulation = percent(
        14, description="Mechanical heat-recovery regulation level"
    )
    electric_heater_regulation = percent(
        15, description="Electric heater regulation level"
    )
    cooling_regulation = percent(13, description="Cooling regulation level")
    filter_alarm = flag(27, description="Filter alarm active")
    electric_heater_enabled = flag(
        28, description="Electric heater enabled (not necessarily heating)"
    )
    actual_air_speed = reading(48, description="Current fan speed reading")
