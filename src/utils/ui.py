
# utils/ui.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any, Callable

from redwrenlib.utils.debug import alert
from PySide6.QtWidgets import (
    QLabel, QLineEdit, QMessageBox, QPushButton, QSpacerItem,
    QBoxLayout, QHBoxLayout, QVBoxLayout, QLayout,
    QSizePolicy,
)

from .style import (
    BUTTON_STYLE, TEXT_BOX_STYLE, LABEL_BODY_STYLE,
)


#- Lib ---------------------------------------------------------------------------------------------

# Insert a horizontal expanding spacer into a QHBoxLayout.
def spacedh(layout: QHBoxLayout) -> None:
    spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Preferred)
    layout.addItem(spacer)


# Insert a vertical expanding spacer into a QVBoxLayout.
def spacedv(layout: QVBoxLayout) -> None:
    spacer = QSpacerItem(20, 20, QSizePolicy.Preferred, QSizePolicy.Expanding)
    layout.addItem(spacer)


# Add a small blank QLabel line used as a separator in vertical layouts.
def blank_line(layout: QVBoxLayout) -> None:
    line = QLabel()
    line.setFixedHeight(2)
    layout.addWidget(line)


# Create a styled QPushButton wired to the given callback and arguments.
def create_button(
        text: str, hover: str, callback: Callable[..., None], *cb_args: Any, **cb_kwargs: Any
    ) -> QPushButton:

    button = QPushButton(text)
    button.setStyleSheet(BUTTON_STYLE)
    button.setToolTip(hover)

    button.clicked.connect(lambda checked=False: callback(*cb_args, **cb_kwargs))
    return button


# Show a simple QMessageBox (also prints to stderr) for alerts and errors.
def alert_box(status: str, message: str) -> None:
    # backtrack twice to refer the code-block that called alert_box()
    alert(message, backtrack=2, level="error")

    msg_box = QMessageBox()
    msg_box.setWindowTitle(status)
    msg_box.setText(message)
    msg_box.exec_()

def clear_layout(layout: QLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        if item is None: continue

        widget = item.widget()
        if widget:
            widget.setParent(None)
            widget.deleteLater()
            continue

        child_layout = item.layout()
        if child_layout:
            clear_layout(child_layout)
            layout.removeItem(item)
            child_layout.deleteLater()


#- Custom UI Elements ------------------------------------------------------------------------------

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


    # Adjust the widget width to match the current text content (capped).
    def adjust_width(self) -> None:
        metrics = self._text_input.fontMetrics()
        text_width = metrics.horizontalAdvance(self._text_input.text())
        self._text_input.setFixedWidth(min(text_width + 25, 100))

    def obj(self) -> QLineEdit:
        return self._text_input


# Textfield with label next to it.
class LabelledText:

    # Initialise LabelledText with a label and a textbox.
    def __init__(
        self, title: str, value: str, tip: str, parent_layout: QBoxLayout,
        visible: bool = True
    ) -> None:
        layout = QHBoxLayout()

        # label
        self._text_label = QLabel(title)
        self._text_label.setVisible(visible)
        self._text_label.setStyleSheet(LABEL_BODY_STYLE)
        layout.addWidget(self._text_label)

        # text box
        self._text_input = QLineEdit()
        self._text_input.setVisible(visible)
        self._text_input.setPlaceholderText(value)
        self._text_input.setToolTip(tip)
        self._text_input.setText(value)
        self._text_input.setStyleSheet(TEXT_BOX_STYLE)
        layout.addWidget(self._text_input)

        parent_layout.addLayout(layout)

    # Toggle visibility of the two components.
    def visibility(self, visible: bool) -> None:
        self._text_label.setVisible(visible)
        self._text_input.setVisible(visible)

    # Retrieve value of the text box.
    def text(self) -> str:
        return self._text_input.text()

