# utils/typedefs.py

#- Imports -----------------------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import List, Tuple, Optional

from sklearn.mixture import GaussianMixture


#- Type Definitions --------------------------------------------------------------------------------

float2d_t = List[List[float]]
float3d_t = List[List[List[float]]]
int2d_t = List[List[int]]


@dataclass
class SensorData:
    sensor: str
    values: float3d_t = field(default_factory=list)

    def AddValues(self, counter: List[float], readings: List[float]) -> None:
        read_values: float2d_t = [[x, y] for x, y in zip(counter, readings)]
        self.values.append(read_values)


@dataclass(frozen=True)
class GestureInput:
    name: str
    repeats: int
    sensors: Tuple[int, ...]
    parameters: Tuple[int, int, float]


@dataclass(frozen=True)
class GestureData:
    threshold: Optional[float]
    models: dict[str, Tuple[GaussianMixture]]


@dataclass(frozen=True)
class GestureUpdater:
    file: str
    data: GestureData
    old_data: GestureInput

