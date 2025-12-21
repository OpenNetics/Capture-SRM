
# window/edit_label.py

#- Imports -----------------------------------------------------------------------------------------

from PySide6.QtWidgets import QLineEdit

from utils.style import TEXT_BOX_STYLE


#- EditLabel class ---------------------------------------------------------------------------------

# Simple editable label that auto-resizes to fit its text.
class EditLabel():

    # Initialise EditLabel with given text and set up auto-resize behaviour.
    def __init__(self, label: str, color: str) -> None:
        self._text_input = QLineEdit()
        self._text_input.setStyleSheet(TEXT_BOX_STYLE + f"color: {color};")
        self._text_input.textChanged.connect(self._adjust_width)
        self._text_input.setText(label)


    #- Class Properties ----------------------------------------------------------------------------

    # Return the QLineEdit object for the modified class.
    @property
    def object(self) -> QLineEdit: return self._text_input


    #- Private Methods -----------------------------------------------------------------------------

    # Adjust the widget width to match the current text content (capped).
    def _adjust_width(self) -> None:
        metrics = self._text_input.fontMetrics()
        text_width = metrics.horizontalAdvance(self._text_input.text())
        self._text_input.setFixedWidth(min(text_width + 25, 100))


    #- Public Methods ------------------------------------------------------------------------------

    # Change style of the Label. Add on top of the default style.
    def style(self, color: str, decor_css: str="") -> None:
        self._text_input.setStyleSheet(TEXT_BOX_STYLE + f"color: {color}; {decor_css}")

