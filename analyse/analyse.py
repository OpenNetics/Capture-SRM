
# analyse/analyse.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Tuple
from threading import Thread

import numpy as np
from numpy.typing import NDArray
from sklearn.mixture import GaussianMixture

from utils.typedefs import SensorData, float3d_t
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


def _single_thread_analyse(
    name: str, readings: List[SensorData], parameters: Tuple[int, int, float]
) -> None:
    if not create_gesture(name, parameters[2]):
        # failed to create gesture file
        return

    for reading in readings:
        model: List[GaussianMixture] = _create_model(reading.values, parameters[0], parameters[1])
        write_gmm(name, reading.sensor, model)


#- Public Methods ----------------------------------------------------------------------------------

def analyse(
    name: str, readings: List[SensorData], parameters: Tuple[int, int, float]
) -> None:
    single_thread = Thread(target=_single_thread_analyse, args=(name, readings, parameters,))
    single_thread.start()

