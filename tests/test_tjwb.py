import pytest
import pandas as pd
from math import isclose

from tjwb import PumpConfig, ValveOverflowConfig, BoxCulvertConfig, calculate, WaterLevelCapacityMappingColumnsName, \
    RequiredColumnsName, TJWBResult, ComponentConfig


def test_calculate_with_valid_data():
    df = pd.DataFrame({
        'Datetime': pd.date_range('2023-01-01', periods=5, freq='h'),
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Pump.Opening': [1, 1, 1, 1, 1],
        'ValveOverflow.Opening': [0.8, 0.8, 0.8, 0.8, 0.8],
        'BoxCulvert.Opening': [0.5, 0.5, 0.5, 0.5, 0.5]
    })

    water_level_capacity_mapping_df = pd.DataFrame({
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Capacity': [100, 200, 300, 400, 500]
    })

    pump_configs = [PumpConfig(column_name_prefix='Pump')]
    valve_overflow_configs = [ValveOverflowConfig(column_name_prefix='ValveOverflow', elevation=0.5, height=1.0)]
    box_culvert_configs = [BoxCulvertConfig(column_name_prefix='BoxCulvert', elevation=0.5, height=1.0)]

    result = calculate(
        df,
        water_level_capacity_mapping_df,
        WaterLevelCapacityMappingColumnsName(),
        RequiredColumnsName(),
        pump_configs=pump_configs,
        valve_overflow_configs=valve_overflow_configs,
        box_culvert_configs=box_culvert_configs
    )

    assert isinstance(result, TJWBResult)
    assert not result.inflow_speed.isnull().any()
    assert not result.outflow_speed.isnull().any()
    assert len(result.components_outflow_speed) == 3


def test_calculate_with_missing_columns():
    df = pd.DataFrame({
        'Datetime': pd.date_range('2023-01-01', periods=5, freq='h'),
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5]
    })

    water_level_capacity_mapping_df = pd.DataFrame({
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Capacity': [100, 200, 300, 400, 500]
    })

    with pytest.raises(ValueError):
        calculate(
            df,
            water_level_capacity_mapping_df,
            WaterLevelCapacityMappingColumnsName(),
            RequiredColumnsName(),
        )


def test_calculate_with_invalid_datetime():
    df = pd.DataFrame({
        'Datetime': ['invalid_date'] * 5,
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Pump.Opening': [1, 1, 1, 1, 1]
    })

    water_level_capacity_mapping_df = pd.DataFrame({
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Capacity': [100, 200, 300, 400, 500]
    })

    with pytest.raises(ValueError):
        calculate(
            df,
            water_level_capacity_mapping_df,
            WaterLevelCapacityMappingColumnsName(),
            RequiredColumnsName(),
            pump_configs=[PumpConfig(column_name_prefix='Pump')]
        )


def test_calculate_with_nan_values():
    df = pd.DataFrame({
        'Datetime': pd.date_range('2023-01-01', periods=5, freq='h'),
        'Water Level': [0.5, 1.0, None, 2.0, 2.5],
        'Pump.Opening': [1, 1, 1, 1, None]
    })

    water_level_capacity_mapping_df = pd.DataFrame({
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Capacity': [100, 200, 300, 400, 500]
    })

    with pytest.raises(ValueError):
        calculate(
            df,
            water_level_capacity_mapping_df,
            WaterLevelCapacityMappingColumnsName(),
            RequiredColumnsName(),
            pump_configs=[PumpConfig(column_name_prefix='Pump')]
        )


def test_calculate_with_component_config_validation():
    df = pd.DataFrame({
        'Datetime': pd.date_range('2023-01-01', periods=5, freq='h'),
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Invalid.Opening': [1, 1, 1, 1, 1]
    })

    water_level_capacity_mapping_df = pd.DataFrame({
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Capacity': [100, 200, 300, 400, 500]
    })

    class CustomConfig(ComponentConfig):
        pass

    with pytest.raises(TypeError):
        calculate(
            df,
            water_level_capacity_mapping_df,
            WaterLevelCapacityMappingColumnsName(),
            RequiredColumnsName(),
            pump_configs=[CustomConfig(column_name_prefix='Invalid')]
        )


def test_calculate_with_no_components_configured():
    df = pd.DataFrame({
        'Datetime': pd.date_range('2023-01-01', periods=5, freq='h'),
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5]
    })

    water_level_capacity_mapping_df = pd.DataFrame({
        'Water Level': [0.5, 1.0, 1.5, 2.0, 2.5],
        'Capacity': [100, 200, 300, 400, 500]
    })

    with pytest.raises(ValueError):
        calculate(
            df,
            water_level_capacity_mapping_df,
            WaterLevelCapacityMappingColumnsName(),
            RequiredColumnsName()
        )


def test_calculate_with_box_culvert_and_valve_overflow():
    df = pd.DataFrame({
        'Datetime': pd.date_range('2023-01-01', periods=5, freq='h'),
        'Water Level': [1.5, 2.0, 2.5, 3.0, 3.5],
        'BoxCulvert.Opening': [1, 1, 1, 1, 1],
        'ValveOverflow.Opening': [1, 1, 1, 1, 1]
    })

    water_level_capacity_mapping_df = pd.DataFrame({
        'Water Level': [1.5, 2.0, 2.5, 3.0, 3.5],
        'Capacity': [200, 300, 400, 500, 600]
    })

    box_culvert_configs = [BoxCulvertConfig(column_name_prefix='BoxCulvert', elevation=1.0, height=2.0)]
    valve_overflow_configs = [ValveOverflowConfig(column_name_prefix='ValveOverflow', elevation=1.0, height=2.0)]

    result = calculate(
        df,
        water_level_capacity_mapping_df,
        WaterLevelCapacityMappingColumnsName(),
        RequiredColumnsName(),
        box_culvert_configs=box_culvert_configs,
        valve_overflow_configs=valve_overflow_configs
    )

    assert isclose(result.outflow_speed.sum(), sum(result.outflow_speed), rel_tol=1e-5)
    assert len(result.components_outflow_speed) == 2


def test_calculate_with_nearest_mapping():
    df = pd.DataFrame({
        'Datetime': pd.date_range('2023-01-01', periods=5, freq='h'),
        'Water Level': [1.5, 2.0, 2.5, 3.0, 3.4],  # Invalid WaterLevel
        'BoxCulvert.Opening': [1, 1, 1, 1, 1],
        'ValveOverflow.Opening': [1, 1, 1, 1, 1]
    })

    water_level_capacity_mapping_df = pd.DataFrame({
        'Water Level': [1.5, 2.0, 2.5, 3.0, 3.5],
        'Capacity': [200, 300, 400, 500, 600]
    })

    box_culvert_configs = [BoxCulvertConfig(column_name_prefix='BoxCulvert', elevation=1.0, height=2.0)]
    valve_overflow_configs = [ValveOverflowConfig(column_name_prefix='ValveOverflow', elevation=1.0, height=2.0)]

    result = calculate(
        df,
        water_level_capacity_mapping_df,
        WaterLevelCapacityMappingColumnsName(),
        RequiredColumnsName(),
        box_culvert_configs=box_culvert_configs,
        valve_overflow_configs=valve_overflow_configs,
        nearest_mapping=True
    )

    assert isclose(result.outflow_speed.sum(), sum(result.outflow_speed), rel_tol=1e-5)
    assert len(result.components_outflow_speed) == 2
