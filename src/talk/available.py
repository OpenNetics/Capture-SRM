
# talk/available.py

#- Imports -----------------------------------------------------------------------------------------

import serial.tools.list_ports



#- Declarations ------------------------------------------------------------------------------------

def baud_rates() -> list[str]:
    return [
        "1200", "2400", "4800", "9600",
        "14400", "19200", "38400", "57600",
        "115200", "230400", "250000", "500000",
    ]


def connected_ports() -> list[str]:
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

