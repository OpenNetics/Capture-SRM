
# utils/extra.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any


#- Lib ---------------------------------------------------------------------------------------------

# Return a random RGB color tuple used for new graph lines.
def new_color() -> tuple[int, int, int]:
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


# Return a list for "12,324,34,foo,11,bar" string
def parse_string_list(string: str) -> list[Any]:
    result: list[Any] = []

    for element in string.split(','): # split the string by commas
        try:
            num = float(element) # convert to float first, will handle integers as well
            result.append(num)

        except ValueError:
            result.append(element.strip('"'))

    return result

