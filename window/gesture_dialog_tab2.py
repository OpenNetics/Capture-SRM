
# window/gesture_dialog.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Callable, List, Optional, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog, QWidget,
    QComboBox, QFileDialog, QLabel, QLineEdit,
    QLayout, QVBoxLayout, QHBoxLayout,
    QSizePolicy,
)

from utils.style import (
    TEXT_HEAD, TEXT_BODY,
    COMBOBOX_STYLE,
)
from utils.typedefs import(
    TAB2,
    GestureUpdater,
)
from utils.ui import (
    spacedv, blank_line,
    create_button, labelled_text_widget,
)
from analyse import read_gesture


#- Tab Class ---------------------------------------------------------------------------------------

class Tab2:

    def __init__(
            self,
            parent: QDialog,
            parent_layout: QWidget,
            input_names: List[str],
            submit: Callable[[int], None]
        ) -> None:

        self.parent = parent
        self.submit: Callable[[int], None] = submit
        self.input_names: List[str] = input_names

        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setContentsMargins(10, 10, 10, 10)
        parent_layout.setLayout(self.layout)

        self.init_filename() # add file selection on main layout

        self.body_layout = QVBoxLayout() # layout for dynamic content
        self.layout.addLayout(self.body_layout)

        self.init_buttons()  # add buttons on main layout

    #- Init Modules --------------------------------------------------------------------------------

    def init_filename(self) -> None:
        # Gesture Name
        file_name_layout = QHBoxLayout()

        self.gesture_file = QLineEdit(self.parent)
        self.gesture_file.setPlaceholderText("Gesture Path")
        self.gesture_file.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        file_name_layout.addWidget(self.gesture_file, 1)

        browse_button = create_button("Browse", self.init_input_filepath)
        browse_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        file_name_layout.addWidget(browse_button, 0)

        self.layout.addLayout(file_name_layout)

        load_data = create_button("Load File Data", self.init_source_list)
        self.layout.addWidget(load_data)


    def init_input_filepath(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent, "Open Gesture File", "", "Gesture Files (*.ges);;All Files (*)",
            options=QFileDialog.Options()
        )
        if not file_path: return

        self.gesture_file.setText(file_path)


    def init_buttons(self) -> None:
        blank_line(self.layout)
        spacedv(self.layout)
        button_layout = QHBoxLayout()

        self.cancel_button = create_button("Cancel", self.parent.reject)
        self.continue_button = create_button("Continue", self.finish)

        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.continue_button)

        self.layout.addLayout(button_layout)


    def init_source_list(self) -> None:
        gesture_data = read_gesture(self.gesture_file.text())
        if gesture_data is None: return

        # clear previous body layout
        while self.body_layout.count():
            item: QLayout = self.body_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()

        blank_line(self.body_layout)
        label = QLabel("Available Sources:")
        label.setStyleSheet(TEXT_HEAD)
        self.body_layout.addWidget(label)

        self.drop_boxes: List[QComboBox] = []

        for model in gesture_data.models.keys():
            label_holder: QHBoxLayout = QHBoxLayout()

            text_label = QLabel(model)
            text_label.setStyleSheet(TEXT_BODY)
            text_label.setFixedWidth(100)
            label_holder.addWidget(text_label)

            input_name_list = QComboBox()
            input_name_list.addItems(["<UNCHANGED>"] + self.input_names)
            input_name_list.setStyleSheet(COMBOBOX_STYLE)
            self.drop_boxes.append(input_name_list)
            label_holder.addWidget(input_name_list)

            self.body_layout.addLayout(label_holder)

        blank_line(self.body_layout)
        threshold_label = str(gesture_data.threshold) if (
            gesture_data.threshold is not None ) else "None Saved"

        self.threshold_label = labelled_text_widget(
            "Threshold", threshold_label, threshold_label, self.body_layout)

        spacedv(self.body_layout)


    #- Getters and Actions -------------------------------------------------------------------------

    def get_inputs(self) -> Optional[GestureUpdater]:
        return self.values if hasattr(self, 'values') else None


    def finish(self) -> None:
        self.values: GestureUpdater

        self.submit(TAB2)

    #- Key Events ----------------------------------------------------------------------------------

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() in [Qt.Key_Return, Qt.Key_Enter]:
            self.continue_button.click()
        elif event.key() == Qt.Key_Escape:
            self.cancel_button.click()
        else:
            super().keyPressEvent(event)

