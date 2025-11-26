
# window/gesture_dialog_tab2.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Callable, List, Optional, Union, Tuple

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget,
    QComboBox, QFileDialog, QLabel, QLineEdit,
    QLayout, QVBoxLayout, QHBoxLayout,
    QSizePolicy,
)

from utils.style import (
    TEXT_HEAD, TEXT_BODY,
    COMBOBOX_STYLE,
)
from utils.typing import(
    TAB2,
    LABEL_RANDOM_STATE, LABEL_N_COMPONENT, LABEL_THRESHOLD,
    GestureData, GestureInput, GestureUpdater, ModelParameters
)
from utils.ui import (
    spacedv, blank_line,
    create_button, labelled_text_widget,
)
from analyse import read_gesture

from .checks import (
    check_empty_string,
    check_string_numeric,
)


#- Tab Class ---------------------------------------------------------------------------------------

# Tab responsible for collecting inputs needed to update existing gesture.
class Tab2:

    # Initialise fields, sensor list, model parameter inputs and action buttons.
    def __init__(
            self,
            parent: QDialog,
            parent_layout: QWidget,
            input_names: List[str],
            submit: Callable[[int], None]
        ) -> None:

        self.parent = parent
        self.submit: Callable[[int], None] = submit
        self.input_names: List[str] = input_names

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self.layout)

        self.init_filename() # add file selection on main layout

        self.body_layout = QVBoxLayout() # layout for dynamic content
        self.layout.addLayout(self.body_layout)

        self.init_buttons()  # add buttons on main layout

    #- Init Modules --------------------------------------------------------------------------------

    # Add widgets to find select gesture files. Add load button to call function to load file data.
    def init_filename(self) -> None:
        # Gesture Name
        file_name_layout = QHBoxLayout()

        self.gesture_file = QLineEdit(self.parent)
        self.gesture_file.setPlaceholderText("Gesture Path")
        self.gesture_file.setToolTip("File to further update.")
        self.gesture_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_name_layout.addWidget(self.gesture_file, 1)

        browse_button = create_button("Browse", "File to further update.", self.init_input_filepath)
        browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_name_layout.addWidget(browse_button, 0)

        self.layout.addLayout(file_name_layout)

        load_data = create_button("Load File Data", "", self.dynamic_source_list)
        self.layout.addWidget(load_data)


    # Browse button action: open file dialog to choose target gesture file.
    def init_input_filepath(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Open Gesture File", "", "Gesture Files (*.ges);;All Files (*)",
            options=QFileDialog.Options()
        )
        if not file_path: return

        self.gesture_file.setText(file_path)


    # Create Cancel / Continue buttons and wire them to actions.
    def init_buttons(self) -> None:
        blank_line(self.layout)
        spacedv(self.layout)
        button_layout = QHBoxLayout()

        self.cancel_button = create_button("Cancel", "[esc]", self.parent.reject)
        self.continue_button = create_button("Continue", "[return]", self.finish)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.continue_button)

        self.layout.addLayout(button_layout)

    #- Dynamically Generated Modules ---------------------------------------------------------------

    # Read file data and add dynamic widgets to body layout, with data from gesture file.
    def dynamic_source_list(self) -> None:
        self.gesture_data: Optional[GestureData] = read_gesture(self.gesture_file.text())
        if self.gesture_data is None: return

        # clear previous body layout
        while self.body_layout.count():
            item: QLayout = self.body_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        blank_line(self.body_layout)
        label = QLabel("Available Sources:")
        label.setStyleSheet(TEXT_HEAD)
        self.body_layout.addWidget(label)

        self.drop_boxes: List[QComboBox] = []

        for model in self.gesture_data.models.keys():
            label_holder: QHBoxLayout = QHBoxLayout()

            text_label = QLabel(model)
            text_label.setStyleSheet(TEXT_BODY)
            text_label.setFixedWidth(100)
            label_holder.addWidget(text_label)

            input_name_list = QComboBox()
            input_name_list.addItems(["<UNCHANGED>"] + self.input_names)
            input_name_list.setStyleSheet(COMBOBOX_STYLE)
            self.drop_boxes.append(input_name_list)
            label_holder.addWidget(input_name_list)

            self.body_layout.addLayout(label_holder)

        self.dynamic_data_usage()


    # Use the read data to autofill model parameters. Allow editing them for future training.
    def dynamic_data_usage(self) -> None:
        blank_line(self.body_layout)
        label = QLabel("New Training Model Parameters:")
        label.setStyleSheet(TEXT_HEAD)
        self.body_layout.addWidget(label)

        self.entered_parameters: dict[str,QLineEdit] = {}
        blank_line(self.body_layout)
        def show_saved_values(label: str, value: Union[int, float, None]) -> None:
            text_label = str(value) if value is not None else "None Saved"
            text_widget = labelled_text_widget(label, text_label, text_label, self.body_layout)
            self.entered_parameters[label] = (text_widget)

        show_saved_values(LABEL_RANDOM_STATE, self.gesture_data.parameters.random_state)
        show_saved_values(LABEL_N_COMPONENT, self.gesture_data.parameters.n_component)
        show_saved_values(LABEL_THRESHOLD, self.gesture_data.parameters.threshold)

        repeats_widget = labelled_text_widget("Repeats", "", "Positive Integer", self.body_layout)
        repeats_widget.setToolTip("Number of times to repeat the gesture recording.")
        self.entered_parameters["repeats"] = (repeats_widget)

        spacedv(self.body_layout)

    #- Getters and Actions -------------------------------------------------------------------------

    # Return tuple of source matches
    def source_matches(self) -> Optional[Tuple[int, ...]]:
        return None


    # Return assembled GestureUpdater values if finish() previously validated them.
    def get_inputs(self) -> Optional[GestureUpdater]:
        return self.values if hasattr(self, 'values') else None


    # Validate inputs, assemble GestureUpdater dataclass and submit tab result.
    def finish(self) -> None:
        name = self.gesture_file.text()
        error = check_empty_string(name, "Gesture Name: Missing title.")
        if error:
            return None

        random_state = check_string_numeric(
            self.entered_parameters[LABEL_RANDOM_STATE],
            "Random State: Enter integer value in the valid range", int, 0, 4294967295
        )
        if random_state is None: return None

        threshold = check_string_numeric(
            self.entered_parameters[LABEL_THRESHOLD],
            "Threshold: Enter valid integer value.", float
        )
        if threshold is None: return None

        n_component = check_string_numeric(
            self.entered_parameters[LABEL_N_COMPONENT],
            "n Component: Enter valid integer value.", int, 1
        )
        if not n_component: return None

        repeats = check_string_numeric(
            self.entered_parameters["repeats"],
            "Repeats: Enter valid integer value.", int, 1
        )
        if not repeats: return None

        source_matches: Optional[Tuple[int,...]] = self.source_matches()
        if source_matches is None: return None

        self.values = GestureUpdater(
            file=GestureInput(
                name=name,
                repeats=repeats,
                sensors=source_matches,
                parameters=ModelParameters(random_state, n_component, threshold)
            ),
            data=self.gesture_data.models
        )

        self.submit(TAB2)

    #- Key Events ----------------------------------------------------------------------------------

    # Map keyboard events to dialog interactions (enter/escape).
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.continue_button.click()
        elif event.key() == Qt.Key_Escape:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)

