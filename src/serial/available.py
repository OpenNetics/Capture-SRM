
# serial/available.py

#- Imports -----------------------------------------------------------------------------------------

from typing import List


#- Declarations ------------------------------------------------------------------------------------

def baud_rates() -> List[str]:
    return [
        "1200", "2400", "4800", "9600",
        "14400", "19200", "38400", "57600",
        "115200", "230400", "250000", "500000",
    ]


def connected_ports() -> List[str]:
    Result = [ "/dev/cu.usbmodem54E20", "/dev/cu.usbmodem54E21", "/dev/cu.usbmodem54E22" ]
    return Result

