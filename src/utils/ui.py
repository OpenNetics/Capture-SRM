
# utils/ui.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any, Callable

from redwrenlib.utils.debug import alert
from PySide6.QtWidgets import (
    QLabel, QMessageBox, QPushButton, QSpacerItem,
    QHBoxLayout, QVBoxLayout, QLayout,
    QSizePolicy,
)

from .style import BUTTON_STYLE


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


# Delete all elemets in recursive from a layout.
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

