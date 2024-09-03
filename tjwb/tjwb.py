import dataclasses
import math
import uuid
from typing import Optional, List, Dict

import pandas as pd


@dataclasses.dataclass
class RequiredColumnsName:
    datetime: str = 'Datetime'
    water_level: str = 'Water Level'


# # # COMPONENTS # # #
@dataclasses.dataclass
class ComponentConfig:
    column_name_prefix: str


@dataclasses.dataclass
class EHComponentConfig(ComponentConfig):
    elevation: float
    height: float


@dataclasses.dataclass
class PumpConfig(ComponentConfig):
    pass


@dataclasses.dataclass
class ValveOverflowConfig(EHComponentConfig):
    pass


@dataclasses.dataclass
class BoxCulvertConfig(EHComponentConfig):
    pass


# # # COMPONENTS # # #


@dataclasses.dataclass
class WaterLevelCapacityMappingColumnsName:
    water_level: str = 'Water Level'
    capacity: str = 'Capacity'


def _validate_components_config(components_config: List[ComponentConfig]):
    all_prefixes = []
    for component_config in components_config:
        all_prefixes.append(component_config.column_name_prefix)
        if '.' in component_config.column_name_prefix:
            raise ValueError(
                f"Data column name prefix must not contain '.' character: {component_config.column_name_prefix} "
            )
    if len(all_prefixes) != len(set(all_prefixes)):
        raise ValueError("The list contains duplicate prefixes.")


def _validate_water_level_capacity_mapping_df(
        _df: pd.DataFrame,
        water_level_capacity_mapping_columns_name: WaterLevelCapacityMappingColumnsName,
):
    wlcm_cn = water_level_capacity_mapping_columns_name
    wlcm_df = _df.copy()

    required_columns = [wlcm_cn.capacity, wlcm_cn.water_level]

    missing_columns = [col for col in required_columns if col not in wlcm_df.columns]
    if missing_columns:
        raise ValueError(
            f"The Water Level Capacity Mapping DataFrame"
            f"needs to have the following columns: {', '.join(missing_columns)}"
        )

    for col in required_columns:
        if not pd.api.types.is_numeric_dtype(wlcm_df[col]):
            raise TypeError(f"Column '{col}' must be of type float.")

    if wlcm_df[required_columns].isnull().any().any():
        raise ValueError("There are missing values in one or more of the required columns.")

    return wlcm_df[required_columns]


def _count_decimal_places(number: float):
    number_str = str(number)
    if '.' in number_str:
        decimal_part = number_str.split('.')[1]
        return len(decimal_part)
    else:
        return 0


