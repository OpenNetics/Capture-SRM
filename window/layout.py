
# window/layout.py

#- Imports -----------------------------------------------------------------------------------------

from random import randint

import pyqtgraph as pg
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QVBoxLayout, QWidget, QPushButton


#- Defines -----------------------------------------------------------------------------------------

BACKGROUND_COLOR: str = "#101e15"
APPLICATION_NAME: str = "Gesture Tracker v0.0.1"


#- Window Class ------------------------------------------------------------------------------------

def print_message():
    pass

class LiveGraph( QWidget ):

    def __init__( self ) -> None:
        super().__init__()

        self.setWindowTitle( APPLICATION_NAME )
        self.resize( 1200, 600 )
        self.setStyleSheet( f"background-color: {BACKGROUND_COLOR};" )

        self.layout = QVBoxLayout()
        self.setLayout( self.layout )

        self.button = QPushButton( "Toggle All" )
        self.button.clicked.connect( self.button_toggle_recent )
        self.layout.addWidget( self.button )

        # Initialise the plot
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground( BACKGROUND_COLOR )
        self.layout.addWidget( self.plot_widget )

        self.plot_widget.showGrid( x=True, y=True )
        self.plot_widget.setMouseEnabled( True, True )

        self.reading_source = []
        self.counter = [0]
        self.toggle_recent = 0

        self.timer = QTimer()
        self.timer.timeout.connect( self.update_plot )
        self.timer.start(100)

        # Set-up hover label
        self.hover_label = pg.LabelItem()
        self.plot_widget.addItem( self.hover_label )


    def update_plot(self) -> None:
        self.plot_widget.clear()

        for line in self.reading_source:
            sliced_line = pg.PlotDataItem(
                x = self.counter[self.toggle_recent:],
                y = line["reading"][self.toggle_recent:],
                pen = pg.mkPen( color=line["color"], width=2 )
            )

            self.plot_widget.addItem( sliced_line )


    def button_toggle_recent( self ) -> None:
        self.toggle_recent = 0 - 10 - self.toggle_recent
        self.update_plot()


    def new_color( self ) -> ( int, int, int ):
        return ( randint( 0, 255 ), randint( 60, 255 ), randint( 0, 200 ) )


    def add_data( self, values ) -> None:
        if not isinstance(values, list):
            raise ValueError("Input must be an array of values.")

        self.counter.append( self.counter[-1] + 1 )

        # Clear old data and add new lines
        for i, value in enumerate(values):

            if i >= len( self.reading_source ):
                new_line: dict = {
                    "reading": [value] * len( self.counter ),
                    "color": self.new_color(),
                }

                self.reading_source.append(new_line)

            else:
                self.reading_source[i]["reading"].append( value )

        self.update_plot()

