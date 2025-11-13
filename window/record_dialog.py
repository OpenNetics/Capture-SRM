
# window/record_dialog.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List

from PySide6.QtWidgets import (
    QLabel,
    QDialog,
    QLineEdit,
    QCheckBox,
    QVBoxLayout,
    QHBoxLayout
)

# from .helper import spaced_element

from .style import (
    BACKGROUND_COLOR,
    FONT_COLOR,
)


#- Window Class ------------------------------------------------------------------------------------

class RecordDialog( QDialog ):

    from .helper import create_button

    def __init__( self, total_inputs: int ) -> None:
        super().__init__()
        self.setWindowTitle( "Record Gestures" )
        self.resize( 250, 200 )
        self.setStyleSheet( f"background-color: {BACKGROUND_COLOR};" )

        self.layout = QVBoxLayout(self)

        # Gesture Name
        self.gesture_name_input = QLineEdit( self )
        self.gesture_name_input.setPlaceholderText( "Gesture Name" )
        self.layout.addWidget( self.gesture_name_input )

        # Repeats
        self.repeats_input = QLineEdit( self )
        self.repeats_input.setPlaceholderText( "Repeats (integer )")
        self.layout.addWidget( self.repeats_input )

        # Sensor Select Checkboxes
        text_label = QLabel( "Select Sensors" )
        text_label.setStyleSheet( f"color: {FONT_COLOR}" )
        self.layout.addWidget( text_label )

        self.sensor_checkboxes = []
        for i in range( 0, total_inputs ):
            checkbox = QCheckBox( f"index {i+1}", self )
            self.sensor_checkboxes.append( checkbox )
            self.layout.addWidget( checkbox )


        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = self.create_button( "Cancel", self.reject  )
        self.continue_button = self.create_button("Continue", self.accept )

        button_layout.addWidget( self.cancel_button )
        button_layout.addWidget( self.continue_button )

        self.layout.addLayout( button_layout )


    def get_inputs( self ) -> ( str, int, List ):
        gesture_name = self.gesture_name_input.text()
        repeats = int(self.repeats_input.text())
        selected_sensors = [cb.text() for cb in self.sensor_checkboxes if cb.isChecked()]

        return gesture_name, repeats, selected_sensors


