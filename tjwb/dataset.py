from dataclasses import dataclass


@dataclass
class ComponentConfig:
    elevation: float
    height: float


from typing import List, Dict, Optional, Tuple
from datetime import datetime

class Dataset:
    def __init__(self):
        self._time_series: List[datetime] = []
        self._water_level: List[float] = []
        self._capacity: Optional[List[float]] = None
        self._pumps: Dict[str, List[float]] = {}
        self._box_culverts: Dict[str, Tuple[ComponentConfig, List[float]]] = {}
        self._valve_overflows: Dict[str, Tuple[ComponentConfig, List[List[float]]]] = {}
        self._custom_outflows: Dict[str, List[float]] = {}

    def time_series(self, time_series: List[datetime]) -> 'Dataset':
        self._time_series = time_series
        return self

    def water_level(self, water_level: List[float]) -> 'Dataset':
        self._water_level = water_level
        return self
    
    def capacity(self, capacity: List[float]):
        self._capacity = capacity
        return self

    def pump(self, pump_id: str, values: List[float]) -> 'Dataset':
        if '.' in pump_id:
            raise ValueError('Pump ID must not contain dot.')
        self._pumps[pump_id] = values
        return self

    def box_culvert(
            self, box_culvert_id: str,
            component_config: ComponentConfig,
            values: List[float]
    ) -> 'Dataset':
        if '.' in box_culvert_id:
            raise ValueError('Box Culver ID must not contain dot.')
        self._box_culverts[box_culvert_id] = (component_config, values)
        return self

    def valve_overflow(
            self, valve_overflow_id: str,
            component_config: ComponentConfig,
            values: List[List[float]]
    ) -> 'Dataset':
        if '.' in valve_overflow_id:
            raise ValueError('Valve Overflow ID must not contain dot.')
        self._valve_overflows[valve_overflow_id] = (component_config, values)
        return self
    
    def custom_outflows(self, _id: str, values: List[float]) -> 'Dataset':
        if '.' in _id:
            raise ValueError('ID must not contain dot.')
        self._custom_outflows[_id] = values
        return self

    def get_time_series(self) -> List[datetime]:
        return self._time_series

    def get_water_level(self) -> List[float]:
        return self._water_level

    def get_pumps(self) -> Dict[str, List[float]]:
        return self._pumps

    def get_box_culverts(self) -> Dict[str, Tuple[ComponentConfig, List[float]]]:
        return self._box_culverts

    def get_valve_overflows(self) -> Dict[str, Tuple[ComponentConfig, List[List[float]]]]:
        return self._valve_overflows

    def get_capacity(self) -> Optional[List[float]]:
        return self._capacity
    
    def get_custom_outflows(self) -> Dict[str, List[float]]:
        return self._custom_outflows