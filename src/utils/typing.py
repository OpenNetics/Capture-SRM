
# utils/typing.py

#- Imports -----------------------------------------------------------------------------------------

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from sklearn.mixture import GaussianMixture
from redwrenlib.utils import defaults
from redwrenlib.typing import (
    float2d_t, float3d_t
)


#- Constants ---------------------------------------------------------------------------------------

RECORD_ACTION_STOP: int = 0
RECORD_ACTION_START: int = 1
RECORD_ACTION_DISCARD: int = 2
RECORD_ACTION_RESTART: int = 3
RECORD_ACTION_TERMINATE: int = 4

TAB1: int = 1
TAB2: int = 2
TAB3: int = 3

LABEL_RANDOM_STATE: str = "Random State"
LABEL_N_COMPONENTS: str = "n Components"
LABEL_THRESHOLD: str = "Threshold"


#- Data Classes ------------------------------------------------------------------------------------

# Dataclass holding sensor name and appended time/reading pairs for analysis.
@dataclass
class SensorValues:
    label: str
    values: float3d_t = field(default_factory=list)

    def AddValues(self, counter: List[float], readings: List[float]) -> None:
        read_values: float2d_t = [[x, y] for x, y in zip(counter, readings)]
        self.values.append(read_values)


# Default parameters for Gaussian Mixture models.
@dataclass(frozen=True)
class ModelParameters:
    threshold:  float = defaults.MODEL_THRESHOLD
    random_state: int = defaults.MODEL_RANDOM_STATE
    n_components: int = defaults.MODEL_N_COMPONENTS


# Immutable input bundle used when recording a new gesture (name, repeats, sensors, params).
@dataclass(frozen=True)
class GestureInput:
    filename: str
    repeats: int
    parameters: Dict[int, ModelParameters]


# Structure used when updating an existing gesture file (filename, new data and original inputs).
@dataclass(frozen=True)
class GestureUpdater:
    file: GestureInput
    data: dict[str, List[GaussianMixture]]


#- Aliases -----------------------------------------------------------------------------------------

sensor_values_t = List[SensorValues]
model_parameters_t = Tuple[ModelParameters, ...]

