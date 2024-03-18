import math

class BoxDrainUtilities:
    def calculate_boxdrain_outflow(
        water_level: float,
        boxdrain_elevation: float,
        boxdrain_height: float,
        drain_opening_level: float,
        round_to: int=None
    ):
        result = 0
        
        if water_level - boxdrain_elevation < 0:
            return result
        elif (water_level - boxdrain_elevation) >= 1.5 * drain_opening_level:
            result = 0.63 * 0.94 * boxdrain_height * drain_opening_level * math.sqrt(2 * 9.81 * ((water_level - boxdrain_elevation) - 0.63 * drain_opening_level))
        else:
            result = 0.36 * boxdrain_height * math.sqrt(2 * 9.81 * (water_level - boxdrain_elevation) ** 3)
            
        return (
                round(
                    result,
                    round_to
                )
                if round_to is not None
                else result
            )