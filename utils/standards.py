
# utils/standards.py

from typing import List

def baud_rates() -> List[str]:
    return [
        "1200", "2400", "4800", "9600",
        "14400", "19200", "38400", "57600",
        "115200", "230400", "250000", "500000",
    ]

