
# window/gesture_dialog_tab1.py

#- Imports -----------------------------------------------------------------------------------------

from dataclasses import dataclass
from typing import Callable, Optional

from opennetics.utils import defaults
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget, QFrame,
    QCheckBox, QFileDialog, QLabel, QLineEdit,
    QVBoxLayout, QHBoxLayout, QScrollArea,
    QSizePolicy,
)

from utils.extra import file_name_path, datestring
from utils.style import (
    SCROLL_HEIGHT,
    LABEL_HEAD_STYLE, SCROLL_BAR_STYLE, TEXT_BOX_STYLE
)
from utils.typing import (
    LABEL_RANDOM_STATE, LABEL_N_COMPONENTS, LABEL_THRESHOLD,
    GestureInput, ModelParameters, Tab
)
from utils.ui import (
    spacedv, blank_line, create_button
)

from .labelled_text import LabelledText
from .checks import (
    check_empty_string,
    check_string_numeric,
)


#- Local Defines -----------------------------------------------------------------------------------

@dataclass
class ModelParametersLabels:
    checkbox: QCheckBox
    threshold: LabelledText
    n_components: LabelledText
    random_state: LabelledText
    whitespace: QLabel


#- Tab Class ---------------------------------------------------------------------------------------

# Tab responsible for collecting inputs needed to record a new gesture.
class Tab1:

    # Initialise fields, checkboxes, model parameter inputs and action buttons.
    def __init__(
            self,
            parent: QDialog,
            parent_layout: QWidget,
            input_names: tuple[str, ...],
            submit: Callable[[Tab], None],
            cancel: Callable[[], None]
        ) -> None:

        #========================================
        # class vars with their init values
        #========================================
        self._parent = parent
        self._submit = submit
        self._cancel = cancel
        self._input_names = input_names

        self._params_labels: dict[str, ModelParametersLabels] = {}

        #========================================
        # master Layout
        #========================================
        self._layout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self._layout)

        #========================================
        # initialise the system
        #========================================
        self._init_input_fields()
        self._init_checkboxes()
        self._init_buttons()


    #- Private: init modules -----------------------------------------------------------------------

    # Create line edits for gesture name and repeats with a browse/save helper.
    def _init_input_fields(self) -> None:
        #========================================
        # gesture file name (/path)
        #========================================
        file_name_layout = QHBoxLayout()

        # text box for manual path
        self._gesture_file = QLineEdit(self._parent)
        self._gesture_file.setPlaceholderText("Gesture Name")
        self._gesture_file.setToolTip("Path to save gesture file to.")
        self._gesture_file.setStyleSheet(TEXT_BOX_STYLE)
        self._gesture_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_name_layout.addWidget(self._gesture_file, 1)

        # browse button to select path interactively using OS's file manager
        browse_button = create_button(
            "Browse", "Path to save gesture file to.", self._init_input_filepath)

        browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_name_layout.addWidget(browse_button, 0)

        self._layout.addLayout(file_name_layout)

        #========================================
        # repeats: how many times to perform a gesture for study
        #========================================
        self._repeats_input = QLineEdit(self._parent)
        self._repeats_input.setToolTip("Number of times to repeat the gesture recording.")
        self._repeats_input.setPlaceholderText("Repeats (integer)")
        self._repeats_input.setStyleSheet(TEXT_BOX_STYLE)
        self._layout.addWidget(self._repeats_input)


    # Open file dialog to choose target save path for the gesture file.
    def _init_input_filepath(self) -> None:
        # placeholder filename would be datestring()
        file_path, _ = QFileDialog.getSaveFileName(
            self._parent, "Save Gesture", datestring(), "Gesture Files (*.srm);;All Files (*)",
            options = QFileDialog.Options()
        )

        # add selected file path as file text box label
        if file_path: self._gesture_file.setText(file_path)


    # Build sensor selection checkboxes for available input names.
    def _init_checkboxes(self) -> None:
        #========================================
        # section heading
        #========================================
        blank_line(self._layout)
        text_label = QLabel("Select Sensors")
        text_label.setStyleSheet(LABEL_HEAD_STYLE)
        self._layout.addWidget(text_label)

        #========================================
        # scroll area
        #========================================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setMinimumHeight(SCROLL_HEIGHT)
        scroll_area.setStyleSheet(SCROLL_BAR_STYLE)

        label_frame = QFrame(scroll_area)
        label_layout = QVBoxLayout(label_frame)
        scroll_area.setWidget(label_frame)

        self._layout.addWidget(scroll_area)

        #========================================
        # sensor select checkboxes
        #========================================
        for name in self._input_names:
            # the checkbox itself
            checkbox = QCheckBox(name, self._parent)
            checkbox.stateChanged.connect(
                lambda state, name=name: self._toggle_model_parameters(state, name)
            )
            label_layout.addWidget(checkbox)

            # whitespace under the list before the next checkbox
            space_label = QLabel("")
            space_label.setVisible(False)
            space_label.setFixedHeight(1)

            # checkbox's parameters
            # hidden by default, are visible when the checkbox is selected
            params_holder = QHBoxLayout() # hold all parameter LabelledTexts in horizontal group
            self._params_labels[name] = ModelParametersLabels(
                checkbox=checkbox,

                threshold=LabelledText(
                    LABEL_THRESHOLD, str(defaults.MODEL_THRESHOLD),
                    "", params_holder, visible=False
                ),

                random_state=LabelledText(
                    LABEL_RANDOM_STATE, str(defaults.MODEL_RANDOM_STATE),
                    "integer in the range [0, 4294967295]", params_holder, visible=False
                ),

                n_components=LabelledText(
                    LABEL_N_COMPONENTS, str(defaults.MODEL_N_COMPONENTS),
                    "positive integer", params_holder, visible=False
                ),

                whitespace = space_label
            )
            label_layout.addLayout(params_holder)
            label_layout.addWidget(space_label)

        spacedv(label_layout)


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

    # Make model parameters visible for the selected models
    def _toggle_model_parameters(self, state: int, label: str) -> None:
        visible = state == 2  # Checkbox is checked

        self._params_labels[label].threshold.visibility(visible)
        self._params_labels[label].n_components.visibility(visible)
        self._params_labels[label].random_state.visibility(visible)
        self._params_labels[label].whitespace.setVisible(visible)


    # Validate inputs, assemble GestureInput dataclass and submit tab result.
    # Prepare the class return type, self._values, which is otherwise None.
    def _finish(self) -> None:
        #========================================
        # ensure gesture filename is valid path
        #========================================
        name = file_name_path(self._gesture_file.text())
        error = check_empty_string(name, "Gesture Name: Missing title.")
        if error: return None

        #========================================
        # ensure repeates count is a valid integer
        #========================================
        repeats = check_string_numeric(
            self._repeats_input.text(), "Repeat Count: Enter valid integer.", int, 1
        )
        if not repeats: return None

        #========================================
        # checked checkboxes and their values
        #========================================
        source_ids: list[int] = []
        params: list[ModelParameters] = []

        # Break if any model parameter value isn't valid
        for i, label in enumerate(self._params_labels.keys()):
            if not self._params_labels[label].checkbox.isChecked():
                # only check values if the checkbox is selected
                continue

            random_state = check_string_numeric(
                self._params_labels[label].random_state.text(),
                f"[{label}] Random State: Enter integer value in the valid range",
                int, 0, 4294967295
            )
            if random_state is None: return None

            threshold = check_string_numeric(
                self._params_labels[label].threshold.text(),
                f"[{label}] Threshold: Enter valid integer value.", float
            )
            if threshold is None: return None

            n_components = check_string_numeric(
                self._params_labels[label].n_components.text(),
                f"[{label}] n Component: Enter valid integer value.", int, 1
            )
            if n_components is None: return None

            # add to the dictionary with the index of the sensor/source as key
            source_ids.append(i)
            params.append(ModelParameters(threshold, random_state, n_components))

        #========================================
        # return type, self._values, generated when all values are valid
        #========================================
        self._values = GestureInput(
            filename = name,
            repeats  = repeats,
            parameters = tuple(params),
            source_ids = tuple(source_ids),
            file_sources = tuple(self._input_names[i] for i in source_ids)
        )

        self._submit(Tab.CREATE) # close the window with success return


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

