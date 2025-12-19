#!/usr/bin/env python3
# GestureTracker

#- Imports -----------------------------------------------------------------------------------------

import sys

from PySide6.QtWidgets import QApplication

from window import GestureTracker
from talk import Talk


#- Declarations ------------------------------------------------------------------------------------

if __name__ == "__main__":
    app = QApplication( sys.argv )

    talk = Talk()
    window = GestureTracker(talk)
    window.show()

    exit_code = app.exec()

    sys.exit(exit_code)

