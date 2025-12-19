
# talk/talk_signal.py

#- Imports -----------------------------------------------------------------------------------------

from PySide6.QtCore import QObject, Signal


#- TalkSignals Class -------------------------------------------------------------------------------

class TalkSignals(QObject):
    line_received = Signal(str)
    single_received = Signal(str)

