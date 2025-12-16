
# window/checks.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Optional, TypeVar, Type

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

        if min_value is not None and value < min_value: raise ValueError
        if max_value is not None and value > max_value: raise ValueError

        return value

    except ValueError:
        alert_box("Error", error)

    return None


# Ensure that the provided list of source names are unique; pop up an alert on failure.
def check_sources_name(sources: tuple[str, ...]) -> bool:
    result: bool = len(sources) == len(set(sources))
    if not result:
        alert_box("Error", "Make sure all sources have unique names")

    return result

