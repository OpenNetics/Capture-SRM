
# serial/__init__.py

__version__: str = "0.1.0"

from .read import select_baud_rate, select_port
from .available import connected_ports, baud_rates

