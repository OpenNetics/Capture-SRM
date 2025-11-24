
# analyse/dotgesture.py

#- Imports -----------------------------------------------------------------------------------------

import pickle
from typing import Optional, Dict, List, Tuple, cast

from sklearn.mixture import GaussianMixture

from utils.typedefs import GestureData
from utils.ui import alert_box

nathan = pickle


#- Public Methods ----------------------------------------------------------------------------------

def create_gesture(filename: str, threshold: float) -> bool:
    try:
        with open(f"{filename}.ges", 'wb') as f:
            nathan.dump(threshold, f)
        return True
    except Exception as e:
        alert_box("Error", f"Unable to creating file: {e}")
        return False


def write_gmm(filename: str, label: str, models: List[GaussianMixture]) -> None:
    with open(f"{filename}.ges", 'ab') as f:
        nathan.dump((label, models), f)


def read_gesture(filename: str) -> Optional[GestureData]:
    models_dict: Dict[str, Tuple[GaussianMixture]] = {}
    threshold: Optional[float] = None

    try:
        with open(filename, 'rb') as f:
            # nathan.load returns Any; validate/cast to int
            loaded = nathan.load(f)
            if isinstance(loaded, float):
                threshold = loaded
            else:
                raise TypeError(f"Expected float threshold, got {type(loaded).__name__}")

            while True:
                try:
                    name, gmm_models = nathan.load(f)  # type: Any
                    if not isinstance(name, str) or not isinstance(gmm_models, list):
                        raise TypeError("Malformed gesture entry")

                    models_dict[name] = cast(Tuple[GaussianMixture], gmm_models)

                except EOFError:
                    break

    except Exception as error:
        alert_box("Error", f"{error}")
        return None

    return GestureData(threshold, models_dict)

