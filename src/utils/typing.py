
# utils/typing.py

#- Imports -----------------------------------------------------------------------------------------

from enum import Enum
from dataclasses import dataclass, field

from redwrenlib.utils import defaults
from redwrenlib.typing import (
    float2d_t, float3d_t
)


#- Constants ---------------------------------------------------------------------------------------

class RecordAction(Enum):
    STOP = 0
    START = 1
    DISCARD = 2
    RESTART = 3
    TERMINATE = 4

class Tab(Enum):
    NONE = 0
    CREATE = 1
    UPDATE = 2
    TEST = 3

LABEL_RANDOM_STATE: str = "Random State"
LABEL_N_COMPONENTS: str = "n Components"
LABEL_THRESHOLD: str = "Threshold"


#- Data Classes ------------------------------------------------------------------------------------

# Dataclass holding sensor name and appended time/reading pairs for analysis.
@dataclass
class SensorValues:
    label: str
    values: float3d_t = field(default_factory=list)

    def AddValues(self, counter: list[float], readings: list[float]) -> None:
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
    source_ids: tuple[int, ...]
    parameters: tuple[ModelParameters, ...]
    file_sources: tuple[str, ...] = ()


#- Aliases -----------------------------------------------------------------------------------------

sensor_values_t = list[SensorValues]
model_parameters_t = tuple[ModelParameters, ...]

