
# window/graphline.py

from typing import List, Tuple, Optional
from utils.ui import EditLabel

class GraphLine:
    def __init__(
        self, reading: List[float], color: Tuple[int, int, int], title: EditLabel
    ) -> None:
        self.__reading: List[float] = reading
        self.__color: Tuple[int, int, int] = color
        self.__title: EditLabel = title


    def Reading(self, start_idx: int = 0, end_idx: Optional[int] = None) -> List[float]:
        return self.__reading[start_idx:end_idx]


    def Color(self) -> Tuple[int, int, int]:
        return self.__color


    def Title(self) -> EditLabel:
        return self.__title


    def AddReading(self, value: float) -> None:
        self.__reading.append(value)


    def ResetReading(self) -> None:
        self.__reading = [self.__reading[-1]]

