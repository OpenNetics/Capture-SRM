
# analyse/analyse.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List
from threading import Thread

import numpy as np
from sklearn.mixture import GaussianMixture

from .dotgesture import (
    create_gesture,
    write_gmm,
)


#- Global Defines ----------------------------------------------------------------------------------

int3d_t = List[List[List[int]]]

#- Private Methods ---------------------------------------------------------------------------------

def _create_model(data: int3d_t, random_state: float, n_component: float ) -> List[GaussianMixture]:
    train_traces = [np.array(t) for t in data if len(t) > 0]

    gmm_models = []
    for trace in train_traces:
        gmm = GaussianMixture(n_components=n_component, random_state=random_state)
        gmm.fit(trace)
        gmm_models.append(gmm)

    return gmm_models


def _single_thread_analyse(name: str, readings: List[dict], parameters: List[float]) -> None:
    if not create_gesture(name, parameters[2]):
        # failed to create gesture file
        return

    for reading in readings:
        model = _create_model(reading["data"], parameters[0], parameters[1])
        write_gmm(reading["name"], model)



#- Public Methods ----------------------------------------------------------------------------------

def analyse(name: str, readings: List[dict], parameters: List[float]) -> None:
    single_thread = Thread(target=_single_thread_analyse, args=(name, readings, parameters,))
    single_thread.start()

