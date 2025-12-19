
# window/gesture_dialog_tab3.py

#- Imports -----------------------------------------------------------------------------------------

from dataclasses import dataclass
from typing import Callable, Optional

from redwrenlib import GestureFile
from redwrenlib.utils.debug import alert
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget, QFrame,
    QComboBox, QFileDialog, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QScrollArea,
    QSizePolicy,
)

from utils.ui import alert_box, clear_layout
from utils.style import (
    SCROLL_HEIGHT, LABEL_HEAD_STYLE, LABEL_BODY_STYLE,
    COMBOBOX_STYLE, TEXT_BOX_STYLE, SCROLL_BAR_STYLE,
)
from utils.typing import(
    LABEL_RANDOM_STATE, LABEL_N_COMPONENTS, LABEL_THRESHOLD,
    GestureInput, ModelParameters, Tab
)
from utils.ui import (
    spacedv, blank_line, create_button,
)

from .labelled_text import LabelledText
from .gesture_dialog_tab2 import Tab2

#- Tab Class ---------------------------------------------------------------------------------------

# Tab responsible for collecting inputs needed to update existing gesture.
class Tab3(Tab2):

    # Initialise fields, sensor list, model parameter inputs and action buttons.
    def __init__(
            self,
            parent: QDialog,
            parent_layout: QWidget,
            input_names: tuple[str, ...],
            submit: Callable[[Tab], None],
            cancel: Callable[[], None],
        ) -> None:

        super().__init__(parent, parent_layout, input_names, submit, cancel)


    # Create Cancel / Save buttons and wire them to actions.
    def _init_buttons(self) -> None:
        blank_line(self._layout)
        spacedv(self._layout)
        button_layout = QHBoxLayout()

        self._cancel_button = create_button("Cancel", "[esc]", self._cancel)
        self._continue_button = create_button("Save", "[return]", self._finish)

        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._continue_button)

        self._layout.addLayout(button_layout)


    def _dynamic_source_list(self) -> None:
        print("hello world")
        pass


    def _finish(self) -> None:
        pass

    def get_inputs(self) -> None: return None
