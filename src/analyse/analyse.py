
# analyse/analyse.py

#- Imports -----------------------------------------------------------------------------------------

from threading import Thread

import numpy as np
from numpy.typing import NDArray
from sklearn.mixture import GaussianMixture
from redwrenlib import GestureFile
from redwrenlib.typing import float3d_t

from utils.typing import (
    model_parameters_t, sensor_values_t
)


#- Private Methods ---------------------------------------------------------------------------------

def _create_model(data: float3d_t, random_state: int, n_components: int ) -> list[GaussianMixture]:
    # creates a numpy list of arrays from the data iterable of only non-empty arrays
    train_traces: list[NDArray[np.float64]] = [np.array(t) for t in data if len(t) > 0]

    # create models
    gmm_models: list[GaussianMixture] = []
    for trace in train_traces:
        gmm = GaussianMixture(n_components=n_components, random_state=random_state)
        gmm.fit(trace)
        gmm_models.append(gmm)

    return gmm_models


def _single_thread_create(name: str, readings: sensor_values_t, mp: model_parameters_t) -> None:
    gesture_file: GestureFile = GestureFile(name)

    if not (gesture_file.create()):
        # failed to create gesture file
        return

    for i, r in enumerate(readings):
        model = _create_model(r.values, mp[i].random_state, mp[i].n_components)

        gesture_file.append_reading(r.label, model)
        gesture_file.set_parameters(
            label = r.label,
            n_components = mp[i].n_components,
            random_state = mp[i].random_state,
            threshold = mp[i].threshold
        )

    gesture_file.write()
    print(f"Gesture '{name}' analysis complete.")


def _single_thread_update(name: str, readings: sensor_values_t, mp: model_parameters_t) -> None:
    pass


#- Public Methods ----------------------------------------------------------------------------------

# Analyse data and create a new file with it.
def analyse_create(name: str, readings: sensor_values_t, mp: model_parameters_t) -> None:
    single_thread = Thread(target=_single_thread_create, args=(name, readings, mp,))
    single_thread.start()


# Analyse data and write it to an existing file.
def analyse_update(name: str, readings: sensor_values_t, mp: model_parameters_t) -> None:
    single_thread = Thread(target=_single_thread_update, args=(name, readings, mp,))
    single_thread.start()

