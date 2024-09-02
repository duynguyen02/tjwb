# tjwb
![PyPI - Version](https://img.shields.io/pypi/v/tjwb)

`tjwb` is a Python library designed for water balance management in reservoirs. The library provides methods to
calculate inflow and outflow speeds of various components, such as pumps, box culverts, and valve overflows, based on water level and configuration...

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

If the difference between the subsequent capacity and the previous capacity is zero, then the inflow speed and outflow speed
are equal:

```
Subsequent Capacity - Previous Capacity = 0
```

In this case:

```
Inflow Speed = Outflow Speed
```

If the difference between the subsequent capacity and the previous capacity is negative, then the outflow speed is greater
than the inflow speed:

```
Subsequent Capacity - Previous Capacity < 0
```

In this case:

```
Outflow Speed > Inflow Speed
```

Conversely, if the difference between the subsequent capacity and the previous capacity is positive, then the inflow speed
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
import pandas as pd
from tjwb import (calculate, RequiredColumnsName, WaterLevelCapacityMappingColumnsName, PumpConfig, ValveOverflowConfig,
                  BoxCulvertConfig)

# Prepare your data
df = pd.DataFrame({
    'Datetime': ['2024-08-28 10:00:00', '2024-08-28 10:05:00'],
    'Water Level': [5.0, 5.5],
    'Pump.Pump-1': [1.0, 1.5],
    'BoxCulvert.BoxCulvert-1': [0.5, 0.7],
    'ValveOverflow.ValveOverflow-1': [0.3, 0.4],
    'ValveOverflow.ValveOverflow-2': [0.3, 0.4],
    'ValveOverflow.ValveOverflow-3': [0.3, 0.4],
})

water_level_capacity_mapping_df = pd.DataFrame({
    'Water Level': [5.0, 5.5],
    'Capacity': [1000, 1500]
})

# Define component configurations
pump_configs = [PumpConfig(column_name_prefix='Pump')]
box_culvert_configs = [BoxCulvertConfig(column_name_prefix='BoxCulvert', elevation=2.0, height=1.0)]
valve_overflow_configs = [ValveOverflowConfig(column_name_prefix='ValveOverflow', elevation=1.5, height=0.5)]

# Calculate results
result = calculate(
    _df=df,
    _water_level_capacity_mapping_df=water_level_capacity_mapping_df,
    water_level_capacity_mapping_columns_name=WaterLevelCapacityMappingColumnsName(),
    required_columns_name=RequiredColumnsName(),
    pump_configs=pump_configs,
    box_culvert_configs=box_culvert_configs,
    valve_overflow_configs=valve_overflow_configs
)

# Convert results to DataFrame
result_df = result.to_dataframe()
print(result_df)
```

## Main Classes and Functions

- **`calculate`**: The main function for calculating the inflow and outflow speeds based on the given configurations.
- **`TJWBResult`**: Holds the calculated results, including datetime, inflow speed, outflow speed, and outflow speeds for each
  component.
- **`RequiredColumnsName`**: Configuration for the required column names in the input DataFrame.
- **`WaterLevelCapacityMappingColumnsName`**: Configuration for the column names in the water level-capacity mapping
  DataFrame.
- **Component Configurations**:
    - `PumpConfig`
    - `BoxCulvertConfig`
    - `ValveOverflowConfig`

## Error Handling

The `tjwb` library includes various validation steps to ensure that the inputs are correct. Below are the common
scenarios where errors might be raised:

- **Invalid DataFrame Structure**:
    - If the main DataFrame (`_df`) or the Water Level Capacity Mapping DataFrame (`_water_level_capacity_mapping_df`)
      contains missing required columns, a `ValueError` will be raised.
    - If the Water Level Capacity Mapping DataFrame contains non-numeric data in the `water_level` or `capacity`
      columns, a `TypeError` will be raised.
    - If any required column in the main DataFrame contains null values, a `ValueError` will be raised.
    - If the `Datetime` column cannot be converted to a valid datetime format, a `ValueError` will be raised.

- **Component Configuration Errors**:
    - If the `column_name_prefix` of any component contains the character `'.'`, a `ValueError` will be raised, as this
      character is not allowed in column name prefixes.
    - If there are duplicate `column_name_prefix` values among the configured components, a `ValueError` will be raised.
    - If a column referenced in the component configuration does not exist or is not of numeric type, a `TypeError` will
      be raised.

- **Invalid Water Level to Capacity Mapping**:
    - If there is a mismatch between the water levels in the main DataFrame and the Water Level Capacity Mapping
      DataFrame, such that no valid capacity can be mapped, a `ValueError` will be raised.

- **Calculation Errors**:
    - If the calculated inflow or outflow speeds result in negative or NaN values, the library automatically converts
      these to zero using internal validation functions.

## License

This library is released under the MIT License.

## Contact

If you have any questions or issues, please open an issue on [GitHub](https://github.com/duynguyen02/tjwb/issues) or
email us at [duynguyen02.dev@gmail.com](mailto:duynguyen02.dev@gmail.com).
