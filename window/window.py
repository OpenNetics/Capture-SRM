
# window/window.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any, List, Tuple

from redwrenlib.typing import int2d_t, ModelParameters
import pyqtgraph as pg
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget,
    QComboBox, QFileDialog, QLabel, QMessageBox, QTextEdit,
    QHBoxLayout, QVBoxLayout, QScrollArea,
)

from analyse import analyse_create, analyse_update
from utils.extra import new_color, datestring
from utils.ui import (
    spacedh,
    EditLabel, create_button,
)
from utils.style import (
    APPLICATION_NAME,
    BACKGROUND_COLOR,
    WINDOW_SIZE, GRAPH_HEIGHT,
    RAW_VALUE_BOX_STYLE, COMBOBOX_STYLE,
)
from utils.typing import (
    SensorData,
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

        self._layout: QVBoxLayout = QVBoxLayout()
        self.setLayout(self._layout)

        # Variables
        self._graphlines: List[GraphLine] = []
        self._counter: List[float] = [0]
        self._toggle_recent: int = 0
        self._freeze: bool = False

        # Build UI Components
        self._init_buttons()
        self._init_graph_plot()
        self._init_graph_footer()
        self._init_raw_data()

    #- Private: Initialise Components --------------------------------------------------------------

    # Build the top button row and attach callbacks.
    def _init_buttons(self) -> None:
        button_layout = QHBoxLayout()

        self._gesture_button = create_button(
            "Gesture", "Play with gesture files [g]", self._button_gesture)
        self._save_button = create_button(
            "Save", "Save read data in text file [s]", self._button_save)
        self._data_view_button = create_button(
            "Zoom Latest", "Plot only latest 10 readings [t]", self._button_toggle_recent)
        self._freeze_button = create_button(
            "Freeze", "Toggle freezing live plot [space]", self._button_freeze)
        self._clear_button = create_button(
            "Clear", "Clear all read data [esc]", self._button_clear_data)

        button_layout.addWidget(self._gesture_button)
        button_layout.addWidget(self._save_button)
        spacedh(button_layout)
        button_layout.addWidget(self._data_view_button)
        button_layout.addWidget(self._freeze_button)
        button_layout.addWidget(self._clear_button)

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
        # Legends are added to this layout
        self._legend_layout = QHBoxLayout()
        self._layout.addLayout(self._legend_layout)

        # Port & Baud Rate Selector
        self._connection_list = QComboBox()
        self._connection_list.addItems(["<SELECT>"] + connected_ports())
        self._connection_list.setToolTip("Select Connection Port")
        self._connection_list.setStyleSheet(COMBOBOX_STYLE)
        self._connection_list.currentTextChanged.connect(select_port)

        connection_refresh_button = create_button(
            "Refresh", "Reflesh port list", self._button_refresh_connections)

        self._baud_rate_list = QComboBox()
        self._baud_rate_list.addItems(baud_rates())
        self._baud_rate_list.setToolTip("Select Baud Rate")
        self._baud_rate_list.setCurrentText("115200")
        self._baud_rate_list.setStyleSheet(COMBOBOX_STYLE)
        self._baud_rate_list.currentTextChanged.connect(select_baud_rate)

        self._legend_layout.addWidget(connection_refresh_button)
        self._legend_layout.addWidget(self._connection_list)
        self._legend_layout.addWidget(self._baud_rate_list)
        spacedh(self._legend_layout)


    # Create the scrollable raw data text area for incoming sensor values.
    def _init_raw_data(self) -> None:
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)

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
        if self._freeze:
            return

        self._plot_widget.clear()

        for line in self._graphlines:
            sliced_line = pg.PlotDataItem(
                x = self._counter[self._toggle_recent:],
                y = line.Reading(self._toggle_recent),
                pen = pg.mkPen(color=line.Color(), width=2),
            )

            self._plot_widget.addItem(sliced_line)

    #- Private: Button Actions ---------------------------------------------------------------------

    # Toggle between showing latest windowed values and full history.
    def _button_toggle_recent(self) -> None:
        view_button_options = [ "Zoom Latest", "View All" ]
        view_button_tips = ["Plot only latest 10 readings [t]", "Plot all readings [t]"]

        self._toggle_recent = 0 - 10 - self._toggle_recent
        self._data_view_button.setText(view_button_options[self._toggle_recent % 11])
        self._data_view_button.setToolTip(view_button_tips[self._toggle_recent % 11])
        self._update_plot()


    # Clear all recorded data and reset view state.
    def _button_clear_data(self) -> None:
        self._counter = [0]
        self._toggle_recent = 0

        for line in self._graphlines:
            line.ResetReading()

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
        source_names: List[str] = [ source.Title().text() for source in self._graphlines ]
        if not check_sources_name(source_names): return

        self._records_stamps: int2d_t = [] # start blank recording session
        dialog = GestureDialog(source_names)
        if dialog.exec() != QDialog.Accepted: return

        dialog_return = dialog.get_inputs()
        if not dialog_return: return

        tab, dialog_inputs = dialog_return

        if tab == TAB1:
            # dialog_inputs: GestureInput
            repeats: int = dialog_inputs.repeats
            sensors: Tuple[int, ...] = dialog_inputs.sensors
            name: str = dialog_inputs.name
            parameters: ModelParameters = dialog_inputs.parameters
            analyse_method = analyse_create

        elif tab == TAB2:
            # dialog_inputs: GestureUpdater
            repeats: int = dialog_inputs.file.repeats
            sensors: Tuple[int, ...] = dialog_inputs.file.sensors
            name: str = dialog_inputs.file.name
            parameters: ModelParameters = dialog_inputs.file.parameters
            analyse_method = analyse_update
        else:
            return

        inputs = RecordInputs(repeats, self._record_data)
        if inputs.exec() != QDialog.Accepted:
            self._record_data(RECORD_ACTION_TERMINATE)
            return

        analyse_data: List[SensorData] = []
        for source in sensors:
            source_info: SensorData = SensorData(source_names[source])

            for start, end in self._records_stamps:
                source_info.AddValues(
                    self._counter[start:end],
                    self._graphlines[source].Reading(start, end)
                )

            analyse_data.append(source_info)

        analyse_method(name, analyse_data, parameters, getattr(dialog_inputs, 'data', None))


    # Record control callback implementing start/stop/discard/restart semantics.
    def _record_data(self, action: int) -> None:
        if action == RECORD_ACTION_START:
            self._records_stamps.append([len(self._counter)])
            self._plot_widget.setBackground("#121212")

        elif action == RECORD_ACTION_STOP:
            self._records_stamps[-1].append(len(self._counter))
            self._plot_widget.setBackground(BACKGROUND_COLOR)

        elif action == RECORD_ACTION_DISCARD:
            self._records_stamps.pop()
            self._plot_widget.setBackground("#1f1212")

        elif action == RECORD_ACTION_RESTART:
            self._records_stamps[-1][0] = len(self._counter)

        else:
            self._records_stamps = []
            self._plot_widget.setBackground(BACKGROUND_COLOR)


    # Refresh the list of available serial connection ports in the combobox.
    def _button_refresh_connections(self) -> None:
        self._connection_list.clear()
        self._connection_list.addItems(["<SELECT>"] + connected_ports())

    #- Public Calls --------------------------------------------------------------------------------

    # Append new sensor values to internal buffers and create graph lines as needed.
    def add_data(self, values: List[Any]) -> None:
        # add data to the raw data area
        self._data_display.append(str(values))
        self._counter.append(self._counter[-1] + 1)

        # Clear old data and add new lines
        for i, value in enumerate(values):
            # only plot data if values are numeric
            if not (isinstance(value, float) or isinstance(value, int)):
                continue

            if i >= len(self._graphlines):
                colors: Tuple[int, int, int] = new_color()
                text_label = EditLabel(f"source{i+1}")

                new_line: GraphLine = GraphLine(
                    reading=[value] * len(self._counter),
                    color=colors,
                    title=text_label
                )

                self._graphlines.append(new_line)

                # Draw legend
                square = QLabel()
                square.setFixedSize(QSize(20, 20))
                square.setStyleSheet(
                    f"background-color: rgb({colors[0]}, {colors[1]}, {colors[2]});"
                )

                h_layout = QHBoxLayout()
                h_layout.addWidget(square)
                h_layout.addWidget(text_label)

                self._legend_layout.addLayout(h_layout)

            else:
                graphline: GraphLine = self._graphlines[i]
                graphline.AddReading(value)

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

