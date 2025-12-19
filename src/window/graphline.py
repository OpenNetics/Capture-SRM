
# window/graphline.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel, QLineEdit

from utils.extra import new_color
from utils.ui import EditLabel


#- GraphLine class ---------------------------------------------------------------------------------

# Lightweight container representing one plotted sensor line (readings, color, label).
class GraphLine:

    # Initialise a GraphLine with initial readings, color tuple and an editable title widget.
    def __init__(self, reading: list[float], title: str) -> None:
        self.__color: tuple[int, int, int] = new_color()
        self.__reading: list[float] = reading
        self.__title: EditLabel = EditLabel(title, self.__color)


    #- Class Properties ----------------------------------------------------------------------------

    # Return the legend box thingy for this line.
    @property
    def legend(self) -> QLabel:
        square = QLabel()
        square.setFixedSize(QSize(5, 20))
        square.setStyleSheet(
            f"background-color: rgb({self.__color[0]}, {self.__color[1]}, {self.__color[2]});"
        )
        return square


    # Return the QLineEdit object for the current line.
    @property
    def title(self) -> QLineEdit: return self.__title.obj()


    # Return the text of the title widget for this line.
    @property
    def text(self) -> str: return self.__title.obj().text()


    #- Public Methods ------------------------------------------------------------------------------

    # Return a slice of the stored readings between start_idx and end_idx.
    def reading(self, start_idx: int = 0, end_idx: Optional[int] = None) -> list[float]:
        return self.__reading[start_idx:end_idx]


    # Return the color tuple used to render this graph line.
    def color(self) -> tuple[int, int, int]:
        return self.__color


    # Append a new numeric reading to this graph line.
    def add_reading(self, value: float) -> None:
        self.__reading.append(value)


    # Reset readings to keep only the most recent value (used when clearing older data).
    def reset_reading(self) -> None:
        self.__reading = [self.__reading[-1]]

