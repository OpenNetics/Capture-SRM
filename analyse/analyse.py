
# analyse/analyse.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Tuple
from threading import Thread

import numpy as np
from numpy.typing import NDArray
from sklearn.mixture import GaussianMixture

from utils.typing import SensorData, float3d_t, ModelParameters
from .dotgesture import create_gesture, write_gmm


#- Private Methods ---------------------------------------------------------------------------------

def _create_model(data: float3d_t, random_state: int, n_component: int ) -> List[GaussianMixture]:
    train_traces: List[NDArray[np.float64]] = [np.array(t) for t in data if len(t) > 0]

    gmm_models: List[GaussianMixture] = []
    for trace in train_traces:
        gmm = GaussianMixture(n_components=n_component, random_state=random_state)
        gmm.fit(trace)
        gmm_models.append(gmm)

    return gmm_models


def _single_thread_analyse(name: str, readings: List[SensorData], mp: ModelParameters) -> None:
    if not create_gesture(name, mp):
        # failed to create gesture file
        return

    for r in readings:
        model: List[GaussianMixture] = _create_model(r.values, mp.random_state, mp.n_component)
        write_gmm(name, r.sensor, model)

    print(f"Gesture '{name}' analysis complete.")


#- Public Methods ----------------------------------------------------------------------------------

def analyse(name: str, readings: List[SensorData], mp: ModelParameters) -> None:
    single_thread = Thread(target=_single_thread_analyse, args=(name, readings, mp,))
    single_thread.start()

