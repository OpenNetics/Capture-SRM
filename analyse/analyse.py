
# analyse/analyse.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List
from threading import Thread

import numpy as np
from numpy.typing import NDArray
from sklearn.mixture import GaussianMixture
from redwrenlib import GestureFile
from redwrenlib.typing import (
    ModelParameters,
    float3d_t, data_dict_t
)

from utils.typing import SensorData


#- Private Methods ---------------------------------------------------------------------------------

def _create_model(data: float3d_t, random_state: int, n_components: int ) -> List[GaussianMixture]:
    train_traces: List[NDArray[np.float64]] = [np.array(t) for t in data if len(t) > 0]

    gmm_models: List[GaussianMixture] = []
    for trace in train_traces:
        gmm = GaussianMixture(n_components=n_components, random_state=random_state)
        gmm.fit(trace)
        gmm_models.append(gmm)

    return gmm_models


def _single_thread_analyse(name: str, readings: List[SensorData], mp: ModelParameters) -> None:
    if not (gesture_file := GestureFile(name)):
        # failed to create gesture file
        return

    gesture_file.set_parameters(mp)

    for r in readings:
        model: List[GaussianMixture] = _create_model(r.values, mp.random_state, mp.n_components)
        gesture_file.append_reading(r.sensor, model)

    print(f"Gesture '{name}' analysis complete.")


#- Public Methods ----------------------------------------------------------------------------------

def analyse_create(name: str, readings: List[SensorData], mp: ModelParameters, ugh: None) -> None:
    single_thread = Thread(target=_single_thread_analyse, args=(name, readings, mp,))
    single_thread.start()

def analyse_update(name: str, readings: List[SensorData], mp: ModelParameters, old_data: data_dict_t) -> None:
    print("update one called")
    pass

