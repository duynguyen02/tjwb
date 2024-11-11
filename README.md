# tjwb

![PyPI - Version](https://img.shields.io/pypi/v/tjwb)

`tjwb` is a Python library designed for water balance management in reservoirs. The library provides methods to
calculate inflow and outflow speeds of various components, such as pumps, box culverts, and valve overflows, based on
water level and configuration...

## Overview

```
Subsequent Capacity = Previous Capacity + (Inflow Speed * ΔT) - (Outflow Speed * ΔT)
```

Where:

- **Subsequent Capacity**: The capacity of the reservoir after the current time step.
- **Previous Capacity**: The capacity of the reservoir before the current time step.
- **Inflow Speed**: The rate at which water is entering the reservoir.
- **Outflow Speed**: The rate at which water is leaving the reservoir.
- **ΔT**: The time step or interval over which the inflow and outflow are measured.

If the difference between the subsequent capacity and the previous capacity is zero, then the inflow speed and outflow
speed
are equal:

```
Subsequent Capacity - Previous Capacity = 0
```

In this case:

```
Inflow Speed = Outflow Speed
```

If the difference between the subsequent capacity and the previous capacity is negative, then the outflow speed is
greater
than the inflow speed:

```
Subsequent Capacity - Previous Capacity < 0
```

In this case:

```
Outflow Speed > Inflow Speed
```

Conversely, if the difference between the subsequent capacity and the previous capacity is positive, then the inflow
speed
is greater than the outflow speed:

```
Subsequent Capacity - Previous Capacity > 0
```

In this case:

```
Inflow Speed > Outflow Speed
```

## Installation

To install the library, use pip:

```bash
pip install tjwb
```

## Usage

### Basic Example

```python
from datetime import datetime
from tjwb.dataset import Dataset, ComponentConfig
from tjwb.tjwb import calculate

dataset = (
    Dataset()
    .time_series([datetime(2023, 1, 1), datetime(2023, 1, 2)])
    .water_level([2.0, 3.0])
    .pump("pump1", [0.5, 0.6])
    .pump("pump2", [0.4, 0.4])
    .box_culvert("culvert1", ComponentConfig(elevation=1.0, height=2.0), [0.7, 0.8])
    .valve_overflow(
        "overflow1", ComponentConfig(elevation=1.0, height=2.0), [
            [0.4, 0.3],  # port 0
            [0.4, 0.3],  # port 1
            [0.4, 0.3],  # port 2
        ]
    )
)

result_df = calculate(
    dataset=dataset,
    water_level_capacity_map={2.0: 100, 3.0: 200},
    round_to=None,
    nearest_mapping=False
)
```
## License

This library is released under the MIT License.

## Contact

If you have any questions or issues, please open an issue on [GitHub](https://github.com/duynguyen02/tjwb/issues) or
email us at [duynguyen02.dev@gmail.com](mailto:duynguyen02.dev@gmail.com).
