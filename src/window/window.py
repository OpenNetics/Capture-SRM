
# window/window.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any, Dict, List, Tuple

import pyqtgraph as pg
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget, QFrame,
    QComboBox, QFileDialog, QLabel, QMessageBox, QTextEdit,
    QHBoxLayout, QVBoxLayout, QScrollArea,
)
from redwrenlib.typing import int2d_t

from src.analyse import analyse_create, analyse_update
from src.utils.extra import new_color, datestring
from src.utils.ui import (
    EditLabel,
    spacedh, create_button,
)
from src.utils.style import (
    APPLICATION_NAME,
    BACKGROUND_COLOR,
    WINDOW_SIZE, GRAPH_HEIGHT,
    RAW_VALUE_BOX_STYLE, COMBOBOX_STYLE, SCROLL_BAR_STYLE,
)
from src.utils.typing import (
    SensorValues, ModelParameters,
    sensor_values_t,
    RECORD_ACTION_STOP,
    RECORD_ACTION_START,
    RECORD_ACTION_DISCARD,
    RECORD_ACTION_RESTART,
    RECORD_ACTION_TERMINATE,
    TAB1, TAB2,
)
from src.serial import (
    select_port, select_baud_rate,
    baud_rates, connected_ports
)

from .gesture_dialog import GestureDialog
from .record_inputs import RecordInputs
from .graphline import GraphLine
from .checks import check_sources_name


#- Window Class ------------------------------------------------------------------------------------

