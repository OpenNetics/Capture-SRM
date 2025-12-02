
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

from utils.extra import file_name_path
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

        self._parent = parent
        self._submit: Callable[[int], None] = submit
        self._cancel: Callable[[], None] = cancel
        self._input_names: List[str] = input_names

        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self._layout)

        self._init_input_fields()
        self._init_checkboxes()
        self._init_model_params()
        self._init_buttons()

    #- Private: init modules -----------------------------------------------------------------------

    # Create line edits for gesture name and repeats with a browse/save helper.
    def _init_input_fields(self) -> None:
        # Gesture Name
        file_name_layout = QHBoxLayout()

        self._gesture_file = QLineEdit(self._parent)
        self._gesture_file.setPlaceholderText("Gesture Name")
        self._gesture_file.setToolTip("Path to save gesture file to.")
        self._gesture_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_name_layout.addWidget(self._gesture_file, 1)

        browse_button = create_button(
            "Browse", "Path to save gesture file to.", self._init_input_filepath)

        browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_name_layout.addWidget(browse_button, 0)

        self._layout.addLayout(file_name_layout)

        # Repeats
        self._repeats_input = QLineEdit(self._parent)
        self._repeats_input.setToolTip("Number of times to repeat the gesture recording.")
        self._repeats_input.setPlaceholderText("Repeats (integer)")
        self._layout.addWidget(self._repeats_input)


    # Open file dialog to choose target save path for the gesture file.
    def _init_input_filepath(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(
            self._parent, "Save Gesture", "", "Gesture Files (*.ges);;All Files (*)",
            options=QFileDialog.Options()
        )
        if file_path:
            self._gesture_file.setText(file_path)


    # Build sensor selection checkboxes for available input names.
    def _init_checkboxes(self) -> None:
        blank_line(self._layout)

        text_label = QLabel("Select Sensors")
        text_label.setStyleSheet(TEXT_HEAD)
        self._layout.addWidget(text_label)

        # Sensor Select Checkboxes
        self._sensor_checkboxes: List[QCheckBox] = []
        for name in self._input_names:
            checkbox = QCheckBox(name, self._parent)
            self._sensor_checkboxes.append(checkbox)
            self._layout.addWidget(checkbox)


    # Add widgets to configure model parameters (random state, n components, threshold).
    def _init_model_params(self) -> None:
        blank_line(self._layout)

        text_label = QLabel("Model Parameters")
        text_label.setStyleSheet(TEXT_HEAD)
        self._layout.addWidget(text_label)

        self._random_state_label = labelled_text_widget(
            LABEL_RANDOM_STATE, "42", "integer in the range [0, 4294967295]", self._layout)

        self._n_components_label = labelled_text_widget(
            LABEL_N_COMPONENTS, "2", "positive integer", self._layout)

        self._threshold_label = labelled_text_widget(
            LABEL_THRESHOLD, "-10", "", self._layout)


    # Create Cancel / Continue buttons and wire them to actions.
    def _init_buttons(self) -> None:
        blank_line(self._layout)
        spacedv(self._layout)
        button_layout = QHBoxLayout()

        self._cancel_button = create_button("Cancel", "[esc]" ,self._cancel)
        self._continue_button = create_button("Continue", "[return]", self._finish)

        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._continue_button)

        self._layout.addLayout(button_layout)

    #- Private: actions ----------------------------------------------------------------------------

    # Validate inputs, assemble GestureInput dataclass and submit tab result.
    def _finish(self) -> None:
        name = file_name_path(self._gesture_file.text())
        error = check_empty_string(name, "Gesture Name: Missing title.")
        if error:
            return None

        repeats = check_string_numeric(
            self._repeats_input,
            "Repeat Count: Enter valid integer.", int, 1
        )
        if not repeats: return None

        selected_sensors = check_checkboxes_ticked(
            self._sensor_checkboxes,
            1, "Sources: Select sources to record."
        )
        if not selected_sensors: return None

        random_state = check_string_numeric(
            self._random_state_label,
            "Random State: Enter integer value in the valid range", int, 0, 4294967295
        )
        if random_state is None: return None

        threshold = check_string_numeric(
            self._threshold_label,
            "Threshold: Enter valid integer value.", float
        )
        if threshold is None: return None

        n_components = check_string_numeric(
            self._n_components_label,
            "n Component: Enter valid integer value.", int, 1
        )
        if not n_components: return None

        self._values = GestureInput(
            name=name,
            repeats=repeats,
            sensors=tuple(selected_sensors), # convert sensors list -> tuple for immutability
            parameters=ModelParameters(random_state, n_components, threshold)
        )

        self._submit(TAB1)

    #- Public Calls --------------------------------------------------------------------------------

    # Return assembled GestureInput values if finish() previously validated them.
    def get_inputs(self) -> Optional[GestureInput]:
        return self._values if hasattr(self, '_values') else None

    #- Keyboard Shortcut Override ------------------------------------------------------------------

    # Map keyboard events to dialog interactions (enter/escape).
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self._continue_button.click()
        elif event.key() == Qt.Key_Escape:
            self._cancel_button.click()
        else:
            super().keyPressEvent(event)

