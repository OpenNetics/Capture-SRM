
# layout/record_inputs.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QHBoxLayout, QVBoxLayout,
)

from utils.ui import create_button
from utils.style import (
    BACKGROUND_COLOR, FONT_COLOR,
)
from utils.typedefs import (
    RECORD_ACTION_STOP,
    RECORD_ACTION_START,
    RECORD_ACTION_DISCARD,
    RECORD_ACTION_RESTART,
    RECORD_ACTION_TERMINATE
)

#- Window Class ------------------------------------------------------------------------------------

class RecordInputs(QDialog):

    def __init__(self, total_recordings: int, record_function: Callable[[int], None]) -> None:
        super().__init__()
        self.setWindowTitle("Record Gestures")
        self.setFixedSize(300, 150)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        self.layout = QVBoxLayout(self)

        self.total_recordings = total_recordings
        self.call = record_function
        self.recording = False
        self.recording_counter = 1

        # Recording Index
        self.text_label = QLabel(f"Record {total_recordings} gestures")
        self.text_label.setStyleSheet(f"color: {FONT_COLOR}")
        self.layout.addWidget(self.text_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = create_button("Cancel","[esc]" ,self.button_cancel)
        self.start_stop_button = create_button("Start", "[return]", self.button_start_stop)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.start_stop_button)

        self.layout.addLayout(button_layout)


    def button_cancel(self) -> None:
        button_title = self.cancel_button.text()

        if button_title == "Discard":
            self.text_label.setText(
                f"Deleted recording {self.recording_counter-1} of {self.total_recordings}"
            )
            self.recording_counter -= 1
            self.call(RECORD_ACTION_DISCARD)

        elif button_title == "Restart":
            self.call(RECORD_ACTION_RESTART)

        else:
            self.call(RECORD_ACTION_TERMINATE)
            self.reject()


    def button_start_stop(self) -> None:
        if (self.start_stop_button.text() == "Continue"
            and self.recording_counter == self.total_recordings):
            self.accept()

        elif self.recording:
            self.recording = False
            self.cancel_button.setText("Discard Previous")

            if self.recording_counter < self.total_recordings:
                self.start_stop_button.setText("Start")
                self.recording_counter += 1
                self.text_label.setText(
                    f"Record: {self.recording_counter} of {self.total_recordings}")
            else:
                self.start_stop_button.setText("Continue")
                self.text_label.setText(f"Recorded {self.total_recordings} readings")

            self.call(RECORD_ACTION_STOP)

        else:
            self.recording = True
            self.cancel_button.setText("Restart")
            self.start_stop_button.setText("Stop")
            self.text_label.setText(
                f"Recording: {self.recording_counter} of {self.total_recordings}")
            self.call(RECORD_ACTION_START)


    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space, Qt.Key_S]:
            self.start_stop_button.click()
        elif event.key() in [Qt.Key_Escape, Qt.Key_C]:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)

