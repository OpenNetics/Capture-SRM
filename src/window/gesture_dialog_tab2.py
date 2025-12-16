
# window/gesture_dialog_tab2.py

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
    LabelledText,
)

from .checks import check_string_numeric


#- Local Defines -----------------------------------------------------------------------------------

@dataclass
class ReadModelData:
    dropbox: QComboBox
    threshold: LabelledText
    n_components: LabelledText
    random_state: LabelledText
    whitespace: QLabel

DROPBOX_UNCHANGED: str = "<UNCHANGED>"


#- Tab Class ---------------------------------------------------------------------------------------

# Tab responsible for collecting inputs needed to update existing gesture.
class Tab2:

    # Initialise fields, sensor list, model parameter inputs and action buttons.
    def __init__(
            self,
            parent: QDialog,
            parent_layout: QWidget,
            input_names: tuple[str, ...],
            submit: Callable[[Tab], None],
            cancel: Callable[[], None],
        ) -> None:

        #========================================
        # class vars with their init values
        #========================================
        self._parent = parent
        self._submit = submit
        self._cancel = cancel
        self._input_names = input_names

        #========================================
        # master Layout
        #========================================
        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self._layout)

        #========================================
        # scroll area
        #========================================
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.NoFrame)
        scroll_area.setMinimumHeight(SCROLL_HEIGHT)
        scroll_area.setStyleSheet(SCROLL_BAR_STYLE)

        label_frame = QFrame(scroll_area)
        self._body_layout = QVBoxLayout(label_frame) # layout for dynamic content
        scroll_area.setWidget(label_frame)

        #========================================
        # initialise the system
        #========================================
        self._init_filename() # add file selection on main layout
        self._layout.addWidget(scroll_area)
        self._init_buttons()  # add buttons on main layout


    #- Private: init modules -----------------------------------------------------------------------

    # Add widgets to find select gesture files. Add load button to call function to load file data.
    def _init_filename(self) -> None:
        #========================================
        # gesture file name (/path)
        #========================================
        file_name_layout = QHBoxLayout()

        # text box for manual path
        self._gesture_file: QLineEdit = QLineEdit(self._parent)
        self._gesture_file.setPlaceholderText("Gesture Path")
        self._gesture_file.setStyleSheet(TEXT_BOX_STYLE)
        self._gesture_file.setToolTip("File to further update.")
        self._gesture_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_name_layout.addWidget(self._gesture_file, 1)

        # browse button to select path interactively using OS's file manager
        browse_button = create_button(
            "Browse", "File to further update.", self._init_input_filepath)

        browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_name_layout.addWidget(browse_button, 0)

        self._layout.addLayout(file_name_layout)

        #========================================
        # button to load the file and read its content
        #========================================
        load_data = create_button("Load File Data", "", self._dynamic_source_list)
        self._layout.addWidget(load_data)


    # Browse button action: open file dialog to choose target gesture file.
    def _init_input_filepath(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self._parent, "Open Gesture File", "", "Gesture Files (*.ges);;All Files (*)",
            options=QFileDialog.Options()
        )
        if not file_path: return

        # add selected file path as file text box label
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
        #========================================
        # read the file
        #========================================
        self._gesture_data = GestureFile(self._gesture_file.text())

        if not self._gesture_data.read():
            alert_box("Error", f"Invalid filename: {self._gesture_file.text()}")
            # do not continue further if the file selected was not valid
            return

        #========================================
        # clear previous body layout
        #========================================
        # the namme of the file currently loaded
        self._selected_file = self._gesture_file.text()

        # clear existing content in the layout
        clear_layout(self._body_layout)

        # ask for repeats for performing the gesture
        self._repeats = LabelledText("Repeats", "", "Positive Integer", self._body_layout)

        #========================================
        # draw file content
        #========================================
        blank_line(self._body_layout)
        label = QLabel("Available Sources:")
        label.setStyleSheet(LABEL_HEAD_STYLE)
        self._body_layout.addWidget(label)

        self._drop_boxes: dict[str, ReadModelData] = {}
        read_data = self._gesture_data.get_gesture_data()

        for model_name in read_data.keys():
            label_holder: QHBoxLayout = QHBoxLayout()
            params_holder: QHBoxLayout = QHBoxLayout()

            # sensor name from the file
            text_label = QLabel(model_name)
            text_label.setStyleSheet(LABEL_BODY_STYLE)
            text_label.setFixedWidth(100)
            label_holder.addWidget(text_label)

            # list of sensors connected to the device
            input_name_list = QComboBox()
            input_name_list.addItems([DROPBOX_UNCHANGED] + list(self._input_names))
            input_name_list.setStyleSheet(COMBOBOX_STYLE)
            input_name_list.currentTextChanged.connect(
                lambda state, model=model_name: self._source_selected(state, model)
            )
            label_holder.addWidget(input_name_list)

            # space under the parameter list
            space_label = QLabel("")
            space_label.setVisible(False)
            space_label.setFixedHeight(20)

            # parameters from the file
            self._drop_boxes[model_name] = ReadModelData(
                dropbox = input_name_list,

                threshold = LabelledText(
                    LABEL_THRESHOLD, str(read_data[model_name].threshold),
                    "", params_holder, visible=False
                ),

                random_state = LabelledText(
                    LABEL_RANDOM_STATE, str(read_data[model_name].random_state),
                    "integer in the range [0, 4294967295]", params_holder, visible=False
                ),

                n_components = LabelledText(
                    LABEL_N_COMPONENTS, str(read_data[model_name].n_components),
                    "positive integer", params_holder, visible=False
                ),

                whitespace = space_label
            )

            self._body_layout.addLayout(label_holder)
            self._body_layout.addLayout(params_holder)
            self._body_layout.addWidget(space_label)
        spacedv(self._body_layout)


    #- Private: actions ----------------------------------------------------------------------------

    def _source_selected(self, text: str, label: str) -> None:
        visible = text != DROPBOX_UNCHANGED

        self._drop_boxes[label].threshold.visibility(visible)
        self._drop_boxes[label].n_components.visibility(visible)
        self._drop_boxes[label].random_state.visibility(visible)
        self._drop_boxes[label].whitespace.setVisible(visible)


    # Validate inputs, assemble GestureInput dataclass and submit tab result.
    def _finish(self) -> None:
        #========================================
        # ensure gesture filename is valid path
        #========================================
        if not hasattr(self, '_selected_file'): return None

        #========================================
        # ensure repeates count is a valid integer
        #========================================
        repeats = check_string_numeric(
            self._repeats.text(), "Repeat Count: Enter valid integer.", int, 1
        )
        if not repeats: return None

        #========================================
        # checked checkboxes and their values
        #========================================
        file_sources: list[str] = []
        source_ids: list[int] = []
        params: list[ModelParameters] = []

        # Break if any model parameter value isn't valid
        for label in self._drop_boxes.keys():
            index: int = self._drop_boxes[label].dropbox.currentIndex()

            # only check values if the checkbox is selected
            if index == 0: continue # index 0 is DROPBOX_UNCHANGED

            random_state = check_string_numeric(
                self._drop_boxes[label].random_state.text(),
                f"[{label}] Random State: Enter integer value in the valid range",
                int, 0, 4294967295
            )
            if random_state is None: return None

            threshold = check_string_numeric(
                self._drop_boxes[label].threshold.text(),
                f"[{label}] Threshold: Enter valid integer value.", float
            )
            if threshold is None: return None

            n_components = check_string_numeric(
                self._drop_boxes[label].n_components.text(),
                f"[{label}] n Component: Enter valid integer value.", int, 1
            )
            if n_components is None: return None

            # add to the dictionary with the index of the sensor/source as key
            file_sources.append(label)
            source_ids.append(index-1) # -1 because extra DROPBOX_UNCHANGED was added at start
            params.append(ModelParameters(threshold, random_state, n_components))

        #========================================
        # return type, self._values, generated when all values are valid
        #========================================
        self._values = GestureInput(
            filename = self._selected_file,
            repeats  = repeats,
            source_ids = tuple(source_ids),
            parameters = tuple(params),
            file_sources = tuple(file_sources),
        )

        self._submit(Tab.UPDATE)


    #- Public Calls --------------------------------------------------------------------------------

    # Return assembled GestureUpdater values if finish() previously validated them.
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

