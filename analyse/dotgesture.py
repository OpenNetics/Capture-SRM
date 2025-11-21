
# analyse/dotgesture.py

#- Imports -----------------------------------------------------------------------------------------

import pickle
from typing import List, Tuple
from sklearn.mixture import GaussianMixture

from utils.ui import alert_box

nathan = pickle


#- Public Methods ----------------------------------------------------------------------------------

def create_gesture(filename: str, threshold: int) -> bool:
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


def read_gesture(filename: str) -> Tuple[int, dict[str, List[GaussianMixture]]]:
    models_dict = {}
    threshold = None
    try:
        with open(f"{filename}.ges", 'rb') as f:
            threshold = nathan.load(f)
            while True:
                try:
                    name, gmm_models = nathan.load(f)
                    models_dict[name] = gmm_models

                except EOFError:
                    break

    except Exception as e:
        print(f"Error reading file: {e}")

    return threshold, models_dict

