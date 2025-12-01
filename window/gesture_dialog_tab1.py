
# window/gesture_dialog_tab1.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Callable, List, Optional

from redwrenlib.typing import ModelParameters
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget,
    QCheckBox, QFileDialog, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout,
    QSizePolicy,
)

from utils.style import TEXT_HEAD
from utils.typing import (
    TAB1,
    LABEL_RANDOM_STATE, LABEL_N_COMPONENTS, LABEL_THRESHOLD,
    GestureInput,
)
from utils.ui import (
    spacedv, blank_line,
    create_button, labelled_text_widget,
)
from .checks import (
    check_empty_string,
    check_string_numeric,
    check_checkboxes_ticked
)


#- Tab Class ---------------------------------------------------------------------------------------

# Tab responsible for collecting inputs needed to record a new gesture.
class Tab1:

    # Initialise fields, checkboxes, model parameter inputs and action buttons.
    def __init__(
            self,
            parent: QDialog,
            parent_layout: QWidget,
            input_names: List[str],
            submit: Callable[[int], None],
            cancel: Callable[[], None]
        ) -> None:

        self.parent = parent
        self.submit: Callable[[int], None] = submit
        self.cancel: Callable[[], None] = cancel
        self.input_names: List[str] = input_names

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self.layout)

        self.init_input_fields()
        self.init_checkboxes()
        self.init_model_params()
        self.init_buttons()

    #- Init Modules --------------------------------------------------------------------------------

    # Create line edits for gesture name and repeats with a browse/save helper.
    def init_input_fields(self) -> None:
        # Gesture Name
        file_name_layout = QHBoxLayout()

        self.gesture_file = QLineEdit(self.parent)
        self.gesture_file.setPlaceholderText("Gesture Name")
        self.gesture_file.setToolTip("Path to save gesture file to.")
        self.gesture_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_name_layout.addWidget(self.gesture_file, 1)

        browse_button = create_button(
            "Browse", "Path to save gesture file to.", self.init_input_filepath)

        browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_name_layout.addWidget(browse_button, 0)

        self.layout.addLayout(file_name_layout)

        # Repeats
        self.repeats_input = QLineEdit(self.parent)
        self.repeats_input.setToolTip("Number of times to repeat the gesture recording.")
        self.repeats_input.setPlaceholderText("Repeats (integer)")
        self.layout.addWidget(self.repeats_input)


    # Open file dialog to choose target save path for the gesture file.
    def init_input_filepath(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self.parent, "Save Gesture", "", "Gesture Files (*.ges);;All Files (*)",
            options=QFileDialog.Options()
        )
        if file_path:
            self.gesture_file.setText(file_path)


    # Build sensor selection checkboxes for available input names.
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


    # Add widgets to configure model parameters (random state, n components, threshold).
    def init_model_params(self) -> None:
        blank_line(self.layout)

        text_label = QLabel("Model Parameters")
        text_label.setStyleSheet(TEXT_HEAD)
        self.layout.addWidget(text_label)

        self.random_state_label = labelled_text_widget(
            LABEL_RANDOM_STATE, "42", "integer in the range [0, 4294967295]", self.layout)

        self.n_components_label = labelled_text_widget(
            LABEL_N_COMPONENTS, "2", "positive integer", self.layout)

        self.threshold_label = labelled_text_widget(
            LABEL_THRESHOLD, "-10", "", self.layout)


    # Create Cancel / Continue buttons and wire them to actions.
    def init_buttons(self) -> None:
        blank_line(self.layout)
        spacedv(self.layout)
        button_layout = QHBoxLayout()

        self.cancel_button = create_button("Cancel", "[esc]" ,self.cancel)
        self.continue_button = create_button("Continue", "[return]", self.finish)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.continue_button)

        self.layout.addLayout(button_layout)

    #- Getters and Actions -------------------------------------------------------------------------

    # Return assembled GestureInput values if finish() previously validated them.
    def get_inputs(self) -> Optional[GestureInput]:
        return self.values if hasattr(self, 'values') else None


    # Validate inputs, assemble GestureInput dataclass and submit tab result.
    def finish(self) -> None:
        name = self.gesture_file.text()
        error = check_empty_string(name, "Gesture Name: Missing title.")
        if error:
            return None

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

        n_components = check_string_numeric(
            self.n_components_label,
            "n Component: Enter valid integer value.", int, 1
        )
        if not n_components: return None

        self.values = GestureInput(
            name=name,
            repeats=repeats,
            sensors=tuple(selected_sensors), # convert sensors list -> tuple for immutability
            parameters=ModelParameters(random_state, n_components, threshold)
        )

        self.submit(TAB1)

    #- Key Events ----------------------------------------------------------------------------------

    # Map keyboard events to dialog interactions (enter/escape).
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.continue_button.click()
        elif event.key() == Qt.Key_Escape:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)

