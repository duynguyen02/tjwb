import math

class ValveOverflowUtilities:
    def calculate_valveoverflow_outflow(
        water_level: float,
        valveoverflow_elevation: float,
        valveoverflow_height: float,
        overflow_opening_level: float,
        round_to: int=None
    ):
        result = 0
        
        if water_level - valveoverflow_elevation < 0:
            return result
        elif (water_level - valveoverflow_elevation) >= 1.5 * overflow_opening_level:
            result = 0.63 * 0.94 * valveoverflow_height * overflow_opening_level * math.sqrt(2 * 9.81 * ((water_level - valveoverflow_elevation) - 0.63 * overflow_opening_level))
        else:
            result = 0.36 * valveoverflow_height * math.sqrt(2 * 9.81 * (water_level - valveoverflow_elevation) ** 3)
        
        return (
                round(
                    result,
                    round_to
                )
                if round_to is not None
                else result
            )