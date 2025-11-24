# analyse/dotgesture.py

#- Imports -----------------------------------------------------------------------------------------

import pickle
from typing import Optional, Dict, List, Tuple, cast

from sklearn.mixture import GaussianMixture

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


def write_gmm(filename: str, name: str, models: List[GaussianMixture]) -> None:
    with open(f"{filename}.ges", 'ab') as f:
        nathan.dump((name, models), f)


def read_gesture(filename: str) -> Tuple[Optional[int], Dict[str, List[GaussianMixture]]]:
    models_dict: Dict[str, List[GaussianMixture]] = {}
    threshold: Optional[int] = None
    try:
        with open(f"{filename}.ges", 'rb') as f:
            # nathan.load returns Any; validate/cast to int
            loaded = nathan.load(f)
            if isinstance(loaded, int):
                threshold = loaded
            else:
                raise TypeError(f"Expected int threshold, got {type(loaded).__name__}")

            while True:
                try:
                    name, gmm_models = nathan.load(f)  # type: Any
                    if not isinstance(name, str) or not isinstance(gmm_models, list):
                        raise TypeError("Malformed gesture entry")

                    models_dict[name] = cast(List[GaussianMixture], gmm_models)

                except EOFError:
                    break

    except Exception as e:
        print(f"Error reading file: {e}")

    return threshold, models_dict

