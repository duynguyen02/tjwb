from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from tjwb.columns_constant import *
from tjwb.dataset import Dataset, ComponentConfig
from tjwb.tjwb import dataset_to_dataframe, validate_time_series, validate_columns_size, get_capacity, map_capacity, \
    calculate_box_culvert_outflow, calculate_valve_overflow_outflow, calculate_pumps_outflow, \
    calculate_box_culverts_outflow, calculate_valve_overflows_outflow, calculate


# Helper function to create a sample dataset
def create_sample_dataset():
    dataset = Dataset()
    dataset.time_series([datetime(2023, 1, 1), datetime(2023, 1, 2)])
    dataset.water_level([2.0, 2.1])
    dataset.pump("pump1", [0.5, 0.6])
    dataset.box_culvert("culvert1", ComponentConfig(1.0, 2.0), [0.7, 0.8])
    dataset.valve_overflow("overflow1", ComponentConfig(1.0, 2.0), [[0.4, 0.3], [0.5, 0.4]])
    return dataset


# Test case for dataset_to_dataframe
def test_dataset_to_dataframe():
    dataset = create_sample_dataset()
    df = dataset_to_dataframe(dataset)
    assert TIME_SERIES in df.columns
    assert WATER_LEVEL in df.columns
    assert f"{PUMP}.pump1" in df.columns
    assert f"{BOX_CULVERT}.culvert1" in df.columns
    assert f"{VALVE_OVERFLOW}.overflow1.0" in df.columns


# Test case for validate_time_series
def test_validate_time_series():
    dataset = create_sample_dataset()
    df = dataset_to_dataframe(dataset)
    validate_time_series(df)

    # Check for non-increasing time series
    df[TIME_SERIES] = [datetime(2023, 1, 2), datetime(2023, 1, 1)]
    with pytest.raises(ValueError, match="The time series is not strictly increasing."):
        validate_time_series(df)


# Test case for validate_columns_size
def test_validate_columns_size():
    dataset = create_sample_dataset()
    df = dataset_to_dataframe(dataset)

    # Check for inconsistent column size
    df[WATER_LEVEL] = pd.Series([2.0])
    print(df)
    with pytest.raises(ValueError,
                       match="The column 'WaterLevel' does not have the same size as the 'TimeSeries' column."):
        validate_columns_size(df)


# Test case for get_capacity
def test_get_capacity():
    water_level_capacity_map = {2.0: 100, 3.0: 200}
    assert get_capacity(2.0, water_level_capacity_map, False) == 100
    assert np.isnan(get_capacity(1.5, water_level_capacity_map, False))
    assert get_capacity(1.5, water_level_capacity_map, True) == 100


# Test case for map_capacity
def test_map_capacity():
    dataset = create_sample_dataset()
    df = dataset_to_dataframe(dataset)
    water_level_capacity_map = {2.0: 100, 2.1: 200}
    map_capacity(df, water_level_capacity_map, nearest_mapping=True)
    assert df[CAPACITY].iloc[0] == 100
    assert df[CAPACITY].iloc[1] == 200

    # Test for missing values with nearest_mapping=False
    with pytest.raises(ValueError, match="There are missing values in the 'Capacity' column."):
        map_capacity(df, {2.0: 100}, nearest_mapping=False)


# Test case for calculate_box_culvert_outflow
def test_calculate_box_culvert_outflow():
    outflow = calculate_box_culvert_outflow(2.5, 1.0, 2.0, 1.0)
    assert outflow > 0  # Check if the output is valid
    assert calculate_box_culvert_outflow(0.5, 1.0, 2.0, 1.0) == 0  # Should return 0


# Test case for calculate_valve_overflow_outflow
def test_calculate_valve_overflow_outflow():
    outflow = calculate_valve_overflow_outflow(2.5, 1.0, 2.0, 1.0)
    assert outflow > 0
    assert calculate_valve_overflow_outflow(0.5, 1.0, 2.0, 1.0) == 0  # Should return 0


# Test case for calculate_pumps_outflow
def test_calculate_pumps_outflow():
    dataset = create_sample_dataset()
    df = dataset_to_dataframe(dataset)
    df[OUTFLOW] = 0.0
    calculate_pumps_outflow(df)
    assert OUTFLOW in df.columns
    assert df[OUTFLOW].iloc[0] == 0.5
    assert df[OUTFLOW].iloc[1] == 0.6


# Test case for calculate_box_culverts_outflow
def test_calculate_box_culverts_outflow():
    dataset = create_sample_dataset()
    df = dataset_to_dataframe(dataset)
    df[OUTFLOW] = 0.0
    calculate_box_culverts_outflow(df, dataset)
    assert f"{OUT_BOX_CULVERT}.culvert1" in df.columns
    assert df[OUTFLOW].iloc[0] > 0


# Test case for calculate_valve_overflows_outflow
def test_calculate_valve_overflows_outflow():
    dataset = create_sample_dataset()
    df = dataset_to_dataframe(dataset)
    df[OUTFLOW] = 0.0
    calculate_valve_overflows_outflow(df, dataset)
    assert f"{OUT_VALVE_OVERFLOW}.overflow1.0" in df.columns
    assert df[OUTFLOW].iloc[0] > 0


# Test case for calculate
def test_calculate():
    dataset = create_sample_dataset()
    water_level_capacity_map = {2.0: 100, 2.1: 200}
    df = calculate(dataset, water_level_capacity_map)
    assert INTERVAL in df.columns
    assert INFLOW in df.columns
    assert OUTFLOW in df.columns