# GestureTracker: main application widget that manages UI, plotting and gesture workflows.
class GestureTracker(QWidget):

    # Initialise the main window, state variables and build UI components.
    def __init__(self) -> None:
        super().__init__()

        #========================================
        # window properties
        #========================================
        self.setWindowTitle(APPLICATION_NAME)
        self.resize(WINDOW_SIZE["width"], WINDOW_SIZE["height"])
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        #========================================
        # master Layout
        #========================================
        self._layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self._layout)

        #========================================
        # class vars with their init values
        #========================================
        self._graphlines: List[GraphLine] = []
        self._counter: List[float] = [0]
        self._toggle_recent: int = 0
        self._freeze: bool = False

        #========================================
        # initialise the system
        #========================================
        self._init_buttons()
        self._init_graph_plot()
        self._init_graph_footer()
        self._init_raw_data()


    #- Private: Initialise Components --------------------------------------------------------------

    # Build the top button row and attach callbacks.
    def _init_buttons(self) -> None:
        button_layout = QHBoxLayout()

        #========================================
        # top-left buttons
        #========================================
        self._gesture_button = create_button(
            "Gesture", "Play with gesture files [g]", self._button_gesture)
        button_layout.addWidget(self._gesture_button)

        self._save_button = create_button(
            "Save", "Save read data in text file [s]", self._button_save)
        button_layout.addWidget(self._save_button)

        #========================================
        # whitespace dividing left-right regions
        #========================================
        spacedh(button_layout)

        #========================================
        # top-right buttons
        #========================================
        self._data_view_button = create_button(
            "Zoom Latest", "Plot only latest 10 readings [t]", self._button_toggle_recent)
        button_layout.addWidget(self._data_view_button)

        self._freeze_button = create_button(
            "Freeze", "Toggle freezing live plot [space]", self._button_freeze)
        button_layout.addWidget(self._freeze_button)

        self._clear_button = create_button(
            "Clear", "Clear all read data [esc]", self._button_clear_data)
        button_layout.addWidget(self._clear_button)

        # to the layout
        self._layout.addLayout(button_layout)


    # Create and configure the plot widget used for realtime graphs.
    def _init_graph_plot(self) -> None:
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground(BACKGROUND_COLOR)
        self._layout.addWidget(self._plot_widget)
        self._plot_widget.setFixedHeight(GRAPH_HEIGHT)

        self._plot_widget.showGrid(x=True, y=True)
        self._plot_widget.setMouseEnabled(True, True)


    # Create footer area containing legends and connection/baud selectors.
    def _init_graph_footer(self) -> None:
        self._legend_layout = QHBoxLayout() # graph legends are added to this layout
        self._layout.addLayout(self._legend_layout)

        #========================================
        # port refresh button
        #========================================
        connection_refresh_button = create_button(
            "Refresh", "Reflesh port list", self._button_refresh_connections)
        self._legend_layout.addWidget(connection_refresh_button)

        #========================================
        # port list
        #========================================
        self._connection_list = QComboBox()
        self._connection_list.addItems(["<SELECT>"] + connected_ports())
        self._connection_list.setToolTip("Select Connection Port")
        self._connection_list.setStyleSheet(COMBOBOX_STYLE)
        self._connection_list.currentTextChanged.connect(select_port)
        self._legend_layout.addWidget(self._connection_list)

        #========================================
        # baud rate list
        #========================================
        self._baud_rate_list = QComboBox()
        self._baud_rate_list.addItems(baud_rates())
        self._baud_rate_list.setToolTip("Select Baud Rate")
        self._baud_rate_list.setCurrentText("115200")
        self._baud_rate_list.setStyleSheet(COMBOBOX_STYLE)
        self._baud_rate_list.currentTextChanged.connect(select_baud_rate)
        self._legend_layout.addWidget(self._baud_rate_list)

        spacedh(self._legend_layout)


    # Scrollable raw data text area for incoming sensor values.
    def _init_raw_data(self) -> None:
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameStyle(QFrame.NoFrame)
        self._scroll_area.setStyleSheet(SCROLL_BAR_STYLE)

        self._scroll_area_content = QWidget()
        self._scroll_area_layout = QVBoxLayout(self._scroll_area_content)

        self._data_display = QTextEdit()
        self._data_display.setStyleSheet(RAW_VALUE_BOX_STYLE)
        self._data_display.setReadOnly(True)

        self._scroll_area_layout.addWidget(self._data_display)
        self._scroll_area.setWidget(self._scroll_area_content)

        self._layout.addWidget(self._scroll_area)


    #- Private: Sensor Data ------------------------------------------------------------------------

    # Update the plot from graphlines unless the UI is frozen.
    def _update_plot(self) -> None:
        if self._freeze: return     # don't update graph if freeze is active

        self._plot_widget.clear()   # clear old plots

        for line in self._graphlines:
            sliced_line = pg.PlotDataItem(
                x = self._counter[self._toggle_recent:],
                y = line.reading(self._toggle_recent),
                pen = pg.mkPen(color=line.color(), width=2),
            )

            self._plot_widget.addItem(sliced_line)


    #- Private: Button Actions ---------------------------------------------------------------------

    # Toggle between showing latest windowed values and full history.
    def _button_toggle_recent(self) -> None:
        # dynamic names and hover-descriptions
        view_button_options = [ "Zoom Latest", "View All" ]
        view_button_tips = ["Plot only latest 10 readings [t]", "Plot all readings [t]"]

        # toggle between values 0 and -10
        # don't want to define another static or global variable
        self._toggle_recent = 0 - 10 - self._toggle_recent

        # don't want to use if else on self._toggle_recent to get 0/1 (index for the two text lists)
        index = self._toggle_recent % 11

        self._data_view_button.setText(view_button_options[index])
        self._data_view_button.setToolTip(view_button_tips[index])
        self._update_plot()


    # Clear all recorded data and reset view state.
    def _button_clear_data(self) -> None:
        self._counter = [0]
        self._toggle_recent = 0

        for line in self._graphlines: line.reset_reading()

        self._data_display.clear()
        self._update_plot()


    # Toggle freezing of live plotting (pause/resume visuals).
    def _button_freeze(self) -> None:
        self._freeze = not self._freeze
        self._freeze_button.setText("Unfreeze" if self._freeze else "Freeze")
        self._update_plot()


    # Open a file dialog and save the raw text of incoming data to disk.
    def _button_save(self) -> None:
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", datestring(), "Text Files (*.txt);;All Files (*)",
            options=QFileDialog.Options()
        )

        if file_path:
            with open(file_path, 'w') as file:
                file.write(self._data_display.toPlainText())

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.NoIcon)
            msg_box.setWindowTitle("Success")
            msg_box.setText("File saved successfully!")
            msg_box.exec_()


    # Launch gesture dialog, handle recording flow and hand over data to analyser.
    def _button_gesture(self) -> None:
        #========================================
        # sensor/source names
        #========================================
        # get all the set names from the graph footer EditLabels
        source_names: List[str] = [ source.text() for source in self._graphlines ]

        # ensure all sensors have unique names
        if not check_sources_name(source_names): return

        #========================================
        # pop the gesture dialog window
        #========================================
        # pop the window
        dialog = GestureDialog(source_names)
        if dialog.exec() != QDialog.Accepted:
            return # return if the window was cancelled or just exited without okay signal

        # input values entered in the window, retrieve them
        dialog_return = dialog.get_inputs()
        if not dialog_return:
            return # return if the values were None: happens when invalid values are entered

        #========================================
        # parse retrieved values depending on the window tab it was returned from
        #========================================
        tab, dialog_inputs = dialog_return

        if tab == TAB1:
            # dialog_inputs: GestureInput
            repeats: int = dialog_inputs.repeats
            filename: str = dialog_inputs.filename
            parameters: Dict[int, ModelParameters] = dialog_inputs.parameters
            analyse_method = analyse_create # analyse method to call

        elif tab == TAB2:
            # dialog_inputs: GestureUpdater
            repeats: int = dialog_inputs.file.repeats
            filename: str = dialog_inputs.file.filename
            parameters: Dict[int, ModelParameters] = dialog_inputs.file.parameters
            analyse_method = analyse_update # analyse method to call

        else: return # return for invalid tabs

        #========================================
        # pop the gesture record window
        #========================================
        # start blank recording session
        self._records_stamps: int2d_t = []

        # repeats = how many readings to read
        # self._record_data = method to handle data record. it accepts RECORD_ACTION_x enums args
        inputs = RecordInputs(repeats, self._record_data)

        if inputs.exec() != QDialog.Accepted:
            self._record_data(RECORD_ACTION_TERMINATE) # if a record was created, close & clear it
            return # exit if pressed cancel on the record prompt

        #========================================
        # get sensor values and timestamps for the sessions recorded
        #========================================

        # Basically, the RecordInputs window stores timestamps for when to start and stop recordings
        # start/stop/cancel/discard/restart all that is handled by self._record_data() method.
        #
        # At this stage of the code, we have self._records_stamps which is 2d-int array with start
        # and stop timestamps. the following code-block uses that to slice highlighted data from the
        # time (self._counter) and reading (self._graphlines) lists.
        #
        # self._graphlines is a list of all sources/sensors, here, each individual that's selected
        # is processed and selected data is stored in a sensor_values_t list.

        analyse_data: sensor_values_t = []
        for source in parameters.keys():
            source_info: SensorValues = SensorValues(source_names[source])

            for start, end in self._records_stamps:
                source_info.AddValues(
                    self._counter[start:end],
                    self._graphlines[source].reading(start, end)
                )

            analyse_data.append(source_info)

        analyse_method(
            filename, analyse_data, parameters.values(),
            getattr(dialog_inputs, 'data', None) # to make the two analyse methods similar
        )


    # Record control callback implementing start/stop/discard/restart semantics.
    def _record_data(self, action: int) -> None:
        # create a new timestamp- add start point
        if action == RECORD_ACTION_START:
            self._records_stamps.append([len(self._counter)])
            self._plot_widget.setBackground("#121212")

        # add end point for last created timestamp
        elif action == RECORD_ACTION_STOP:
            self._records_stamps[-1].append(len(self._counter))
            self._plot_widget.setBackground(BACKGROUND_COLOR)

        # delete the last timestamp
        elif action == RECORD_ACTION_DISCARD:
            self._records_stamps.pop()
            self._plot_widget.setBackground("#1f1212")

        # reset the start point for the current timestamp to current counter value
        elif action == RECORD_ACTION_RESTART:
            self._records_stamps[-1][0] = len(self._counter)

        # empty the record, clear all timestamps
        else: # == RECORD_ACTION_TERMINATE
            self._records_stamps = []
            self._plot_widget.setBackground(BACKGROUND_COLOR)


    # Refresh the list of available serial connection ports in the combobox.
    def _button_refresh_connections(self) -> None:
        self._connection_list.clear() # remove old values
        self._connection_list.addItems(["<SELECT>"] + connected_ports())


    #- Public Calls --------------------------------------------------------------------------------

    # Append new sensor values to internal buffers and create graph lines as needed.
    def add_data(self, values: List[Any]) -> None:
        # add data to the raw data area
        self._data_display.append(str(values))
        self._counter.append(self._counter[-1] + 1)

        # clear old data and add new lines
        for i, value in enumerate(values):
            # only plot data if values are numeric
            if not (isinstance(value, float) or isinstance(value, int)): continue

            #========================================
            # create new graphline
            #========================================
            if i >= len(self._graphlines):
                #========================================
                # draw the line
                #========================================
                colors: Tuple[int, int, int] = new_color()
                text_label = EditLabel(f"source{i+1}", colors)

                new_line: GraphLine = GraphLine(
                    reading=[value] * len(self._counter),
                    color=colors,
                    title=text_label
                )

                self._graphlines.append(new_line)

                #========================================
                # draw legend
                #========================================
                square = QLabel()
                square.setFixedSize(QSize(5, 20))
                square.setStyleSheet(
                    f"background-color: rgb({colors[0]}, {colors[1]}, {colors[2]});"
                )

                h_layout = QHBoxLayout()
                h_layout.addWidget(square)
                h_layout.addWidget(text_label.obj())

                self._legend_layout.addLayout(h_layout)

            #========================================
            # update existing line
            #========================================
            else:
                graphline: GraphLine = self._graphlines[i]
                graphline.add_reading(value)

        self._update_plot()


    #- Keyboard Shortcut Override ------------------------------------------------------------------

    # Map keyboard events to the corresponding toolbar button actions.
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_G:
            self._gesture_button.click()

        elif event.key() == Qt.Key_Space:
            self._freeze_button.click()

        elif event.key() == Qt.Key_S:
            self._save_button.click()

        elif event.key() == Qt.Key_T:
            self._data_view_button.click()

        elif event.key() == Qt.Key_Escape:
            self._clear_button.click()

        else:
            super().keyPressEvent(event)

