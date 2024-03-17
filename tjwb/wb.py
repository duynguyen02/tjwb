import pandas as pd

from .boxdrain import BoxDrainUtilities
from .valveoverflow import ValveOverflowUtilities

class MissingColumnsExeption(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(f"Missing columns: {args}")


class WB:
    
    REQUIRED_COLUMNS = ['timestamp', 'water_level']
    VALUE_PREFIX_COLUMNS = ['pump_', 'rain_', 'boxdrain_', 'valveoverflow_']
    
    def __init__(
        self,
        elevation_to_storage_df: pd.DataFrame,
        boxdrain_elevation: float=None,
        boxdrain_height: float=None,
        valveoverflow_elevation: float=None,
        valveoverflow_height: float=None,
    ):
        self._elevation_to_storage_df = elevation_to_storage_df
        
        self._boxdrain_elevation = boxdrain_elevation
        self._boxdrain_height = boxdrain_height
        self._valveoverflow_elevation = valveoverflow_elevation
        self._valveoverflow_height = valveoverflow_height
        
        
    
    @property
    def elevation_to_storage_df(self):
        return self._elevation_to_storage_df
    
    @elevation_to_storage_df.setter
    def elevation_to_storage_df(self, value):
        self._elevation_to_storage_df = value
        
    @staticmethod
    def required_columns(df: pd.DataFrame, required_columns: list[str]):
        return all(col in df.columns for col in required_columns)
    
    def _calculate_valveoverflow_outflow(
        self,
        pre_df: pd.DataFrame,
        round_to: int=None
    ):
        df = pre_df.copy()
        if (
            self._valveoverflow_elevation is not None and
            self._valveoverflow_height is not None
        ):
            valveoverflow_columns = [col for col in df.columns if any(col.startswith(prefix) for prefix in ['valveoverflow_'])]
            for col in valveoverflow_columns:
                underscore_index = col.index('_')
                overflow_id = col[underscore_index + 1:]
                df[f'valveoverflowOutflow_{overflow_id}'] = df.apply(
                    lambda row: ValveOverflowUtilities.calculate_valveoverflow_outflow(
                        water_level=row['water_level'],
                        valveoverflow_elevation=self._valveoverflow_elevation,
                        valveoverflow_height=self._valveoverflow_height,
                        overflow_opening_level=row[col],
                        round_to=round_to
                    ),
                    axis=1
                )
                df['Q_out_total'] += df[f'valveoverflowOutflow_{overflow_id}']
        return df
        
    
    def _caculate_boxdrain_outflow(
        self,
        pre_df: pd.DataFrame,
        round_to: int=None
    ):
        df = pre_df.copy()
        if (
            self._boxdrain_elevation is not None and
            self._boxdrain_height is not None
        ):
            boxdrain_columns = [col for col in df.columns if any(col.startswith(prefix) for prefix in ['boxdrain_'])]
            
            for col in boxdrain_columns:
                underscore_index = col.index('_')
                drain_id = col[underscore_index + 1:]
                
                df[f'boxdrainOutflow_{drain_id}'] = df.apply(
                    lambda row: BoxDrainUtilities.calculate_boxdrain_outflow(
                        water_level=row['water_level'],
                        boxdrain_elevation=self._boxdrain_elevation,
                        boxdrain_height=self._boxdrain_height,
                        drain_opening_level=row[col],
                        round_to=round_to
                    ),
                    axis=1
                )
                df['Q_out_total'] += df[f'boxdrainOutflow_{drain_id}']
        return df
    
    def _calculate_inflow(
        self,
        pre_df: pd.DataFrame,
        round_to: int=None
    ):
        df = pre_df.copy()
        
        q_in = round(((df['Q_out_total'] * df['delta_T']) + (df['storage'].diff())*10**6) / (df['delta_T']), 3)
        
        df['Q_in'] = q_in if round_to is None else round(q_in, round_to)
        
        condition = (df['Q_in'].isna()) | (df['Q_in'] < 0)
        df.loc[condition, 'Q_in'] = 0
        
        return df
        
    
    def calculate(
        self,
        pre_df: pd.DataFrame,
        round_to: int=None,
    ):
        df = pre_df.copy()
        
        if not self.required_columns(df, self.REQUIRED_COLUMNS):
            raise MissingColumnsExeption(self.REQUIRED_COLUMNS)
        
        
        required_prefixes_columns = [
            col for col in df.columns
            if any(col.startswith(prefix) for prefix in self.VALUE_PREFIX_COLUMNS)
        ]
        if not required_prefixes_columns:
            raise MissingColumnsExeption(f"Requires at least one of the columns to have a prefix: {self.VALUE_PREFIX_COLUMNS}")
        
        processing_columns = self.REQUIRED_COLUMNS + required_prefixes_columns
        
        # removing all invalid columns
        df = df[processing_columns]
        df = df.dropna()
        
        # processing timestamp
        df['timestamp'] = df['timestamp'].astype(str)
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values(by='datetime')
        
        # caculating delta_T
        df['delta_T'] = df['datetime'].diff().dt.total_seconds().fillna(0)
        df = df.drop(columns=['datetime'])
        
        # may raise an Exception if elevation from df and _elevation_to_storage_df is invalid
        df['storage'] = df['water_level'].map(self._elevation_to_storage_df.set_index('elevation')['storage'])
        df = df.dropna(subset=['storage'])

        df['Q_out_total'] = 0
        
        # add pumping station flow to Q_out_total
        pump_columns = [col for col in df.columns if col.startswith('pump_')]
        for col in pump_columns:
            df['Q_out_total'] += df[col]
            
        # calculate and add the flow of the boxdrain to Q_out_total
        df = self._caculate_boxdrain_outflow(df, round_to)
            
        # calculate and add the flow of the valveoverflow to Q_out_total
        df = self._calculate_valveoverflow_outflow(df, round_to)
        
        df = self._calculate_inflow(df, round_to)

        return df
        
