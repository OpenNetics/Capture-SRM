
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
    alert_box,
    blank_line,
    create_button,
    labelled_text_widget,
)
from .style import (
    BACKGROUND_COLOR,
    TEXT_HEAD
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

        self.random_state_label = labelled_text_widget("Random State", "42", self.tab1_layout)
        self.n_component_label = labelled_text_widget("n Component", "2", self.tab1_layout)
        self.threshold_label = labelled_text_widget("Threshold", "-10", self.tab1_layout)


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

    def get_inputs(self) -> Union[ bool, Tuple[str, int, List[int], List[float]] ]:
        gesture_name = self.gesture_name_input.text()
        if gesture_name == "":
            alert_box(self, "Error", "Gesture Name: Missing title.")
            return False

        try:
            repeats = int(self.repeats_input.text())
            if repeats < 1:
                raise ValueError
        except ValueError:
            alert_box(self, "Error", "Repeat Count: Enter valid integer.")
            return False

        try:
            selected_sensors = [
                index
                for index, checkbox in enumerate(self.sensor_checkboxes)
                if checkbox.isChecked()
            ]

            if len(selected_sensors) < 1:
                raise ValueError
        except ValueError:
            alert_box(self, "Error", "Sources: Select sources to record.")
            return False

        try:
            random_state = float( self.random_state_label.text() )
        except ValueError:
            alert_box(self, "Error", "Random State: Enter valid integer value.")
            return False

        try:
            threshold = float( self.threshold_label.text() )
        except ValueError:
            alert_box(self, "Error", "Threshold: Enter valid integer value.")
            return False

        try:
            n_component = float( self.n_component_label.text() )
        except ValueError:
            alert_box(self, "Error", "n Component: Enter valid integer value.")
            return False

        return gesture_name, repeats, selected_sensors, [random_state, n_component, threshold]


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.continue_button.click()
        elif event.key() == Qt.Key_Escape:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)

