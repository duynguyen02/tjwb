import math
from typing import Dict, Optional

import numpy as np
import pandas as pd

from tjwb.columns_constant import *
from tjwb.dataset import Dataset, ComponentConfig


def dataset_to_dataframe(dataset: Dataset):
    dataset_dict = {
        TIME_SERIES: dataset.get_time_series(),
        WATER_LEVEL: dataset.get_water_level(),
    }
    for pump_id, values in dataset.get_pumps().items():
        dataset_dict[f'{PUMP}.{pump_id}'] = values

    for box_culvert_id, (config, values) in dataset.get_box_culverts().items():
        dataset_dict[f'{BOX_CULVERT}.{box_culvert_id}'] = values

    for valve_overflow_id, (config, values) in dataset.get_valve_overflows().items():
        for i, val in enumerate(values):
            dataset_dict[f'{VALVE_OVERFLOW}.{valve_overflow_id}.{i}'] = val
            
    for custom_outflow_id, values in dataset.get_custom_outflows().items():
        dataset_dict[f'{CUSTOM}.{custom_outflow_id}'] = values
        
    if dataset.get_capacity() is not None:
        dataset_dict[CAPACITY] = dataset.get_capacity()

    df = pd.DataFrame(dataset_dict)
    df[TIME_SERIES] = pd.to_datetime(df[TIME_SERIES])
    return df


def validate_time_series(df: pd.DataFrame):
    if not df[TIME_SERIES].is_monotonic_increasing:
        raise ValueError("The time series is not strictly increasing.")

    time_diffs = df[TIME_SERIES].diff().dropna()
    if not time_diffs.nunique() == 1:
        raise ValueError("The intervals between datetimes are not consistent.")


def validate_columns_size(df: pd.DataFrame):
    time_series_size = len(df[TIME_SERIES])
    for column in df.columns:
        if column != TIME_SERIES and df[column].count() != time_series_size:
            raise ValueError(f"The column '{column}' does not have the same size as the 'TimeSeries' column.")


def validate_dataframe(df: pd.DataFrame):
    validate_time_series(df)
    validate_columns_size(df)


def get_capacity(water_level: float, water_level_capacity_map: Dict[float, float], nearest_mapping: bool):
    if water_level in water_level_capacity_map:
        return water_level_capacity_map[water_level]

    if nearest_mapping:
        nearest_key = min(water_level_capacity_map.keys(), key=lambda x: abs(x - water_level))
        return water_level_capacity_map[nearest_key]

    return np.nan


def map_capacity(df: pd.DataFrame, water_level_capacity_map: Dict[float, float], nearest_mapping: bool):
    df[CAPACITY] = df[WATER_LEVEL].apply(lambda x: get_capacity(x, water_level_capacity_map, nearest_mapping))
    if df[CAPACITY].isna().any():
        raise ValueError(
            "There are missing values in the 'Capacity' column. Consider setting 'nearest_mapping=True' "
            "to fill missing values with the nearest available capacity.")
    return df


def calculate_box_culvert_outflow(
        water_level: float,
        elevation: float,
        height: float,
        opening_value: float
):
    if water_level - elevation < 0:
        return 0
    elif (water_level - elevation) >= 1.5 * opening_value:
        term = (2 * 9.81 * ((water_level - elevation) - 0.63 * opening_value))
        return 0.63 * 0.94 * height * opening_value * math.sqrt(term)
    else:
        return 0.36 * height * math.sqrt(2 * 9.81 * (water_level - elevation) ** 3)


def calculate_valve_overflow_outflow(
        water_level: float,
        elevation: float,
        height: float,
        opening_value: float
):
    if water_level < elevation:
        return 0
    elif (water_level - elevation) >= 1.5 * opening_value:
        term = (2 * 9.81 * ((water_level - elevation) - 0.63 * opening_value))
        return 0.63 * 0.94 * height * opening_value * math.sqrt(term)
    else:
        return 0.36 * height * math.sqrt(2 * 9.81 * (water_level - elevation) ** 3)


