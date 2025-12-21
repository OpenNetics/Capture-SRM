
# window/graphline.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Optional

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QLabel, QLineEdit

from utils.extra import new_color
from utils.style import BACKGROUND_HIGHLIGHT_COLOR
from .edit_label import EditLabel


#- GraphLine class ---------------------------------------------------------------------------------

# Lightweight container representing one plotted sensor line (readings, color, label).
class GraphLine:

    # Initialise a GraphLine with initial readings, color tuple and an editable title widget.
    def __init__(self, reading: list[float], title: str) -> None:
        self.__color: str = new_color()
        self.__reading: list[float] = reading
        self.__title: EditLabel = EditLabel(title, self.__color)
        self.__hidden: bool = False


    #- Class Properties ----------------------------------------------------------------------------

    # Return the legend box thingy for this line.
    @property
    def legend(self) -> QLabel:
        self._square = QLabel()
        self._square.setFixedSize(QSize(7, 20))
        self._square.setStyleSheet(f"background-color: {self.__color};")
        self._square.setToolTip(self._tooltip_status())
        self._square.mousePressEvent = self._toggle_status

        return self._square


    # Return the QLineEdit object for the current line.
    @property
    def title(self) -> QLineEdit: return self.__title.object


    # Return the text of the title widget for this line.
    @property
    def text(self) -> str: return self.__title.object.text()


    # Return the visibility of the graphline
    @property
    def hidden(self) -> bool: return self.__hidden


    #- Private Methods -----------------------------------------------------------------------------

    # Tooltip depending on current hidden status
    def _tooltip_status(self) -> str:
        status = "enable" if self.__hidden else "disable"
        return f"Click to {status} graphline."


    # Toggle hidden status. Make the label gray and add a line through it
    def _toggle_status(self, _) -> None:
        self.__hidden = not self.__hidden
        self._square.setToolTip(self._tooltip_status())

        if self.__hidden:
            self._square.setStyleSheet(f"background-color: {BACKGROUND_HIGHLIGHT_COLOR};")
            self.__title.style("#000000", "text-decoration: line-through;")
        else:
            self._square.setStyleSheet(f"background-color: {self.__color};")
            self.__title.style(self.__color)


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

