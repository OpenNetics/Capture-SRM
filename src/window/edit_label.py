
# window/edit_label.py

#- Imports -----------------------------------------------------------------------------------------

from PySide6.QtWidgets import QLineEdit

from utils.style import TEXT_BOX_STYLE


#- EditLabel class ---------------------------------------------------------------------------------

# Simple editable label that auto-resizes to fit its text.
class EditLabel():

    # Initialise EditLabel with given text and set up auto-resize behaviour.
    def __init__(self, label: str, colors: tuple[int, int, int]) -> None:
        self._text_input = QLineEdit()
        self._text_input.setStyleSheet(
            TEXT_BOX_STYLE + f"color: rgb({colors[0]}, {colors[1]}, {colors[2]});"
        )
        self._text_input.textChanged.connect(self.adjust_width)
        self._text_input.setText(label)


    # Return the QLineEdit object for the modified class
    @property
    def object(self) -> QLineEdit: return self._text_input


    # Adjust the widget width to match the current text content (capped).
    def adjust_width(self) -> None:
        metrics = self._text_input.fontMetrics()
        text_width = metrics.horizontalAdvance(self._text_input.text())
        self._text_input.setFixedWidth(min(text_width + 25, 100))

