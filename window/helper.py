
# window/helper.py

#- Imports -----------------------------------------------------------------------------------------

from random import randint

from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
)

from .style import BUTTON_STYLE


#- Lib ---------------------------------------------------------------------------------------------

def new_color() -> (int, int, int):
    return (randint(0, 255), randint(60, 255), randint(0, 200))


def spaced_element(layout) -> None:
    spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Preferred)
    layout.addItem(spacer)


def blank_line(layout: QHBoxLayout) -> None:
    line = QLabel()
    line.setFixedHeight(1)
    layout.addWidget(line)


def create_button(text: str, callback: callable) -> QPushButton:
    button = QPushButton(text)
    button.setStyleSheet(BUTTON_STYLE)
    button.clicked.connect(callback)

    return button


def alert_box(window, status: str, message: str) -> None:
    msg_box = QMessageBox(window)
    msg_box.setIcon(QMessageBox.NoIcon)
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

