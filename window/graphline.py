
# window/graphline.py

from typing import List, Tuple, Optional
from utils.ui import EditLabel

# Lightweight container representing one plotted sensor line (readings, color, label).
class GraphLine:

    # Initialise a GraphLine with initial readings, color tuple and an editable title widget.
    def __init__(
        self, reading: List[float], color: Tuple[int, int, int], title: EditLabel
    ) -> None:
        self.__reading: List[float] = reading
        self.__color: Tuple[int, int, int] = color
        self.__title: EditLabel = title


    # Return a slice of the stored readings between start_idx and end_idx.
    def Reading(self, start_idx: int = 0, end_idx: Optional[int] = None) -> List[float]:
        return self.__reading[start_idx:end_idx]


    # Return the color tuple used to render this graph line.
    def Color(self) -> Tuple[int, int, int]:
        return self.__color


    # Return the editable title widget for this line.
    def Title(self) -> EditLabel:
        return self.__title


    # Append a new numeric reading to this graph line.
    def AddReading(self, value: float) -> None:
        self.__reading.append(value)


    # Reset readings to keep only the most recent value (used when clearing older data).
    def ResetReading(self) -> None:
        self.__reading = [self.__reading[-1]]

