
# window/gesture_dialog.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from utils.ui import (
    create_button,
)
from utils.typedefs import GestureData, GestureUpdater


#- Tab Class ---------------------------------------------------------------------------------------

class Tab2:

    def __init__(self, parent: QDialog, parent_layout: QWidget, input_names: List[str]) -> None:
        self.parent = parent
        self.input_names: List[str] = input_names

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self.layout)

        self.init_buttons()


    def init_buttons(self) -> None:
        button_layout = QHBoxLayout()

        self.cancel_button = create_button("Cancel", self.parent.reject)
        self.continue_button = create_button("Continue", self.parent.submit, 2) # calling from tab 2

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.continue_button)

        self.layout.addLayout(button_layout)


    def get_inputs(self) -> Optional[GestureUpdater]:
        return None

