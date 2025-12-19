
# talk/__init__.py

#- Imports -----------------------------------------------------------------------------------------

from .talk import Talk
from .utils import all_ports, BAUDRATES


#- Export ------------------------------------------------------------------------------------------

__all__ = [
    "Talk",
    "all_ports",
    "BAUDRATES",
]