def calculate_pumps_outflow(df: pd.DataFrame):
    for index, row in df.iterrows():
        pump_columns = [col for col in df.columns if col.startswith(PUMP)]
        outflow_sum = sum(row[pump] for pump in pump_columns)
        df.at[index, OUTFLOW] = outflow_sum
    return df

def calculate_custom_outflows_outflow(df: pd.DataFrame):
    for index, row in df.iterrows():
        custom_outflows_columns = [col for col in df.columns if col.startswith(CUSTOM)]
        outflow_sum = sum(row[custom_outflow] for custom_outflow in custom_outflows_columns)
        df.at[index, CUSTOM] = outflow_sum
    return df

def calculate_box_culverts_outflow(df: pd.DataFrame, dataset: Dataset):
    for col in df.columns:
        if col.startswith(BOX_CULVERT):
            valve_overflow_id = col.split(".")[1]
            outflow_column_name = f'{OUT_BOX_CULVERT}.{valve_overflow_id}'

            cfg, _ = dataset.get_box_culverts().get(valve_overflow_id)
            cfg: ComponentConfig

            for index, row in df.iterrows():
                water_level = row[WATER_LEVEL]
                opening_value = row[col]
                outflow = calculate_box_culvert_outflow(water_level, cfg.elevation, cfg.height, opening_value)

                df.at[index, outflow_column_name] = outflow
                df.at[index, OUTFLOW] += outflow
    return df


def calculate_valve_overflows_outflow(df: pd.DataFrame, dataset: Dataset):
    for col in df.columns:
        if col.startswith(VALVE_OVERFLOW):
            valve_overflow_id = col.split(".")[1]
            valve_overflow_port = col.split(".")[2]
            outflow_column_name = f'{OUT_VALVE_OVERFLOW}.{valve_overflow_id}.{valve_overflow_port}'

            cfg, _ = dataset.get_valve_overflows().get(valve_overflow_id)
            cfg: ComponentConfig

            for index, row in df.iterrows():
                water_level = row[WATER_LEVEL]
                opening_value = row[col]
                outflow = calculate_valve_overflow_outflow(water_level, cfg.elevation, cfg.height, opening_value)

                df.at[index, outflow_column_name] = outflow
                df.at[index, OUTFLOW] += outflow
    return df


def calculate(
        dataset: Dataset,
        water_level_capacity_map: Dict[float, float],
        round_to: Optional[int] = None,
        nearest_mapping: bool = False,
        capacity_from_dataset_first: bool = False
):
    # # # prepare data # # #
    df = dataset_to_dataframe(dataset)
    validate_dataframe(df)
    
    if not capacity_from_dataset_first or dataset.get_capacity() is None:
        if round_to is not None:
            water_level_capacity_map = {round(key, round_to): value for key, value in water_level_capacity_map.items()}
            df[WATER_LEVEL] = df[WATER_LEVEL].round(round_to)
        
        map_capacity(df, water_level_capacity_map, nearest_mapping)
        
    df[INTERVAL] = df[TIME_SERIES].diff().dt.total_seconds().fillna(0)

    # # # calculate # # #
    df[OUTFLOW] = 0.0
    
    calculate_pumps_outflow(df)
    calculate_box_culverts_outflow(df, dataset)
    calculate_valve_overflows_outflow(df, dataset)
    calculate_custom_outflows_outflow(df)
    
    df[INFLOW] = ((df[OUTFLOW] * df[INTERVAL]) + (
        df[CAPACITY].diff()) * 10 ** 6) / (df[INTERVAL])

    df[INFLOW] = df[INFLOW].apply(lambda x: x if x >= 0 else 0).fillna(0)
    df[OUTFLOW] = df[OUTFLOW].apply(lambda x: x if x >= 0 else 0).fillna(0)

    return df
