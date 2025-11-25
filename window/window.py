
# window/window.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any, List, Tuple

import pyqtgraph as pg
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget,
    QComboBox, QFileDialog, QLabel, QMessageBox, QTextEdit,
    QHBoxLayout, QVBoxLayout, QScrollArea,
)

from utils.ui import (
    spacedh,
    EditLabel, create_button,
    new_color,
)
from utils.style import (
    APPLICATION_NAME,
    BACKGROUND_COLOR,
    WINDOW_SIZE, GRAPH_HEIGHT,
    RAW_VALUE_BOX_STYLE, COMBOBOX_STYLE,
)
from utils.typedefs import (
    SensorData,
    int2d_t,
    RECORD_ACTION_STOP,
    RECORD_ACTION_START,
    RECORD_ACTION_DISCARD,
    RECORD_ACTION_RESTART,
    RECORD_ACTION_TERMINATE,
    TAB1, TAB2,
)
from serial import (
    select_port, select_baud_rate,
    baud_rates, connected_ports
)
from analyse import analyse

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

        self.setWindowTitle(APPLICATION_NAME)
        self.resize(WINDOW_SIZE["width"], WINDOW_SIZE["height"])
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        self.layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self.layout)

        # Variables
        self.graphlines: List[GraphLine] = []
        self.counter: List[float] = [0]
        self.toggle_recent: int = 0
        self.freeze: bool = False

        # Build UI Components
        self.init_buttons()
        self.init_graph_plot()
        self.init_graph_footer()
        self.init_raw_data()

    #- Initialise Components ----------------------------------------------------------------------

    # Build the top button row and attach callbacks.
    def init_buttons(self) -> None:
        button_layout = QHBoxLayout()

        self.gesture_button = create_button(
            "Gesture", "Play with gesture files [g]", self.button_gesture)
        self.save_button = create_button(
            "Save", "Save read data in text file [s]", self.button_save)
        self.data_view_button = create_button(
            "Zoom Latest", "Plot only latest 10 readings [t]", self.button_toggle_recent)
        self.freeze_button = create_button(
            "Freeze", "Toggle freezing live plot [space]", self.button_freeze)
        self.clear_button = create_button(
            "Clear", "Clear all read data [esc]", self.button_clear_data)

        button_layout.addWidget(self.gesture_button)
        button_layout.addWidget(self.save_button)
        spacedh(button_layout)
        button_layout.addWidget(self.data_view_button)
        button_layout.addWidget(self.freeze_button)
        button_layout.addWidget(self.clear_button)

        self.layout.addLayout(button_layout)


    # Create and configure the plot widget used for realtime graphs.
    def init_graph_plot(self) -> None:
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(BACKGROUND_COLOR)
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setFixedHeight(GRAPH_HEIGHT)

        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setMouseEnabled(True, True)


    # Create footer area containing legends and connection/baud selectors.
    def init_graph_footer(self) -> None:
        # Legends are added to this layout
        self.legend_layout = QHBoxLayout()
        self.layout.addLayout(self.legend_layout)

        # Port & Baud Rate Selector
        self.connection_list = QComboBox()
        self.connection_list.addItems(["<SELECT>"] + connected_ports())
        self.connection_list.setToolTip("Select Connection Port")
        self.connection_list.setStyleSheet(COMBOBOX_STYLE)
        self.connection_list.currentTextChanged.connect(select_port)

        connection_refresh_button = create_button(
            "Refresh", "Reflesh port list", self.button_refresh_connections)

        self.baud_rate_list = QComboBox()
        self.baud_rate_list.addItems(baud_rates())
        self.baud_rate_list.setToolTip("Select Baud Rate")
        self.baud_rate_list.setCurrentText("115200")
        self.baud_rate_list.setStyleSheet(COMBOBOX_STYLE)
        self.baud_rate_list.currentTextChanged.connect(select_baud_rate)

        self.legend_layout.addWidget(connection_refresh_button)
        self.legend_layout.addWidget(self.connection_list)
        self.legend_layout.addWidget(self.baud_rate_list)
        spacedh(self.legend_layout)


    # Create the scrollable raw data text area for incoming sensor values.
    def init_raw_data(self) -> None:
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_content = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_content)

        self.data_display = QTextEdit()
        self.data_display.setStyleSheet(RAW_VALUE_BOX_STYLE)
        self.data_display.setReadOnly(True)

        self.scroll_area_layout.addWidget(self.data_display)
        self.scroll_area.setWidget(self.scroll_area_content)

        self.layout.addWidget(self.scroll_area)

    #- Sensor Data --------------------------------------------------------------------------------

    # Update the plot from graphlines unless the UI is frozen.
    def update_plot(self) -> None:
        if self.freeze:
            return

        self.plot_widget.clear()

        for line in self.graphlines:
            sliced_line = pg.PlotDataItem(
                x = self.counter[self.toggle_recent:],
                y = line.Reading(self.toggle_recent),
                pen = pg.mkPen(color=line.Color(), width=2),
            )

            self.plot_widget.addItem(sliced_line)


    # Append new sensor values to internal buffers and create graph lines as needed.
    def add_data(self, values: List[Any]) -> None:
        # add data to the raw data area
        self.data_display.append(str(values))
        self.counter.append(self.counter[-1] + 1)

        # Clear old data and add new lines
        for i, value in enumerate(values):
            # only plot data if values are numeric
            if not (isinstance(value, float) or isinstance(value, int)):
                continue

            if i >= len(self.graphlines):
                colors: Tuple[int, int, int] = new_color()
                text_label = EditLabel(f"source{i+1}")

                new_line: GraphLine = GraphLine(
                    reading=[value] * len(self.counter),
                    color=colors,
                    title=text_label
                )

                self.graphlines.append(new_line)

                # Draw legend
                square = QLabel()
                square.setFixedSize(QSize(20, 20))
                square.setStyleSheet(
                    f"background-color: rgb({colors[0]}, {colors[1]}, {colors[2]});"
                )

                h_layout = QHBoxLayout()
                h_layout.addWidget(square)
                h_layout.addWidget(text_label)

                self.legend_layout.addLayout(h_layout)

            else:
                graphline: GraphLine = self.graphlines[i]
                graphline.AddReading(value)

        self.update_plot()

    #- Button Actions -----------------------------------------------------------------------------

    # Toggle between showing latest windowed values and full history.
    def button_toggle_recent(self) -> None:
        view_button_options = [ "Zoom Latest", "View All" ]
        view_button_tips = ["Plot only latest 10 readings [t]", "Plot all readings [t]"]

        self.toggle_recent = 0 - 10 - self.toggle_recent
        self.data_view_button.setText(view_button_options[self.toggle_recent % 11])
        self.data_view_button.setToolTip(view_button_tips[self.toggle_recent % 11])
        self.update_plot()


    # Clear all recorded data and reset view state.
    def button_clear_data(self) -> None:
        self.counter = [0]
        self.toggle_recent = 0

        for line in self.graphlines:
            line.ResetReading()

        self.data_display.clear()
        self.update_plot()


    # Toggle freezing of live plotting (pause/resume visuals).
    def button_freeze(self) -> None:
        self.freeze = not self.freeze
        self.freeze_button.setText("Unfreeze" if self.freeze else "Freeze")
        self.update_plot()


    # Open a file dialog and save the raw text of incoming data to disk.
    def button_save(self) -> None:
        # Open file dialog to select save location
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File", "lol", "Text Files (*.txt);;All Files (*)",
            options=QFileDialog.Options()
        )

        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.data_display.toPlainText())

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.NoIcon)
            msg_box.setWindowTitle("Success")
            msg_box.setText("File saved successfully!")
            msg_box.exec_()


    # Launch gesture dialog, handle recording flow and hand over data to analyser.
    def button_gesture(self) -> None:
        source_names: List[str] = [ source.Title().text() for source in self.graphlines ]
        if not check_sources_name(source_names):
            return

        self.records_stamps: int2d_t = [] # start blank recording session

        dialog = GestureDialog(source_names)

        if dialog.exec() != QDialog.Accepted:
            return

        dialog_return = dialog.get_inputs()
        if not dialog_return: return

        tab, dialog_inputs = dialog_return

        inputs = RecordInputs(dialog_inputs.repeats, self.record_data)
        if inputs.exec() != QDialog.Accepted:
            self.record_data(RECORD_ACTION_TERMINATE)
            return

        analyse_data: List[SensorData] = []
        for source in dialog_inputs.sensors:
            source_info: SensorData = SensorData(source_names[source])

            for start, end in self.records_stamps:
                source_info.AddValues(
                    self.counter[start:end],
                    self.graphlines[source].Reading(start, end)
                )

            analyse_data.append(source_info)

        if tab == TAB1:
            analyse(dialog_inputs.name, analyse_data, dialog_inputs.parameters)


    # Record control callback implementing start/stop/discard/restart semantics.
    def record_data(self, action: int) -> None:
        if action == RECORD_ACTION_START:
            self.records_stamps.append([len(self.counter)])
            self.plot_widget.setBackground("#121212")

        elif action == RECORD_ACTION_STOP:
            self.records_stamps[-1].append(len(self.counter))
            self.plot_widget.setBackground(BACKGROUND_COLOR)

        elif action == RECORD_ACTION_DISCARD:
            self.records_stamps.pop()
            self.plot_widget.setBackground("#1f1212")

        elif action == RECORD_ACTION_RESTART:
            self.records_stamps[-1][0] = len(self.counter)

        else:
            self.records_stamps = []
            self.plot_widget.setBackground(BACKGROUND_COLOR)


    # Refresh the list of available serial connection ports in the combobox.
    def button_refresh_connections(self) -> None:
        self.connection_list.clear()
        self.connection_list.addItems(connected_ports())


    # Map keyboard events to the corresponding toolbar button actions.
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_G:
            self.gesture_button.click()

        elif event.key() == Qt.Key_Space:
            self.freeze_button.click()

        elif event.key() == Qt.Key_S:
            self.save_button.click()

        elif event.key() == Qt.Key_T:
            self.data_view_button.click()

        elif event.key() == Qt.Key_Escape:
            self.clear_button.click()

        else:
            super().keyPressEvent(event)

