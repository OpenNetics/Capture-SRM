# analyse/dotgesture.py

#- Imports -----------------------------------------------------------------------------------------

import pickle
from typing import Any, Dict, List, Optional

from sklearn.mixture import GaussianMixture

from utils.typedefs import GestureData, ModelParameters
from utils.ui import alert_box

nathan = pickle


#- Public Methods ----------------------------------------------------------------------------------

def create_gesture(filename: str, model_params: ModelParameters) -> bool:
    """
    Persist the model parameters (ModelParameters) as the first object in the
    gesture file. Returns True on success, False and shows an alert on error.
    """
    try:
        with open(filename, "wb") as f:
            nathan.dump(model_params, f)
        return True
    except Exception as e:
        alert_box("Error", f"Unable to create file: {e}")
        return False


def write_gmm(filename: str, label: str, models: List[GaussianMixture]) -> None:
    with open(filename, "ab") as f:
        nathan.dump((label, models), f)


def read_gesture(filename: str) -> Optional[GestureData]:
    """
    Read a gesture file.

    Expects the first pickled object to be a ModelParameters instance and the
    following objects to be (label, [GaussianMixture, ...]) entries.
    Returns GestureData on success, or None on error (and shows an alert).
    """
    models_dict: Dict[str, List[GaussianMixture]] = {}
    models_params: Optional[ModelParameters] = None

    try:
        with open(filename, "rb") as f:
            loaded: Any = nathan.load(f)
            if isinstance(loaded, ModelParameters):
                models_params = loaded
            else:
                raise TypeError(f"Expected ModelParameters first, got {type(loaded).__name__}")

            while True:
                try:
                    name, gmm_models = nathan.load(f)  # type: Any
                    if not isinstance(name, str) or not isinstance(gmm_models, list):
                        raise TypeError("Malformed gesture entry: expected (str, list)")

                    # store as a tuple to match GestureData typing
                    models_dict[name] = gmm_models

                except EOFError:
                    break

    except Exception as error:
        alert_box("Error", f"{error}")
        return None

    return GestureData(parameters=models_params, models=models_dict)

