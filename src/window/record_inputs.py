
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

from src.utils.ui import create_button
from src.utils.style import (
    BACKGROUND_COLOR, FONT_COLOR,
)
from src.utils.typing import (
    RECORD_ACTION_STOP,
    RECORD_ACTION_START,
    RECORD_ACTION_DISCARD,
    RECORD_ACTION_RESTART,
    RECORD_ACTION_TERMINATE
)


#- Window Class ------------------------------------------------------------------------------------

# Dialog used to control recording sessions (start/stop/discard/restart).
class RecordInputs(QDialog):

    # Initialise dialog UI and recording state, pass callbacks to record controller.
    def __init__(self, total_recordings: int, record_function: Callable[[int], None]) -> None:
        super().__init__()
        self.setWindowTitle("Record Gestures")
        self.setFixedSize(300, 150)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        self._layout = QVBoxLayout(self)

        self._total_recordings = total_recordings
        self._call = record_function
        self._recording = False
        self._recording_counter = 1

        # Recording Index
        self._text_label = QLabel(f"Record {total_recordings} gestures")
        self._text_label.setStyleSheet(f"color: {FONT_COLOR}")
        self._layout.addWidget(self._text_label)

        # Buttons
        button_layout = QHBoxLayout()

        self._cancel_button = create_button("Cancel","[esc]" ,self._button_cancel)
        self._start_stop_button = create_button("Start", "[return]", self._button_start_stop)

        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._start_stop_button)

        self._layout.addLayout(button_layout)


    # Handle cancel button actions: discard, restart or terminate the whole session.
    def _button_cancel(self) -> None:
        button_title = self._cancel_button.text()

        if button_title == "Discard":
            self._text_label.setText(
                f"Deleted recording {self._recording_counter-1} of {self._total_recordings}"
            )
            self._recording_counter -= 1
            self._call(RECORD_ACTION_DISCARD)

        elif button_title == "Restart":
            self._call(RECORD_ACTION_RESTART)

        else:
            self._call(RECORD_ACTION_TERMINATE)
            self.reject()


    # Toggle recording start/stop and advance or finalize the recording session.
    def _button_start_stop(self) -> None:
        if (self._start_stop_button.text() == "Continue"
            and self._recording_counter == self._total_recordings):
            self.accept()

        elif self._recording:
            self._recording = False
            self._cancel_button.setText("Discard Previous")

            if self._recording_counter < self._total_recordings:
                self._start_stop_button.setText("Start")
                self._recording_counter += 1
                self._text_label.setText(
                    f"Record: {self._recording_counter} of {self._total_recordings}")
            else:
                self._start_stop_button.setText("Continue")
                self._text_label.setText(f"Recorded {self._total_recordings} readings")

            self._call(RECORD_ACTION_STOP)

        else:
            self._recording = True
            self._cancel_button.setText("Restart")
            self._start_stop_button.setText("Stop")
            self._text_label.setText(
                f"Recording: {self._recording_counter} of {self._total_recordings}")
            self._call(RECORD_ACTION_START)

    #- Keyboard Shortcut Override ------------------------------------------------------------------

    # Map keyboard keys to dialog actions for convenience.
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space, Qt.Key_S]:
            self._start_stop_button.click()
        elif event.key() in [Qt.Key_Escape, Qt.Key_C]:
            self._cancel_button.click()
        else:
            super().keyPressEvent(event)