def _calculate_box_culvert_outflow(
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


def _calculate_valve_overflow_outflow(
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


def _to_zero_if_nan_or_negative(series: pd.Series):
    series = series.fillna(0)
    series = series.apply(lambda x: 0 if x < 0 else x)
    return series


@dataclasses.dataclass
class TJWBResult:
    datetime: pd.Series
    inflow_speed: pd.Series
    outflow_speed: pd.Series
    water_level: pd.Series
    capacity: pd.Series
    components_outflow_speed: Dict[str, pd.Series]

    def to_dataframe(self):
        data = {
            'datetime': self.datetime,
            'inflow_speed': self.inflow_speed,
            'outflow_speed': self.outflow_speed,
            'water_level': self.water_level,
            'capacity': self.capacity,
        }
        data.update(self.components_outflow_speed)
        return pd.DataFrame(data)


def calculate(
        _df: pd.DataFrame,
        _water_level_capacity_mapping_df: pd.DataFrame,
        water_level_capacity_mapping_columns_name: WaterLevelCapacityMappingColumnsName,
        required_columns_name: RequiredColumnsName,
        pump_configs: Optional[List[PumpConfig]] = None,
        valve_overflow_configs: Optional[List[ValveOverflowConfig]] = None,
        box_culvert_configs: Optional[List[BoxCulvertConfig]] = None,
        nearest_mapping: bool = False,
):
    # normalize _water_level_capacity_mapping_df
    wlcm_df = _validate_water_level_capacity_mapping_df(
        _water_level_capacity_mapping_df,
        water_level_capacity_mapping_columns_name,
    )

    # calculate max decimal places for easy reference
    capacity_max_decimal_places = wlcm_df[
        water_level_capacity_mapping_columns_name.capacity].apply(_count_decimal_places).max()
    water_level_max_decimal_places = wlcm_df[
        water_level_capacity_mapping_columns_name.water_level].apply(_count_decimal_places).max()

    """
    WARNING: Edit this block of code to remove or add components that need to be calculated.
    """
    if pump_configs is None:
        pump_configs = []
    if valve_overflow_configs is None:
        valve_overflow_configs = []
    if box_culvert_configs is None:
        box_culvert_configs = []
    components_config = pump_configs + valve_overflow_configs + box_culvert_configs

    # at least 1 component
    if len(components_config) == 0:
        raise ValueError(
            "There are no components configured. "
        )

    _validate_components_config(components_config)

    df = _df.copy()

    if df.isnull().any().any():
        raise ValueError("The DataFrame contains null values.")

    # convert to datetime
    try:
        df[required_columns_name.datetime] = pd.to_datetime(
            df[required_columns_name.datetime],
            utc=True
        )
    except Exception as _:
        raise ValueError(
            "Cannot convert date column to datetime. "
        )

    # calculate delta T
    delta_t_column_name = f'{uuid.uuid4().hex}_delta_t'
    df[delta_t_column_name] = df[required_columns_name.datetime].diff().dt.total_seconds().fillna(0)

    df[required_columns_name.water_level] = round(
        df[required_columns_name.water_level],
        water_level_max_decimal_places
    )

    df[water_level_capacity_mapping_columns_name.capacity] = df[
        required_columns_name.water_level
    ].map(
        wlcm_df.set_index(
            water_level_capacity_mapping_columns_name.water_level
        )[water_level_capacity_mapping_columns_name.capacity]
    )

    if nearest_mapping:
        def fill_capacity(row, df_mapping):
            if pd.notna(row[water_level_capacity_mapping_columns_name.capacity]):
                return row[water_level_capacity_mapping_columns_name.capacity]

            water_level = row[required_columns_name.water_level]

            min_water_level = df_mapping[water_level_capacity_mapping_columns_name.water_level].min()
            max_water_level = df_mapping[water_level_capacity_mapping_columns_name.water_level].max()

            if water_level > max_water_level:
                return df_mapping.loc[
                    df_mapping[
                        water_level_capacity_mapping_columns_name.water_level
                    ] == max_water_level,
                    water_level_capacity_mapping_columns_name.capacity
                ].values[0]

            if water_level < min_water_level:
                return df_mapping.loc[
                    df_mapping[
                        water_level_capacity_mapping_columns_name.water_level
                    ] == min_water_level,
                    water_level_capacity_mapping_columns_name.capacity
                ].values[
                    0]

            lower = df_mapping[df_mapping[water_level_capacity_mapping_columns_name.water_level] < water_level][
                water_level_capacity_mapping_columns_name.water_level].max()
            upper = df_mapping[df_mapping[water_level_capacity_mapping_columns_name.water_level] > water_level][
                water_level_capacity_mapping_columns_name.water_level].min()

            if (water_level - lower) <= (upper - water_level):
                return df_mapping.loc[
                    df_mapping[
                        water_level_capacity_mapping_columns_name.water_level
                    ] == lower,
                    water_level_capacity_mapping_columns_name.capacity
                ].values[0]
            else:
                return df_mapping.loc[
                    df_mapping[
                        water_level_capacity_mapping_columns_name.water_level
                    ] == upper,
                    water_level_capacity_mapping_columns_name.capacity
                ].values[0]

        df[water_level_capacity_mapping_columns_name.capacity] = df.apply(fill_capacity, axis=1, df_mapping=wlcm_df)

    if df.isnull().any().any():
        raise ValueError("The data DataFrame contains invalid water level does not match mapping Dataframe.")

    num_of_elements = df.shape[0]

    # store component results
    components_outflow_speed = {}
    inflow_speed_series = pd.Series([0] * num_of_elements)
    outflow_speed_series = pd.Series([0] * num_of_elements)

    # calculate each components
    for component_config in components_config:
        for col in df.columns:
            if col.startswith(f'{component_config.column_name_prefix}.'):

                if not pd.api.types.is_numeric_dtype(df[col]):
                    raise TypeError(f"Column '{col}' must be of type numeric.")

                """
                WARNING: Edit this block of code to remove or add components that need to be calculated.
                """
                result = None
                if isinstance(component_config, PumpConfig):
                    result = df[col]

                if isinstance(component_config, BoxCulvertConfig):
                    result = pd.Series([
                        _calculate_box_culvert_outflow(wl, component_config.elevation, component_config.height, ov)
                        for wl, ov in zip(df[required_columns_name.water_level], df[col])
                    ])

                if isinstance(component_config, ValveOverflowConfig):
                    result = pd.Series([
                        _calculate_valve_overflow_outflow(wl, component_config.elevation, component_config.height, ov)
                        for wl, ov in zip(df[required_columns_name.water_level], df[col])
                    ])

                if result is None:
                    raise TypeError(f"Invalid component config: {type(component_config)}")

                result = _to_zero_if_nan_or_negative(result)

                outflow_speed_series += result

                components_outflow_speed[
                    f"{component_config.__class__.__name__}.{col.split('.', 1)[1]}"
                ] = result

    inflow_speed_series += ((outflow_speed_series * df[delta_t_column_name]) + (
        df[water_level_capacity_mapping_columns_name.capacity].diff()) * 10 ** 6) / (df[delta_t_column_name])

    inflow_speed_series = _to_zero_if_nan_or_negative(inflow_speed_series)
    outflow_speed_series = _to_zero_if_nan_or_negative(outflow_speed_series)

    return TJWBResult(
        datetime=df[required_columns_name.datetime],
        inflow_speed=inflow_speed_series,
        outflow_speed=outflow_speed_series,
        water_level=df[required_columns_name.water_level],
        capacity=df[water_level_capacity_mapping_columns_name.capacity],
        components_outflow_speed=components_outflow_speed
    )
