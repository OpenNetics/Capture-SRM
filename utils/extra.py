
# utils/extra.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Tuple


#- Lib ---------------------------------------------------------------------------------------------

# Return a random RGB color tuple used for new graph lines.
def new_color() -> Tuple[int, int, int]:
    from random import randint
    return (randint(0, 255), randint(60, 255), randint(0, 200))

