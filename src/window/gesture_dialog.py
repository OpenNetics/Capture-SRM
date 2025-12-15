
# window/gesture_dialog.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QWidget, QTabWidget,
    QVBoxLayout,
)

from utils.style import BACKGROUND_COLOR
from utils.typing import GestureInput, Tab

from .gesture_dialog_tab1 import Tab1
from .gesture_dialog_tab2 import Tab2
from .gesture_dialog_tab3 import Tab3


#- Window Class ------------------------------------------------------------------------------------

# Modal dialog to choose between recording a new gesture or updating an existing one.
class GestureDialog(QDialog):

    # Build dialog tabs and store inputs; submit() will accept the dialog with chosen tab.
    def __init__(self, input_names: Tuple[str, ...]) -> None:
        super().__init__()

        self.setWindowTitle("Record Gestures")
        self.resize(750, 250)
        self.setStyleSheet(f"background-color: {BACKGROUND_COLOR};")

        self.layout = QVBoxLayout(self)
        tab_widget = QTabWidget(self)
        tab_widget.setStyleSheet("QTabWidget::pane { border: none; }")

        self.final_tab: Tab = Tab.NONE

        # Record Tab
        t1 = QWidget()
        tab_widget.addTab(t1, "Record")
        self.tab1 = Tab1(self, t1, input_names, self._submit, self.reject)

        # Update Tab
        t2 = QWidget()
        tab_widget.addTab(t2, "Update")
        self.tab2 = Tab2(self, t2, input_names, self._submit, self.reject)

        # Test Tab
        t3 = QWidget()
        tab_widget.addTab(t3, "Test")
        self.tab3 = Tab3(self, t3, input_names, self._submit, self.reject)

        self.layout.addWidget(tab_widget)


    # Return inputs from the selected tab, or None if no valid inputs were produced.
    def get_inputs(self) -> Optional[Tuple[Tab, GestureInput]]:
        if self.final_tab == Tab.CREATE:
            result = self.tab1.get_inputs()
            if result is not None: return (Tab.CREATE, result)

        elif self.final_tab == Tab.UPDATE:
            result = self.tab2.get_inputs()
            if result is not None: return (Tab.UPDATE, result)

        return None


    # Record which tab produced the inputs and accept the dialog to close it.
    def _submit(self, tab: Tab) -> None:
        self.final_tab = tab
        self.accept()

