
# window/layout.py

#- Imports -----------------------------------------------------------------------------------------

from random import randint

import pyqtgraph as pg
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSizePolicy, QSpacerItem
from PySide6.QtCore import QSize



#- Defines -----------------------------------------------------------------------------------------

BACKGROUND_COLOR: str = "#101e15"
APPLICATION_NAME: str = "Gesture Tracker v0.0.1"

BUTTON_STYLE: str = """
    QPushButton {
        background-color: #112719;
        border: 2px solid #0b1e14;
        border-radius: 5px;
        padding: 5% 10%;
        color: #7d8b94;
    }
    QPushButton:pressed {
        background-color: black;
    }
"""

#- Window Class ------------------------------------------------------------------------------------

def new_color() -> ( int, int, int ):
    return ( randint( 0, 255 ), randint( 60, 255 ), randint( 0, 200 ) )


class LiveGraph( QWidget ):

    def __init__( self ) -> None:
        super().__init__()

        self.setWindowTitle( APPLICATION_NAME )
        self.resize( 1200, 600 )
        self.setStyleSheet( f"background-color: {BACKGROUND_COLOR};" )

        self.layout = QVBoxLayout()
        self.setLayout( self.layout )


        #- Buttons -------------------------------------------------------------

        button_layout = QHBoxLayout()

        self.SaveButton = QPushButton( "Save" )
        self.SaveButton.clicked.connect( self.button_save )
        self.SaveButton.setStyleSheet( BUTTON_STYLE )
        button_layout.addWidget( self.SaveButton )

        self.RecordButton = QPushButton( "Record (Start)" )
        self.RecordButton.clicked.connect( self.button_record )
        self.RecordButton.setStyleSheet( BUTTON_STYLE )
        button_layout.addWidget( self.RecordButton )

        button_layout.addItem(
            QSpacerItem( 20, 20, QSizePolicy.Expanding, QSizePolicy.Preferred )
        )

        self.DataViewButton = QPushButton( "View Toggle" )
        self.DataViewButton.clicked.connect( self.button_toggle_recent )
        self.DataViewButton.setStyleSheet( BUTTON_STYLE )
        button_layout.addWidget( self.DataViewButton )

        self.FreezeButton = QPushButton( "Freeze" )
        self.FreezeButton.clicked.connect( self.button_freeze )
        self.FreezeButton.setStyleSheet( BUTTON_STYLE )
        button_layout.addWidget( self.FreezeButton )

        self.ClearButton = QPushButton( " Clear " )
        self.ClearButton.clicked.connect( self.button_clear_data )
        self.ClearButton.setStyleSheet( BUTTON_STYLE )
        button_layout.addWidget( self.ClearButton )

        self.layout.addLayout( button_layout )


        #- Graph Plot ----------------------------------------------------------

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground( BACKGROUND_COLOR )
        self.layout.addWidget( self.plot_widget )

        self.plot_widget.showGrid( x=True, y=True )
        self.plot_widget.setMouseEnabled( True, True )

        self.reading_source = []
        self.counter = [0]
        self.toggle_recent = 0
        self.freeze = False

        # Legend
        self.legend_layout = QHBoxLayout()
        self.layout.addLayout( self.legend_layout )

        self.legend_layout.addItem(
            QSpacerItem( 20, 20, QSizePolicy.Expanding, QSizePolicy.Preferred )
        )


        #- Raw Values ----------------------------------------------------------



    def update_plot( self ) -> None:
        if self.freeze:
            return

        self.plot_widget.clear()

        for line in self.reading_source:
            sliced_line = pg.PlotDataItem(
                x = self.counter[self.toggle_recent:],
                y = line["reading"][self.toggle_recent:],
                pen = pg.mkPen( color=line["color"], width=2 ),
                name = line["name"]
            )

            self.plot_widget.addItem( sliced_line )


    def add_data( self, values ) -> None:
        if not isinstance(values, list):
            raise ValueError("Input must be an array of values.")

        self.counter.append( self.counter[-1] + 1 )

        # Clear old data and add new lines
        for i, value in enumerate(values):

            if i >= len( self.reading_source ):
                colors: ( int, int, int ) = new_color()

                new_line: dict = {
                    "reading": [value] * len( self.counter ),
                    "color": colors,
                    "name": f"source{i}"
                }

                self.reading_source.append( new_line )

                # Draw legend
                square = QLabel()
                square.setFixedSize( QSize(20, 20) )
                square.setStyleSheet(
                    f"background-color: rgb({colors[0]}, {colors[1]}, {colors[2]});"
                )

                text_label = QLabel( f"source {i+1}" )

                h_layout = QHBoxLayout()
                h_layout.addWidget(square)
                h_layout.addWidget(text_label)

                self.legend_layout.addLayout( h_layout )

            else:
                self.reading_source[i]["reading"].append( value )

        self.update_plot()


    def button_toggle_recent( self ) -> None:
        view_button_options = [ "View Latest", "View All" ]
        self.toggle_recent = 0 - 10 - self.toggle_recent
        self.DataViewButton.setText( view_button_options[self.toggle_recent % 11] )
        self.update_plot()


    def button_clear_data( self ) -> None:
        self.reading_source = []
        self.counter = [0]
        self.toggle_recent = 0
        self.update_plot()


    def button_freeze( self ) -> None:
        self.freeze = not self.freeze
        self.FreezeButton.setText("Unfreeze" if self.freeze else "Freeze")
        self.update_plot()


    def button_save( self ) -> None:
        pass


    def button_record( self ) -> None:
        current_text = self.RecordButton.text()
        new_text = "Record (Stop)" if current_text == "Record (Start)" else "Record (Start)"
        self.RecordButton.setText(new_text)

