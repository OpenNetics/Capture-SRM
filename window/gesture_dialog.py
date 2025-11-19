
# window/gesture_dialog.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Union, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QDialog,
    QWidget,
    QLineEdit,
    QCheckBox,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
)

from .helper import (
    blank_line,
    create_button,
    labelled_text_widget,
)
from .style import (
    BACKGROUND_COLOR,
    TEXT_HEAD
)
from .checks import (
    check_empty_string,
    check_string_numeric,
    check_checkboxes_ticked
)


#- Window Class ------------------------------------------------------------------------------------

class GestureDialog(QDialog):

    def __init__(self, input_names: List[str]) -> None:
        super().__init__()

        self.setWindowTitle("Record Gestures")
        self.resize(450, 200)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        self.layout = QVBoxLayout(self)
        tab_widget = QTabWidget(self)
        tab_widget.setStyleSheet("QTabWidget::pane { border: none; }")

        # Record Tab
        tab1 = QWidget()
        tab_widget.addTab(tab1, "Record")
        self.tab1_layout = QVBoxLayout()
        self.init_tab1_input_fields()
        self.init_tab1_checkboxes(input_names)
        self.init_tab1_model_params()
        self.init_tab1_buttons()
        tab1.setLayout(self.tab1_layout)

        # Update Tab
        tab2 = QWidget()
        tab_widget.addTab(tab2, "Update")
        self.tab2_layout = QVBoxLayout()
        tab2.setLayout(self.tab2_layout)

        self.layout.addWidget(tab_widget)

    #- Tab 1 --------------------------------------------------------------------------------------

    def init_tab1_input_fields(self) -> None:
        # Gesture Name
        self.gesture_name_input = QLineEdit(self)
        self.gesture_name_input.setPlaceholderText("Gesture Name")
        self.tab1_layout.addWidget(self.gesture_name_input)

        # Repeats
        self.repeats_input = QLineEdit(self)
        self.repeats_input.setPlaceholderText("Repeats (integer)")
        self.tab1_layout.addWidget(self.repeats_input)


    def init_tab1_checkboxes(self, input_names: List[str]) -> None:
        blank_line(self.tab1_layout)

        text_label = QLabel("Select Sensors")
        text_label.setStyleSheet(TEXT_HEAD)
        self.tab1_layout.addWidget(text_label)

        # Sensor Select Checkboxes
        self.sensor_checkboxes = []
        for name in input_names:
            checkbox = QCheckBox(name, self)
            self.sensor_checkboxes.append(checkbox)
            self.tab1_layout.addWidget(checkbox)


    def init_tab1_model_params(self) -> None:
        blank_line(self.tab1_layout)

        text_label = QLabel("Model Parameters")
        text_label.setStyleSheet(TEXT_HEAD)
        self.tab1_layout.addWidget(text_label)

        self.random_state_label = labelled_text_widget(
            "Random State", "42", "integer in the range [0, 4294967295]", self.tab1_layout)

        self.n_component_label = labelled_text_widget(
            "n Component", "2", "positive integer", self.tab1_layout)

        self.threshold_label = labelled_text_widget(
            "Threshold", "-10", "", self.tab1_layout)


    def init_tab1_buttons(self) -> None:
        blank_line(self.tab1_layout)
        button_layout = QHBoxLayout()

        self.cancel_button = create_button("Cancel", self.reject )
        self.continue_button = create_button("Continue", self.accept)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.continue_button)

        self.tab1_layout.addLayout(button_layout)

    #- Tab 2 --------------------------------------------------------------------------------------

    #- General ------------------------------------------------------------------------------------

    def get_inputs(self) -> Union[bool, Tuple[str, int, List[int], List[float]]]:
        error = check_empty_string( self.gesture_name_input.text(), "Gesture Name: Missing title.")
        if error:
            return False

        success, repeats = check_string_numeric(
            self.repeats_input, "Repeat Count: Enter valid integer.", int, 1)
        if not success:
            return False

        success, selected_sensors = check_checkboxes_ticked(
            self.sensor_checkboxes, 1, "Sources: Select sources to record.")
        if not success:
            return False

        success, random_state = check_string_numeric(
            self.random_state_label,
            "Random State: Enter integer value in the valid range", int, 0, 4294967295)
        if not success:
            return False

        success, threshold = check_string_numeric(
            self.threshold_label, "Threshold: Enter valid integer value.", float)
        if not success:
            return False

        success, n_component = check_string_numeric(
            self.n_component_label, "n Component: Enter valid integer value.", int, 1)
        if not success:
            return False

        return (
            self.gesture_name_input.text(), repeats, selected_sensors,
            [random_state, n_component, threshold]
        )


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.continue_button.click()
        elif event.key() == Qt.Key_Escape:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)

