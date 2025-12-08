
# window/checks.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Optional, TypeVar, Type, Tuple

from PySide6.QtWidgets import QCheckBox

from utils.ui import alert_box


#- Public Methods ----------------------------------------------------------------------------------

# Show an alert if a required string is empty; returns True when error occurred.
def check_empty_string(string: str, error: str) -> bool:
    if string == "":
        alert_box("Error", error)
        return True

    return False


# Generic numeric validator for QLineEdit that enforces optional min/max bounds.
Numeric = TypeVar('Numeric', int, float)
def check_string_numeric(
    text: str,
    error: str,
    numeric_type: Type[Numeric],
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> Optional[Numeric]:
    try:
        value = numeric_type(text)

        if min_value is not None and value < min_value:
            raise ValueError

        if max_value is not None and value > max_value:
            raise ValueError

        return value

    except ValueError:
        alert_box("Error", error)
        return None


# Ensure that the provided list of source names are unique; pop up an alert on failure.
def check_sources_name(sources: List[str]) -> bool:
    result: bool = len(sources) == len(set(sources))
    if not result:
        alert_box("Error", "Make sure all sources have unique names")

    return result


# Ensure a minimum number of checkboxes are ticked and return their indexes or None on error.
def check_checkboxes_ticked(
    checkboxes: List[QCheckBox],
    length: int,
    error: str,
) -> Optional[Tuple[int, ...]]:
    try:
        selected_boxes = tuple(
            index for index, checkbox in enumerate(checkboxes) if checkbox.isChecked()
        )

        if len(selected_boxes) < length:
            raise ValueError

        return selected_boxes

    except ValueError:
        alert_box("Error", error)
        return None

