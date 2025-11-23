
# window/checks.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Optional, TypeVar, Type

from PySide6.QtWidgets import QLineEdit, QCheckBox

from utils.ui import alert_box


#- Public Methods ----------------------------------------------------------------------------------

def check_empty_string(string: str, error: str) -> bool:
    if string == "":
        alert_box("Error", error)
        return True

    return False


Numeric = TypeVar('Numeric', int, float)
def check_string_numeric(
    string: QLineEdit,
    error: str,
    numeric_type: Type[Numeric],
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> Optional[Numeric]:
    try:
        value = numeric_type(string.text())

        if min_value is not None and value < min_value:
            raise ValueError

        if max_value is not None and value > max_value:
            raise ValueError

        return value

    except ValueError:
        alert_box("Error", error)
        return None


def check_checkboxes_ticked(
    checkboxes: List[QCheckBox],
    length: int,
    error: str,
) -> Optional[List[int]]:
    try:
        selected_boxes = [
            index for index, checkbox in enumerate(checkboxes) if checkbox.isChecked()
        ]

        if len(selected_boxes) < length:
            raise ValueError

        return selected_boxes

    except ValueError:
        alert_box("Error", error)
        return None
