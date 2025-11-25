
# utils/ui.py

#- Imports -----------------------------------------------------------------------------------------

import sys
from typing import Tuple, Any, Callable

from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QBoxLayout,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)

from .style import (
    BUTTON_STYLE,
    TEXT_BODY,
)


#- Lib ---------------------------------------------------------------------------------------------

def new_color() -> Tuple[int, int, int]:
    from random import randint
    return (randint(0, 255), randint(60, 255), randint(0, 200))


def spacedh(layout: QHBoxLayout) -> None:
    spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Preferred)
    layout.addItem(spacer)


def spacedv(layout: QVBoxLayout) -> None:
    spacer = QSpacerItem(20, 20, QSizePolicy.Preferred, QSizePolicy.Expanding)
    layout.addItem(spacer)


def blank_line(layout: QVBoxLayout) -> None:
    line = QLabel()
    line.setFixedHeight(2)
    layout.addWidget(line)


def labelled_text_widget(
    title: str, value: str, placeholder: str, parent_layout: QBoxLayout
) -> QLineEdit:
    layout = QHBoxLayout()

    text_label = QLabel(title)
    text_label.setStyleSheet(TEXT_BODY)
    text_label.setFixedWidth(100)
    layout.addWidget(text_label)

    text_input = QLineEdit()
    text_input.setPlaceholderText(placeholder)
    text_input.setText(value)
    text_input.setStyleSheet(TEXT_BODY)
    layout.addWidget(text_input)

    parent_layout.addLayout(layout)
    return text_input


def create_button(
        text: str, hover: str, callback: Callable[..., None], *cb_args: Any, **cb_kwargs: Any
    ) -> QPushButton:

    button = QPushButton(text)
    button.setStyleSheet(BUTTON_STYLE)
    button.setToolTip(hover)

    button.clicked.connect(lambda checked=False: callback(*cb_args, **cb_kwargs))
    return button


def alert_box(status: str, message: str) -> None:
    print(f"[{status}] {message}", file=sys.stderr)

    msg_box = QMessageBox()
    msg_box.setWindowTitle(status)
    msg_box.setText(message)
    msg_box.exec_()


class EditLabel(QLineEdit):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.setStyleSheet("max-width: 40px; padding: 2px;")
        self.textChanged.connect(self.adjustWidth)
        self.setText(label)


    def adjustWidth(self) -> None:
        metrics = self.fontMetrics()
        text_width = metrics.horizontalAdvance(self.text())
        self.setFixedWidth(min(text_width + 10, 100))

