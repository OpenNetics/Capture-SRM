
# talk/__init__.py

#- Imports -----------------------------------------------------------------------------------------

from .read import select_baud_rate, select_port
from .available import connected_ports, baud_rates


#- Export ------------------------------------------------------------------------------------------

__version__: str = "0.1.0"
__all__ = [
    "select_baud_rate", "select_port",
    "connected_ports", "baud_rates",
]

