# TJWB
Python library used to calculate reservoir water balance.
#### Version: 1.0.0
### Installation
```
pip install tjwb
```

### Get started
#### The datasets that need to be prepared:
The dataset for correlating water level and reservoir capacity. The dataset includes two columns: Elevation and Storage.

| Elevation | Storage |
|-----------|---------|
| 19.00     | 0.000   |
| 19.01     | 0.000   |
| 19.02     | 0.001   |
| 19.03     | 0.001   |
| ...     | ...   |


The dataset contains time-series data with the following columns:

- `timestamp`: indicating the time of observation
- `water_level`: measured water level
- `boxdrain_<id>`: the opening degree of box drains (in meters), which may include multiple columns for different box drain IDs
- `valveoverflow_<id>`: the opening degree of valve overflow (in meters), which may include multiple columns for different valve overflow IDs
- `pump_<id>`: discharge rate of pumps (in m^3/s), which may include multiple columns for different pump IDs.


| timestamp  | water_level | boxdrain_cong1 | valveoverflow_tran1 | valveoverflow_tran2 | valveoverflow_tran3 | pump_01 |
|------------|-------------|----------------|---------------------|---------------------|---------------------|---------|
| 2014-01-01 | 25          | 0              | 0                   | 0                   | 0                   | 12      |
| 2014-01-02 | 25          | 0              | 0                   | 0                   | 0                   | 12      |
| 2014-01-03 | 25          | 0              | 0                   | 0                   | 0                   | 12      |
| 2014-01-04 | 25          | 0              | 0                   | 0                   | 0                   | 12      |
| 2014-01-05 | 25          | 0              | 0                   | 0                   | 0                   | 12      |

#### How to use TJWB to calculate water balance.
```Python
import pandas as pd
from tjwb import wb

pre_df = pd.read_csv('data_example.csv')
ets_df = pd.read_csv('elevation_to_storage_example.csv')

wb = wb.WB(
    ets_df,
    22.5, # boxdrain_elevation
    0.7, # boxdrain_height
    22, # valveoverflow_elevation
    3 # valveoverflow_height
)

df = wb.calculate(
    pre_df,
    3 # round to
)
```
#### The result may be as follows:
| timestamp   | water_level | boxdrain_cong1 | valveoverflow_tran1 | valveoverflow_tran2 | valveoverflow_tran3 | pump_01 | delta_T | storage | Q_out_total | boxdrainOutflow_cong1 | valveoverflowOutflow_tran1 | valveoverflowOutflow_tran2 | valveoverflowOutflow_tran3 | Q_in   |
|-------------|-------------|----------------|---------------------|---------------------|---------------------|---------|---------|---------|-------------|-----------------------|-----------------------------|-----------------------------|-----------------------------|---------|
| 2014-01-01  | 25.00       | 0              | 0                   | 0                   | 0                   | 12      | 0.0     | 2.22    | 12.000      | 0.000                 | 0.0                         | 0.0                         | 0.0                         | 0.000   |
| 2014-01-02  | 25.00       | 0              | 0                   | 0                   | 0                   | 12      | 86400.0 | 2.22    | 12.000      | 0.000                 | 0.0                         | 0.0                         | 0.0                         | 12.000  |
| 2014-01-03  | 25.00       | 0              | 0                   | 0                   | 0                   | 12      | 86400.0 | 2.22    | 12.000      | 0.000                 | 0.0                         | 0.0                         | 0.0                         | 12.000  |
| 2014-01-04  | 25.00       | 0              | 0                   | 0                   | 0                   | 12      | 86400.0 | 2.22    | 12.000      | 0.000                 | 0.0                         | 0.0                         | 0.0                         | 12.000  |
| 2014-01-05  | 25.00       | 0              | 0                   | 0                   | 0                   | 12      | 86400.0 | 2.22    | 12.000      | 0.000                 | 0.0                         | 0.0                         | 0.0                         | 12.000  |
| ...  | ...       | ...              | ...                   | ...                   | ...                   | ...      | ... | ...    | ...      | ...                 | ...                         | ...                         | ...                         | ...  |


### Functions to be developed in the future:
- Establish calculation for other types of drains, overflows, etc.