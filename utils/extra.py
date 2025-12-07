
# utils/extra.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Tuple


#- Lib ---------------------------------------------------------------------------------------------

# Return a random RGB color tuple used for new graph lines.
def new_color() -> Tuple[int, int, int]:
    from random import randint
    return (randint(0, 255), randint(60, 255), randint(0, 200))


# Return filepath for filename
def file_name_path(file: str) -> str:
    import os
    if not os.path.splitext(file)[1]: file += ".ges"
    if os.path.isabs(file): return file
    return os.path.expanduser("~") + "/" + file


# Return month-date-24time
def datestring() -> str:
    from datetime import datetime
    now = datetime.now()
    return now.strftime(f"%m-%d-%H%M")

