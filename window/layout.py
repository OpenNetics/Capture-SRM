
# window/layout.py

#- Imports -----------------------------------------------------------------------------------------

from random import randint

import pyqtgraph as pg
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QVBoxLayout, QWidget, QPushButton


#- Defines -----------------------------------------------------------------------------------------

BACKGROUND_COLOUR: str = "#101e15"
APPLICATION_NAME: str = "Gesture Tracker v0.0.1"


#- Window Class ------------------------------------------------------------------------------------

def print_message():
    pass

class LiveGraph( QWidget ):

    def __init__( self ) -> None:
        super().__init__()

        self.setWindowTitle( APPLICATION_NAME )
        self.setStyleSheet( f"background-color: {BACKGROUND_COLOUR};" )

        self.layout = QVBoxLayout()
        self.setLayout( self.layout )

        self.button = QPushButton( "Toggle All" )
        self.button.clicked.connect( print_message )
        self.layout.addWidget( self.button )

        # Initialise the plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground( BACKGROUND_COLOUR )
        self.layout.addWidget( self.plot_widget )

        self.plot_widget.showGrid( x=True, y=True )
        self.plot_widget.setMouseEnabled( True, True )

        self.data_lines = []
        self.x_data = [0]
        self.y_data = []

        self.timer = QTimer()
        self.timer.timeout.connect( self.update_plot )
        self.timer.start(100)

        # Set-up hover label
        self.hover_label = pg.LabelItem()
        self.plot_widget.addItem( self.hover_label )


    def update_plot( self ) -> None:
        self.plot_widget.clear()

        for line in self.data_lines:
            self.plot_widget.addItem(line)


    def new_color( self ) -> ( int, int, int ):
        return ( randint(50, 250), randint(50, 250), randint(50, 250) )


    def add_data( self, values ) -> None:
        if not isinstance(values, list):
            raise ValueError("Input must be an array of values.")

        self.x_data.append( self.x_data[-1] + 1 )

        # Clear old data and add new lines
        for i, value in enumerate(values):

            if i >= len(self.data_lines):
                pen = pg.mkPen( color=self.new_color(), width=2 )
                y_values = [value]*len(self.x_data)

                new_line = pg.PlotDataItem(
                    x=self.x_data,
                    y=y_values,
                    pen=pen,
                    name=f"Value {i+1}"
                )

                self.y_data.append(y_values)
                self.data_lines.append(new_line)

            else:
                self.y_data[i].append(value)
                self.data_lines[i].setData( x=self.x_data, y=self.y_data[i] )

        self.update_plot()

