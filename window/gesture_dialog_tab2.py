
# window/gesture_dialog_tab2.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Callable, List, Optional, Union, Tuple

from redwrenlib import GestureFile
from redwrenlib.typing import ModelParameters
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget,
    QComboBox, QFileDialog, QLabel, QLineEdit,
    QLayout, QVBoxLayout, QHBoxLayout,
    QSizePolicy,
)

from utils.ui import alert_box
from utils.style import (
    TEXT_HEAD, TEXT_BODY,
    COMBOBOX_STYLE,
)
from utils.typing import(
    TAB2,
    LABEL_RANDOM_STATE, LABEL_N_COMPONENTS, LABEL_THRESHOLD,
    GestureInput, GestureUpdater
)
from utils.ui import (
    spacedv, blank_line,
    create_button, labelled_text_widget,
)

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
            submit: Callable[[int], None],
            cancel: Callable[[], None],
        ) -> None:

        self._parent: QDialog = parent
        self._submit: Callable[[int], None] = submit
        self._cancel: Callable[[], None] = cancel
        self._input_names: List[str] = input_names

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self._layout)

        self._init_filename() # add file selection on main layout

        self._body_layout = QVBoxLayout() # layout for dynamic content
        self._layout.addLayout(self._body_layout)

        self._init_buttons()  # add buttons on main layout

    #- Private: init modules -----------------------------------------------------------------------

    # Add widgets to find select gesture files. Add load button to call function to load file data.
    def _init_filename(self) -> None:
        # Gesture Name
        file_name_layout = QHBoxLayout()

        self._gesture_file: QLineEdit = QLineEdit(self._parent)
        self._gesture_file.setPlaceholderText("Gesture Path")
        self._gesture_file.setToolTip("File to further update.")
        self._gesture_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_name_layout.addWidget(self._gesture_file, 1)

        browse_button = create_button("Browse", "File to further update.", self._init_input_filepath)
        browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_name_layout.addWidget(browse_button, 0)

        self._layout.addLayout(file_name_layout)

        load_data = create_button("Load File Data", "", self._dynamic_source_list)
        self._layout.addWidget(load_data)


    # Browse button action: open file dialog to choose target gesture file.
    def _init_input_filepath(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self._parent, "Open Gesture File", "", "Gesture Files (*.ges);;All Files (*)",
            options=QFileDialog.Options()
        )
        if not file_path: return

        self._gesture_file.setText(file_path)


    # Create Cancel / Continue buttons and wire them to actions.
    def _init_buttons(self) -> None:
        blank_line(self._layout)
        spacedv(self._layout)
        button_layout = QHBoxLayout()

        self._cancel_button = create_button("Cancel", "[esc]", self._cancel)
        self._continue_button = create_button("Continue", "[return]", self._finish)

        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._continue_button)

        self._layout.addLayout(button_layout)

    #- Private: dynamically generated modules ------------------------------------------------------

    # Read file data and add dynamic widgets to body layout, with data from gesture file.
    def _dynamic_source_list(self) -> None:
        self._gesture_data = GestureFile(self._gesture_file.text())
        if not self._gesture_data.read():
            alert_box("Error", f"Invalid filename: {self._gesture_file.text()}")
            return

        self.__selected_file = self._gesture_file.text()

        # clear previous body layout
        while self._body_layout.count():
            item: QLayout = self._body_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        blank_line(self._body_layout)
        label = QLabel("Available Sources:")
        label.setStyleSheet(TEXT_HEAD)
        self._body_layout.addWidget(label)

        self._drop_boxes: List[QComboBox] = []

        for model in self._gesture_data.get_models().keys():
            label_holder: QHBoxLayout = QHBoxLayout()

            text_label = QLabel(model)
            text_label.setStyleSheet(TEXT_BODY)
            text_label.setFixedWidth(100)
            label_holder.addWidget(text_label)

            input_name_list = QComboBox()
            input_name_list.addItems(["<UNCHANGED>"] + self._input_names)
            input_name_list.setStyleSheet(COMBOBOX_STYLE)
            self._drop_boxes.append(input_name_list)
            label_holder.addWidget(input_name_list)

            self._body_layout.addLayout(label_holder)

        self._dynamic_data_usage()


    # Use the read data to autofill model parameters. Allow editing them for future training.
    def _dynamic_data_usage(self) -> None:
        blank_line(self._body_layout)
        label = QLabel("New Training Model Parameters:")
        label.setStyleSheet(TEXT_HEAD)
        self._body_layout.addWidget(label)

        self._entered_parameters: dict[str,QLineEdit] = {}
        blank_line(self._body_layout)
        def _show_saved_values(label: str, value: Union[int, float, None]) -> None:
            text_label = str(value) if value is not None else "None Saved"
            text_widget = labelled_text_widget(label, text_label, text_label, self._body_layout)
            self._entered_parameters[label] = (text_widget)

        parameters: ModelParameters = self._gesture_data.get_parameters()
        _show_saved_values(LABEL_RANDOM_STATE, parameters.random_state)
        _show_saved_values(LABEL_N_COMPONENTS, parameters.n_components)
        _show_saved_values(LABEL_THRESHOLD, parameters.threshold)

        repeats_widget = labelled_text_widget("Repeats", "", "Positive Integer", self._body_layout)
        repeats_widget.setToolTip("Number of times to repeat the gesture recording.")
        self._entered_parameters["repeats"] = (repeats_widget)

        spacedv(self._body_layout)

    #- Private: actions ----------------------------------------------------------------------------

    # Return tuple of source matches
    def _source_matches(self) -> Optional[Tuple[int, ...]]:
        #TODO: alert-box when None
        return (1,2,3)


    # Validate inputs, assemble GestureUpdater dataclass and submit tab result.
    def _finish(self) -> None:
        if not hasattr(self, '_entered_parameters'): return None

        error = check_empty_string(self.__selected_file, "Gesture Name: Missing title.")
        if error: return None

        random_state = check_string_numeric(
            self._entered_parameters[LABEL_RANDOM_STATE],
            "Random State: Enter integer value in the valid range", int, 0, 4294967295
        )
        if random_state is None: return None

        threshold = check_string_numeric(
            self._entered_parameters[LABEL_THRESHOLD],
            "Threshold: Enter valid integer value.", float
        )
        if threshold is None: return None

        n_components = check_string_numeric(
            self._entered_parameters[LABEL_N_COMPONENTS],
            "n Component: Enter valid integer value.", int, 1
        )
        if not n_components: return None

        repeats = check_string_numeric(
            self._entered_parameters["repeats"],
            "Repeats: Enter valid integer value.", int, 1
        )
        if not repeats: return None

        source_matches: Optional[Tuple[int,...]] = self._source_matches()
        if source_matches is None: return None

        self._values = GestureUpdater(
            file=GestureInput(
                name=self.__selected_file,
                repeats=repeats,
                sensors=source_matches,
                parameters=ModelParameters(random_state, n_components, threshold)
            ),
            data=self._gesture_data.get_models()
        )

        self._submit(TAB2)

    #- Public Calls --------------------------------------------------------------------------------

    # Return assembled GestureUpdater values if finish() previously validated them.
    def get_inputs(self) -> Optional[GestureUpdater]:
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

