
# window/record_dialog.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List, Union, Tuple

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QDialog,
    QLineEdit,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout
)

from .style import (
    BACKGROUND_COLOR,
    FONT_COLOR,
)
from .helper import alert_box


#- Window Class ------------------------------------------------------------------------------------

class RecordDialog( QDialog ):

    from .helper import create_button

    def __init__( self, total_inputs: int ) -> None:
        super().__init__()

        self.setWindowTitle( "Record Gestures" )
        self.setFixedWidth( 250 )
        self.resize( 250, 200 )
        self.setStyleSheet( f"background-color: {BACKGROUND_COLOR};" )

        self.layout = QVBoxLayout(self)
        self.setLayout( self.layout )

        self.init_input_fields()
        self.init_checkboxes( total_inputs )
        self.init_buttons()


    def init_input_fields( self ) -> None:
        # Gesture Name
        self.gesture_name_input = QLineEdit( self )
        self.gesture_name_input.setPlaceholderText( "Gesture Name" )
        self.layout.addWidget( self.gesture_name_input )

        # Repeats
        self.repeats_input = QLineEdit( self )
        self.repeats_input.setPlaceholderText( "Repeats (integer )")
        self.layout.addWidget( self.repeats_input )


    def init_checkboxes( self, total_inputs ) -> None:
        # Sensor Select Checkboxes
        text_label = QLabel( "Select Sensors" )
        text_label.setStyleSheet( f"color: {FONT_COLOR}" )
        self.layout.addWidget( text_label )

        self.sensor_checkboxes = []
        for i in range( 0, total_inputs ):
            checkbox = QCheckBox( f"index {i+1}", self )
            self.sensor_checkboxes.append( checkbox )
            self.layout.addWidget( checkbox )


    def init_buttons( self ) -> None:
        button_layout = QHBoxLayout()

        self.cancel_button = self.create_button( "Cancel", self.reject  )
        self.continue_button = self.create_button("Continue", self.accept )

        button_layout.addWidget( self.cancel_button )
        button_layout.addWidget( self.continue_button )

        self.layout.addLayout( button_layout )


    def get_inputs(self) -> Union[bool, Tuple[str, int, List[int]]]:
        gesture_name = self.gesture_name_input.text()
        if gesture_name == "":
            alert_box( self, "Error", "Missing gesture name." )
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
                int(checkbox.text().split()[-1]) - 1
                for checkbox in self.sensor_checkboxes
                if checkbox.isChecked()
            ]
            if len( selected_sensors ) < 1:
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

