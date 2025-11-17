
# layout/record_inputs.py

#- Imports -----------------------------------------------------------------------------------------

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QDialog,
    QVBoxLayout,
    QHBoxLayout
)

# from .helper import spaced_element
from .style import (
    BACKGROUND_COLOR,
    FONT_COLOR,
    RECORD_ACTION_STOP,
    RECORD_ACTION_START,
    RECORD_ACTION_DISCARD,
    RECORD_ACTION_RESTART,
    RECORD_ACTION_TERMINATE
)


#- Window Class ------------------------------------------------------------------------------------

class RecordInputs(QDialog):

    from .helper import create_button

    def __init__(self, total_recordings, record_function) -> None:
        super().__init__()
        self.setWindowTitle("Record Gestures")
        self.setFixedSize(250, 150)
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

        self.cancel_button = self.create_button("Cancel", self.button_cancel)
        self.start_stop_button = self.create_button("Start", self.button_start_stop)

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
        if self.start_stop_button.text() == "Continue":
            self.accept()

        elif self.recording:
            self.recording = False
            self.cancel_button.setText("Discard")
            self.start_stop_button.setText(
                "Start" if self.recording_counter < self.total_recordings else "Continue"
            )
            self.text_label.setText(f"Recorded: {self.recording_counter} of {self.total_recordings}")
            self.recording_counter += 1
            self.call(RECORD_ACTION_STOP)

        else:
            self.recording = True
            self.cancel_button.setText("Restart")
            self.start_stop_button.setText("Stop")
            self.text_label.setText(f"Recording: {self.recording_counter} of {self.total_recordings}")
            self.call(RECORD_ACTION_START)


    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.start_stop_button.click()
        elif event.key() == Qt.Key_Escape:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)

