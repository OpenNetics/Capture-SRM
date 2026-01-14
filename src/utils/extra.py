
# utils/extra.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Any


#- Lib ---------------------------------------------------------------------------------------------

global_color_counter = -1
COLORS_LUT: list[str] = [
    "#fa2077",
    "#7463f3",
    "#ff69b4",
    "#c61b2a",
    "#fdfd20",
    "#5d8aa8",
    "#ff2800",
    "#98ff98",
    "#007aa5",
    "#870606",
    "#f8f8ff",
    "#ff00ff",
    "#f8ba8b",
    "#7F2169",
    "#0069d1",
    "#78f0f0",
    "#a56423",
    "#3f00ff",
]


# Return a random RGB color tuple used for new graph lines.
def new_color() -> str:
    global global_color_counter
    if global_color_counter < len(COLORS_LUT) - 1:
        global_color_counter += 1
        return COLORS_LUT[global_color_counter]

    from random import randint

    r = randint(0, 255)
    g = randint(60, 255)
    b = randint(0, 200)

    return f"#{r:02X}{g:02X}{b:02X}"


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

