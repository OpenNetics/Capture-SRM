# utils/typedefs.py

#- Imports -----------------------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import List, Tuple

from sklearn.mixture import GaussianMixture


#- Constants ---------------------------------------------------------------------------------------

RECORD_ACTION_STOP: int = 0
RECORD_ACTION_START: int = 1
RECORD_ACTION_DISCARD: int = 2
RECORD_ACTION_RESTART: int = 3
RECORD_ACTION_TERMINATE: int = 4

TAB1: int = 1
TAB2: int = 2

LABEL_RANDOM_STATE: str = "Random State"
LABEL_N_COMPONENTS: str = "n Components"
LABEL_THRESHOLD: str = "Threshold"


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
class ModelParameters:
    random_state: int
    n_components: int
    threshold: float


@dataclass(frozen=True)
class GestureInput:
    name: str
    repeats: int
    sensors: Tuple[int, ...]
    parameters: ModelParameters


@dataclass(frozen=True)
class GestureData:
    parameters: ModelParameters
    models: dict[str, List[GaussianMixture]]


@dataclass(frozen=True)
class GestureUpdater:
    file: str
    data: GestureData
    old_data: GestureInput

