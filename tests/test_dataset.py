import pytest
from datetime import datetime

from tjwb.dataset import Dataset, ComponentConfig


def test_time_series():
    dataset = Dataset()
    time_series = [datetime(2023, 1, 1), datetime(2023, 1, 2)]
    dataset.time_series(time_series)
    assert dataset.get_time_series() == time_series

def test_water_level():
    dataset = Dataset()
    water_level = [1.5, 2.3, 3.0]
    dataset.water_level(water_level)
    assert dataset.get_water_level() == water_level

def test_add_pump():
    dataset = Dataset()
    pump_id = "pump1"
    values = [0.1, 0.2, 0.3]
    dataset.pump(pump_id, values)
    assert dataset.get_pumps()[pump_id] == values

def test_add_pump_with_dot():
    dataset = Dataset()
    with pytest.raises(ValueError, match="Pump ID must not contain dot."):
        dataset.pump("pump.1", [0.1, 0.2, 0.3])

def test_add_box_culvert():
    dataset = Dataset()
    box_culvert_id = "culvert1"
    component_config = ComponentConfig(elevation=1.0, height=2.0)
    values = [0.5, 0.7]
    dataset.box_culvert(box_culvert_id, component_config, values)
    assert dataset.get_box_culverts()[box_culvert_id] == (component_config, values)

def test_add_box_culvert_with_dot():
    dataset = Dataset()
    component_config = ComponentConfig(elevation=1.0, height=2.0)
    with pytest.raises(ValueError, match="Box Culver ID must not contain dot."):
        dataset.box_culvert("culvert.1", component_config, [0.5, 0.7])

def test_add_valve_overflow():
    dataset = Dataset()
    valve_overflow_id = "overflow1"
    component_config = ComponentConfig(elevation=1.0, height=2.0)
    values = [[0.3, 0.4], [0.6, 0.8]]
    dataset.valve_overflow(valve_overflow_id, component_config, values)
    assert dataset.get_valve_overflows()[valve_overflow_id] == (component_config, values)

def test_add_valve_overflow_with_dot():
    dataset = Dataset()
    component_config = ComponentConfig(elevation=1.0, height=2.0)
    with pytest.raises(ValueError, match="Valve Overflow ID must not contain dot."):
        dataset.valve_overflow("overflow.1", component_config, [[0.3, 0.4], [0.6, 0.8]])
