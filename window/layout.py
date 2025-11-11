
# window/layout.py

#- Imports -----------------------------------------------------------------------------------------

import pyqtgraph as pg
from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QDialog,
    QTextEdit,
    QComboBox,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QMessageBox
)

from utils import connected_ports, baud_rates
from .helper import (
    new_color,
    spaced_element
)
from .style import (
    BACKGROUND_COLOR,
    FONT_COLOR,
    APPLICATION_NAME,
    WINDOW_SIZE,
    GRAPH_HEIGHT,
    RAW_VALUE_BOX_STYLE,
    COMBOBOX_STYLE
)
from .record_gesture import InputDialog


#- Window Class ------------------------------------------------------------------------------------

class LiveGraph( QWidget ):

    from .helper import create_button

    def __init__( self ) -> None:
        super().__init__()

        self.setWindowTitle( APPLICATION_NAME )
        self.resize( WINDOW_SIZE["width"], WINDOW_SIZE["height"] )
        self.setStyleSheet( f"background-color: {BACKGROUND_COLOR};" )

        self.layout = QVBoxLayout()
        self.setLayout( self.layout )


        #- Variables -----------------------------------------------------------

        self.reading_source = []
        self.counter = [0]
        self.toggle_recent = 0
        self.freeze = False


        #- Buttons -------------------------------------------------------------

        button_layout = QHBoxLayout()

        self.RecordButton = self.create_button("Record (Start)", self.button_record)
        self.SaveButton = self.create_button("Save", self.button_save)
        self.DataViewButton = self.create_button("Zoom Latest", self.button_toggle_recent)
        self.FreezeButton = self.create_button("Freeze", self.button_freeze)
        self.ClearButton = self.create_button("Clear", self.button_clear_data)

        button_layout.addWidget( self.RecordButton )
        button_layout.addWidget( self.SaveButton )
        button_layout.addItem( spaced_element() )
        button_layout.addWidget( self.DataViewButton )
        button_layout.addWidget( self.FreezeButton )
        button_layout.addWidget( self.ClearButton )

        self.layout.addLayout( button_layout )


        #- Graph Plot ----------------------------------------------------------

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground( BACKGROUND_COLOR )
        self.layout.addWidget( self.plot_widget )
        self.plot_widget.setFixedHeight( GRAPH_HEIGHT )

        self.plot_widget.showGrid( x=True, y=True )
        self.plot_widget.setMouseEnabled( True, True )

        # Legend
        self.legend_layout = QHBoxLayout()
        self.layout.addLayout( self.legend_layout )

        self.connection_list = QComboBox()
        self.connection_list.addItems( connected_ports() )
        self.connection_list.setStyleSheet( COMBOBOX_STYLE )
        self.connection_list.currentTextChanged.connect( self.print_selected_item )

        ConnectionsRefreshButoon = self.create_button( "Refresh", self.button_refresh_connections )

        self.baud_rate_list = QComboBox()
        self.baud_rate_list.addItems( baud_rates() )
        self.baud_rate_list.setStyleSheet( COMBOBOX_STYLE )
        self.baud_rate_list.currentTextChanged.connect( self.print_selected_item )

        self.legend_layout.addWidget( ConnectionsRefreshButoon )
        self.legend_layout.addWidget( self.connection_list )
        self.legend_layout.addWidget( self.baud_rate_list )
        self.legend_layout.addItem( spaced_element() )


        #- Raw Values ----------------------------------------------------------

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable( True )

        self.scroll_area_content = QWidget()
        self.scroll_area_layout = QVBoxLayout( self.scroll_area_content )

        self.data_display = QTextEdit()
        self.data_display.setStyleSheet( RAW_VALUE_BOX_STYLE )
        self.data_display.setReadOnly( True )

        self.scroll_area_layout.addWidget( self.data_display )
        self.scroll_area.setWidget( self.scroll_area_content )

        self.layout.addWidget( self.scroll_area )


    def update_plot( self ) -> None:
        if self.freeze:
            return

        self.plot_widget.clear()

        for line in self.reading_source:
            sliced_line = pg.PlotDataItem(
                x = self.counter[self.toggle_recent:],
                y = line["reading"][self.toggle_recent:],
                pen = pg.mkPen( color=line["color"], width=2 ),
            )

            self.plot_widget.addItem( sliced_line )


    def add_data( self, values ) -> None:
        if not isinstance(values, list):
            raise ValueError("Input must be an array of values.")

        # add data to the raw data area
        self.data_display.append( str(values) )

        self.counter.append( self.counter[-1] + 1 )

        # Clear old data and add new lines
        for i, value in enumerate(values):

            if i >= len( self.reading_source ):
                colors: ( int, int, int ) = new_color()

                new_line: dict = {
                    "reading": [value] * len( self.counter ),
                    "color": colors,
                }

                self.reading_source.append( new_line )

                # Draw legend
                square = QLabel()
                square.setFixedSize( QSize(20, 20) )
                square.setStyleSheet(
                    f"background-color: rgb({colors[0]}, {colors[1]}, {colors[2]});"
                )

                text_label = QLabel( f"i{i+1}" )
                text_label.setStyleSheet( f"color: {FONT_COLOR}" )

                h_layout = QHBoxLayout()
                h_layout.addWidget(square)
                h_layout.addWidget(text_label)

                self.legend_layout.addLayout( h_layout )

            else:
                self.reading_source[i]["reading"].append( value )

        self.update_plot()


    def button_toggle_recent( self ) -> None:
        view_button_options = [ "Zoom Latest", "View All" ]
        self.toggle_recent = 0 - 10 - self.toggle_recent
        self.DataViewButton.setText( view_button_options[self.toggle_recent % 11] )
        self.update_plot()


    def button_clear_data( self ) -> None:
        self.counter = [0]
        self.toggle_recent = 0

        for line in self.reading_source:
            line["reading"] = [line["reading"][-1]]

        self.data_display.clear()
        self.update_plot()


    def button_freeze( self ) -> None:
        self.freeze = not self.freeze
        self.FreezeButton.setText("Unfreeze" if self.freeze else "Freeze")
        self.update_plot()


    def button_save( self ) -> None:
        # Open file dialog to select save location
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "Text Files (*.txt);;All Files (*)",
            options=options
        )

        if file_path:
            with open( file_path, 'w' ) as file:
                file.write( self.data_display.toPlainText() )

        msg_box = QMessageBox( self )
        msg_box.setIcon( QMessageBox.NoIcon )
        msg_box.setWindowTitle( "Success" )
        msg_box.setText( "File saved successfully!" )
        msg_box.exec_()


    def button_record( self ) -> None:
        current_text = self.RecordButton.text()
        new_text = "Record (Stop)" if current_text == "Record (Start)" else "Record (Start)"
        self.RecordButton.setText( new_text )

        dialog = InputDialog( len(self.reading_source) )
        if dialog.exec() == QDialog.Accepted:
            gesture_name, repeats, selected_sensors = dialog.get_inputs()


    def button_refresh_connections( self ) -> None:
        self.connection_list.clear()
        self.connection_list.addItems( connected_ports() )


    def print_selected_item( self, text: str ) -> None:
        print( f'Selected item: {text}' )

