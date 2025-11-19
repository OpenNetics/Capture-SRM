
# window/layout.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List

import pyqtgraph as pg
from PySide6.QtCore import Qt, QSize
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

from .gesture_dialog import GestureDialog
from .record_inputs import RecordInputs
from .helper import (
    EditLabel,
    new_color,
    create_button,
    spaced_element,
)
from .style import (
    BACKGROUND_COLOR,
    APPLICATION_NAME,
    WINDOW_SIZE,
    GRAPH_HEIGHT,
    RAW_VALUE_BOX_STYLE,
    COMBOBOX_STYLE,
    RECORD_ACTION_STOP,
    RECORD_ACTION_START,
    RECORD_ACTION_DISCARD,
    RECORD_ACTION_RESTART,
    RECORD_ACTION_TERMINATE
)

from analyse import analyse
from serial import (
    select_port,
    select_baud_rate,
    baud_rates,
    connected_ports
)


#- Window Class ------------------------------------------------------------------------------------

class LiveGraph(QWidget):

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APPLICATION_NAME)
        self.resize(WINDOW_SIZE["width"], WINDOW_SIZE["height"])
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Variables
        self.reading_source = []
        self.counter = [0]
        self.toggle_recent = 0
        self.freeze = False

        # Build UI Components
        self.init_buttons()
        self.init_graph_plot()
        self.init_graph_footer()
        self.init_raw_data()

    #- Initialise Components ----------------------------------------------------------------------

    def init_buttons(self) -> None:
        button_layout = QHBoxLayout()

        self.gesture_button = create_button("Gesture", self.button_gesture)
        self.save_button = create_button("Save", self.button_save)
        self.data_view_button = create_button("Zoom Latest", self.button_toggle_recent)
        self.freeze_button = create_button("Freeze", self.button_freeze)
        self.clear_button = create_button("Clear", self.button_clear_data)

        button_layout.addWidget(self.gesture_button)
        button_layout.addWidget(self.save_button)
        spaced_element(button_layout)
        button_layout.addWidget(self.data_view_button)
        button_layout.addWidget(self.freeze_button)
        button_layout.addWidget(self.clear_button)

        self.layout.addLayout(button_layout)


    def init_graph_plot(self) -> None:
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(BACKGROUND_COLOR)
        self.layout.addWidget(self.plot_widget)
        self.plot_widget.setFixedHeight(GRAPH_HEIGHT)

        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setMouseEnabled(True, True)


    def init_graph_footer(self) -> None:
        # Legends are added to this layout
        self.legend_layout = QHBoxLayout()
        self.layout.addLayout(self.legend_layout)

        # Port & Baud Rate Selector
        self.connection_list = QComboBox()
        self.connection_list.addItems(connected_ports())
        self.connection_list.setStyleSheet(COMBOBOX_STYLE)
        self.connection_list.currentTextChanged.connect(select_port)

        connection_refresh_button = create_button("Refresh", self.button_refresh_connections)

        self.baud_rate_list = QComboBox()
        self.baud_rate_list.addItems(baud_rates())
        self.baud_rate_list.setStyleSheet(COMBOBOX_STYLE)
        self.baud_rate_list.currentTextChanged.connect(select_baud_rate)

        self.legend_layout.addWidget(connection_refresh_button)
        self.legend_layout.addWidget(self.connection_list)
        self.legend_layout.addWidget(self.baud_rate_list)
        spaced_element(self.legend_layout)


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

    def update_plot(self) -> None:
        if self.freeze:
            return

        self.plot_widget.clear()

        for line in self.reading_source:
            sliced_line = pg.PlotDataItem(
                x = self.counter[self.toggle_recent:],
                y = line["reading"][self.toggle_recent:],
                pen = pg.mkPen(color=line["color"], width=2),
            )

            self.plot_widget.addItem(sliced_line)


    def add_data(self, values: List[float]) -> None:
        # add data to the raw data area
        self.data_display.append(str(values))

        self.counter.append(self.counter[-1] + 1)

        # Clear old data and add new lines
        for i, value in enumerate(values):

            if i >= len(self.reading_source):
                colors: (int, int, int) = new_color()
                text_label = EditLabel(f"source{i+1}")

                new_line: dict = {
                    "reading": [value] * len(self.counter),
                    "color": colors,
                    "title": text_label
                }

                self.reading_source.append(new_line)

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
                self.reading_source[i]["reading"].append(value)

        self.update_plot()

    #- Button Actions -----------------------------------------------------------------------------

    def button_toggle_recent(self) -> None:
        view_button_options = [ "Zoom Latest", "View All" ]
        self.toggle_recent = 0 - 10 - self.toggle_recent
        self.data_view_button.setText(view_button_options[self.toggle_recent % 11])
        self.update_plot()


    def button_clear_data(self) -> None:
        self.counter = [0]
        self.toggle_recent = 0

        for line in self.reading_source:
            line["reading"] = [line["reading"][-1]]

        self.data_display.clear()
        self.update_plot()


    def button_freeze(self) -> None:
        self.freeze = not self.freeze
        self.freeze_button.setText("Unfreeze" if self.freeze else "Freeze")
        self.update_plot()


    def button_save(self) -> None:
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
            with open(file_path, 'w') as file:
                file.write(self.data_display.toPlainText())

            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.NoIcon)
            msg_box.setWindowTitle("Success")
            msg_box.setText("File saved successfully!")
            msg_box.exec_()


    def button_gesture(self) -> None:
        self.records_stamps = []
        source_names = [ source["title"].text() for source in self.reading_source ]

        dialog = GestureDialog(source_names)

        if dialog.exec() != QDialog.Accepted:
            return

        values = dialog.get_inputs()

        if not values:
            return

        gesture_name, repeats, selected_sources, model_param = values

        inputs = RecordInputs(repeats, self.record_data)
        if inputs.exec() != QDialog.Accepted:
            self.record_data(RECORD_ACTION_TERMINATE)
            return

        analyse_data = []
        for source in selected_sources:
            source_info: dict = {
                "name": source_names[source],
                "data": []
            }
            for start, end in self.records_stamps:
                source_info["data"].append(self.reading_source[source]["reading"][start:end])

            analyse_data.append(source_info)

        analyse(gesture_name, analyse_data, model_param)


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


    def button_refresh_connections(self) -> None:
        self.connection_list.clear()
        self.connection_list.addItems(connected_ports())


    def keyPressEvent(self, event):
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

