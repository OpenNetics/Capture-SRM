
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
    QHBoxLayout
)

from .style import (
    BACKGROUND_COLOR,
    FONT_COLOR,
)
from .helper import alert_box


#- Window Class ------------------------------------------------------------------------------------

class GestureDialog(QDialog):

    from .helper import create_button

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
        self.repeats_input.setText("5")
        self.tab1_layout.addWidget(self.repeats_input)


    def init_tab1_checkboxes(self, input_names: List[str]) -> None:
        # Sensor Select Checkboxes
        text_label = QLabel("Select Sensors")
        text_label.setStyleSheet(f"color: {FONT_COLOR}")
        self.tab1_layout.addWidget(text_label)

        self.sensor_checkboxes = []
        for name in input_names:
            checkbox = QCheckBox(name, self)
            self.sensor_checkboxes.append(checkbox)
            self.tab1_layout.addWidget(checkbox)


    def init_tab1_buttons(self) -> None:
        button_layout = QHBoxLayout()

        self.cancel_button = self.create_button("Cancel", self.reject )
        self.continue_button = self.create_button("Continue", self.accept)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.continue_button)

        self.tab1_layout.addLayout(button_layout)

    #- Tab 2 --------------------------------------------------------------------------------------

    #- General ------------------------------------------------------------------------------------

    def get_inputs(self) -> Union[ bool, Tuple[str, int, List[int]] ]:
        gesture_name = self.gesture_name_input.text()
        if gesture_name == "":
            alert_box(self, "Error", "Missing gesture name.")
            return False

        try:
            repeats = int(self.repeats_input.text())
            if repeats < 1:
                raise ValueError
        except ValueError:
            alert_box(self, "Error", "Invalid gesture repeat count.")
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
            alert_box(self, "Error", "Select input indexes to record.")
            return False

        return gesture_name, repeats, selected_sensors


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.continue_button.click()
        elif event.key() == Qt.Key_Escape:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)

