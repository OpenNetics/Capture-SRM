
# main.py

#- Imports -----------------------------------------------------------------------------------------

import sys
import time

import numpy as np
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal

from window import GestureTracker


#- Declarations ------------------------------------------------------------------------------------

class DataGenerator(QThread):
    data_signal = Signal(list)

    def run(self):
        while True:
            random_values = np.random.uniform(10, 15, 6)
            array = np.round(random_values, 2).tolist()
            self.data_signal.emit(array)
            time.sleep(1)


def main():
    app = QApplication( sys.argv )
    window = GestureTracker()
    window.show()

    data_thread = DataGenerator()
    data_thread.data_signal.connect(window.add_data)
    data_thread.start()

    exit_code = app.exec()
    data_thread.terminate()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

