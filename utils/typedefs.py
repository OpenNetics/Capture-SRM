
# utils/typedefs.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Tuple


#- Type Definitions --------------------------------------------------------------------------------

float2d_t = List[List[float]]
float3d_t = List[List[List[float]]]
int2d_t = List[List[int]]


class SensorData:
    sensor: str
    values: float3d_t

    def __init__(self, sensor: str, values: float3d_t) -> None:
        self.sensor = sensor
        self.values = values

    def AddValues(self, counter: List[float], readings: List[float]) -> None:
        read_values: float2d_t = [[x, y] for x, y in zip(counter, readings)]
        self.values.append(read_values)


class GestureInput:
    name: str
    repeats: int
    sensors: List[int]
    parameters: Tuple[int, int, float]

