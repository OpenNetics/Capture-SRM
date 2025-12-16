
# window/graphline.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Optional

from utils.ui import EditLabel


#- GraphLine class ---------------------------------------------------------------------------------

# Lightweight container representing one plotted sensor line (readings, color, label).
class GraphLine:

    # Initialise a GraphLine with initial readings, color tuple and an editable title widget.
    def __init__(
        self, reading: list[float], color: tuple[int, int, int], title: EditLabel
    ) -> None:
        self.__reading: list[float] = reading
        self.__color: tuple[int, int, int] = color
        self.__title: EditLabel = title


    # Return a slice of the stored readings between start_idx and end_idx.
    def reading(self, start_idx: int = 0, end_idx: Optional[int] = None) -> list[float]:
        return self.__reading[start_idx:end_idx]


    # Return the color tuple used to render this graph line.
    def color(self) -> tuple[int, int, int]:
        return self.__color


    # Return the editable title widget for this line.
    def text(self) -> str:
        return self.__title.obj().text()


    # Append a new numeric reading to this graph line.
    def add_reading(self, value: float) -> None:
        self.__reading.append(value)


    # Reset readings to keep only the most recent value (used when clearing older data).
    def reset_reading(self) -> None:
        self.__reading = [self.__reading[-1]]

