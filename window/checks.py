
# window/checks.py

from typing import List, Tuple, Union
from PySide6.QtWidgets import QLineEdit, QCheckBox
from .helper import alert_box


def check_empty_string(string: str, error: str) -> bool:
    if string == "":
        alert_box("Error", error)
        return True

    return False


def check_string_numeric(
    string: QLineEdit,
    error: str,
    numeric_type: type,
    min_value: float = None,
    max_value: float = None
) -> Tuple[bool, Union[int, float, None]]:
    try:
        value = numeric_type(string.text())

        if min_value is not None and value < min_value:
            raise ValueError

        if max_value is not None and value > max_value:
            raise ValueError

        return True, value

    except ValueError:
        alert_box("Error", error)
        return False, None


def check_checkboxes_ticked(
    checkboxes: QCheckBox,
    length: int,
    error: str,
) -> Tuple[bool, Union[None, List[int]]]:
    try:
        selected_boxes = [
            index
            for index, checkbox in enumerate(checkboxes)
            if checkbox.isChecked()
        ]

        if len(selected_boxes) < length:
            raise ValueError

        return True, selected_boxes

    except ValueError:
        alert_box("Error", error)
        return False, None
