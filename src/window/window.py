
# window/window.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any

import pyqtgraph as pg
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget, QFrame,
    QComboBox, QFileDialog, QLabel, QMessageBox, QTextEdit, QSlider,
    QHBoxLayout, QVBoxLayout, QScrollArea,
)
from redwrenlib.typing import int2d_t
from redwrenlib.utils.debug import alert

from analyse import analyse_create, analyse_update
from utils.extra import new_color, datestring
from utils.ui import (
    EditLabel,
    spacedh, create_button,
)
from utils.style import (
    APPLICATION_NAME,
    BACKGROUND_COLOR, BACKGROUND_HIGHLIGHT_COLOR,
    WINDOW_SIZE, GRAPH_HEIGHT, ZOOM_SLIDER_WIDTH,
    RAW_VALUE_BOX_STYLE, COMBOBOX_STYLE, SCROLL_BAR_STYLE, LABEL_BODY_STYLE,
)
from utils.typing import (
    SensorValues, RecordAction, Tab,
    sensor_values_t,
)
from talk import (
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
        self._graphlines: list[GraphLine] = []
        self._counter: list[float] = [0]
        self._toggle_recent: int = 0
        self._freeze: bool = False

        #========================================
        # initialise the system
        #========================================
        self._init_header()
        self._init_graph_plot()
        self._init_graph_footer()
        self._init_raw_data()


    #- Private: Initialise Components --------------------------------------------------------------

    # Build the top button row and attach callbacks.
    def _init_header(self) -> None:
        header_layout = QHBoxLayout()

        #========================================
        # top-left buttons
        #========================================
        self._gesture_button = create_button(
            "Gesture", "Play with gesture files [g]", self._button_gesture)
        header_layout.addWidget(self._gesture_button)

        self._save_button = create_button(
            "Save", "Save read data in text file [s]", self._button_save)
        header_layout.addWidget(self._save_button)

        #========================================
        # whitespace dividing left-right regions
        #========================================
        spacedh(header_layout)

        #========================================
        # view slider
        #========================================
        zoom_label = QLabel("Zoom")
        zoom_label.setStyleSheet(LABEL_BODY_STYLE)
        header_layout.addWidget(zoom_label)

        self._zoom_slider = QSlider(Qt.Orientation.Horizontal, self)
        self._zoom_slider.setRange(0, 20)
        self._zoom_slider.setTickInterval(5)
        self._zoom_slider.setValue(0)
        self._zoom_slider.setMaximumWidth(ZOOM_SLIDER_WIDTH)
        self._zoom_slider.setToolTip(" [All] ")
        self._zoom_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        header_layout.addWidget(self._zoom_slider)

        # update label only for allowed values
        self._zoom_slider.valueChanged.connect(self._zoom_value)

        #========================================
        # top-right buttons
        #========================================
        self._freeze_button = create_button(
            "Freeze", "Toggle freezing live plot [space]", self._button_freeze)
        header_layout.addWidget(self._freeze_button)

        self._clear_button = create_button(
            "Clear", "Clear all read data [esc]", self._button_clear_data)
        header_layout.addWidget(self._clear_button)

        # to the layout
        self._layout.addLayout(header_layout)


    # Create and configure the plot widget used for realtime graphs.
    def _init_graph_plot(self) -> None:
        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setBackground(BACKGROUND_COLOR)
        self._plot_widget.setDefaultPadding(0)
        self._layout.addWidget(self._plot_widget)
        self._plot_widget.setFixedHeight(GRAPH_HEIGHT)

        self._plot_widget.showGrid(x=True, y=True)
        self._plot_widget.setMouseEnabled(False, False)


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

    def _zoom_value(self, value: int):
        value *= 5
        label = " [All] " if value == 0 else f" Viewing latest {value} "
        self._zoom_slider.setToolTip(label)
        self._toggle_recent = 0 - value


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
        source_names: tuple[str, ...] = tuple([source.text() for source in self._graphlines])

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
        # parse retrieved values depending on the tab it was returned from
        #========================================
        tab, dialog_inputs = dialog_return

        analyse_method = analyse_create if tab == Tab.CREATE else analyse_update
        # .get_inputs() returns None when tab isnt Tab.CREATE or Tab.UPDATE anyways

        #========================================
        # pop the gesture record window
        #========================================
        # start blank recording session
        self._records_stamps: int2d_t = []

        # repeats = how many readings to read
        # self._record_data = method to handle data record. it accepts RecordAction.x enums args
        inputs = RecordInputs(dialog_inputs.repeats, self._record_data)

        if inputs.exec() != QDialog.Accepted:
            self._record_data(RecordAction.TERMINATE) # if a record was created, close & clear it
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
        for i, source in enumerate(dialog_inputs.source_ids):
            source_info: SensorValues = SensorValues(dialog_inputs.file_sources[i])

            for start, end in self._records_stamps:
                source_info.AddValues(
                    self._counter[start:end],
                    self._graphlines[source].reading(start, end)
                )

            analyse_data.append(source_info)

        analyse_method(dialog_inputs.filename, analyse_data, dialog_inputs.parameters)


    # Record control callback implementing start/stop/discard/restart semantics.
    def _record_data(self, action: RecordAction) -> None:
        # create a new timestamp- add start point
        if action == RecordAction.START:
            self._records_stamps.append([len(self._counter)])
            self._plot_widget.setBackground(BACKGROUND_HIGHLIGHT_COLOR)

        # add end point for last created timestamp
        elif action == RecordAction.STOP:
            self._records_stamps[-1].append(len(self._counter))
            self._plot_widget.setBackground(BACKGROUND_COLOR)

        # delete the last timestamp
        elif action == RecordAction.DISCARD:
            self._records_stamps.pop()
            self._plot_widget.setBackground(BACKGROUND_HIGHLIGHT_COLOR)

        # reset the start point for the current timestamp to current counter value
        elif action == RecordAction.RESTART:
            self._records_stamps[-1][0] = len(self._counter)

        # empty the record, clear all timestamps
        else: # == RecordAction.TERMINATE
            self._records_stamps = []
            self._plot_widget.setBackground(BACKGROUND_COLOR)


    # Refresh the list of available serial connection ports in the combobox.
    def _button_refresh_connections(self) -> None:
        self._connection_list.clear() # remove old values
        self._connection_list.addItems(["<SELECT>"] + connected_ports())


    #- Public Calls --------------------------------------------------------------------------------

    # Append new sensor values to internal buffers and create graph lines as needed.
    def add_data(self, values: list[Any]) -> None:
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
                colors: tuple[int, int, int] = new_color()
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

        elif event.key() in [Qt.Key_Plus, Qt.Key_Equal]:
            value = self._zoom_slider.value()
            if value != 20: self._zoom_slider.setValue(value + 1)

        elif event.key() in [Qt.Key_Underscore, Qt.Key_Minus]:
            value = self._zoom_slider.value()
            if value != 0: self._zoom_slider.setValue(value - 1)

        else:
            super().keyPressEvent(event)

