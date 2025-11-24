
# window/gesture_dialog_tab1.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QDialog,
    QLineEdit,
    QCheckBox,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
)

from utils.style import TAB1, TEXT_HEAD
from utils.typedefs import GestureInput
from utils.ui import (
    spacedv,
    blank_line,
    create_button,
    labelled_text_widget,
)
from .checks import (
    check_empty_string,
    check_string_numeric,
    check_checkboxes_ticked
)


#- Tab Class ---------------------------------------------------------------------------------------

class Tab1:

    def __init__(self, parent: QDialog, parent_layout: QWidget, input_names: List[str]) -> None:
        self.parent = parent
        self.input_names: List[str] = input_names

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self.layout)

        self.init_input_fields()
        self.init_checkboxes()
        self.init_model_params()
        self.init_buttons()


    def init_input_fields(self) -> None:
        # Gesture Name
        file_name_layout = QHBoxLayout()

        self.gesture_file = QLineEdit(self.parent)
        self.gesture_file.setPlaceholderText("Gesture Name")
        self.gesture_file.setToolTip("Path to save gesture file to.")
        self.gesture_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_name_layout.addWidget(self.gesture_file, 1)

        browse_button = create_button("Browse", self.init_input_filepath)
        browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_name_layout.addWidget(browse_button, 0)

        self.layout.addLayout(file_name_layout)

        # Repeats
        self.repeats_input = QLineEdit(self.parent)
        self.repeats_input.setPlaceholderText("Repeats (integer)")
        self.layout.addWidget(self.repeats_input)


    def init_input_filepath(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Save Gesture", "", "Gesture Files (*.ges);;All Files (*)",
            options=QFileDialog.Options()
        )
        if file_path:
            self.gesture_file.setText(file_path)


    def init_checkboxes(self) -> None:
        blank_line(self.layout)

        text_label = QLabel("Select Sensors")
        text_label.setStyleSheet(TEXT_HEAD)
        self.layout.addWidget(text_label)

        # Sensor Select Checkboxes
        self.sensor_checkboxes: List[QCheckBox] = []
        for name in self.input_names:
            checkbox = QCheckBox(name, self.parent)
            self.sensor_checkboxes.append(checkbox)
            self.layout.addWidget(checkbox)


    def init_model_params(self) -> None:
        blank_line(self.layout)

        text_label = QLabel("Model Parameters")
        text_label.setStyleSheet(TEXT_HEAD)
        self.layout.addWidget(text_label)

        self.random_state_label = labelled_text_widget(
            "Random State", "42", "integer in the range [0, 4294967295]", self.layout)

        self.n_component_label = labelled_text_widget(
            "n Component", "2", "positive integer", self.layout)

        self.threshold_label = labelled_text_widget(
            "Threshold", "-10", "", self.layout)


    def init_buttons(self) -> None:
        blank_line(self.layout)
        spacedv(self.layout)
        button_layout = QHBoxLayout()

        self.cancel_button = create_button("Cancel", self.parent.reject)
        self.continue_button = create_button("Continue", self.parent.submit, TAB1) # calling from tab 1

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.continue_button)

        self.layout.addLayout(button_layout)


    def get_inputs(self) -> Optional[GestureInput]:
        # validate fields first
        error = check_empty_string(self.gesture_file.text(), "Gesture Name: Missing title.")
        if error:
            return None
        name = self.gesture_file.text()

        repeats = check_string_numeric(
            self.repeats_input,
            "Repeat Count: Enter valid integer.", int, 1
        )
        if not repeats: return None

        selected_sensors = check_checkboxes_ticked(
            self.sensor_checkboxes,
            1, "Sources: Select sources to record."
        )
        if not selected_sensors: return None

        random_state = check_string_numeric(
            self.random_state_label,
            "Random State: Enter integer value in the valid range", int, 0, 4294967295
        )
        if random_state is None: return None

        threshold = check_string_numeric(
            self.threshold_label,
            "Threshold: Enter valid integer value.", float
        )
        if threshold is None: return None

        n_component = check_string_numeric(
            self.n_component_label,
            "n Component: Enter valid integer value.", int, 1
        )
        if not n_component: return None

        return GestureInput(
            name=name,
            repeats=repeats,
            sensors=tuple(selected_sensors), # convert sensors list -> tuple for immutability
            parameters=(random_state, n_component, threshold)
        )


    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.continue_button.click()
        elif event.key() == Qt.Key_Escape:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)


