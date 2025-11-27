
# utils/extra.py

#- Imports -----------------------------------------------------------------------------------------

from typing import Optional, Tuple


#- Lib ---------------------------------------------------------------------------------------------

# Return a random RGB color tuple used for new graph lines.
def new_color() -> Tuple[int, int, int]:
    from random import randint
    return (randint(0, 255), randint(60, 255), randint(0, 200))


# Print error on screen with more description.
def print_alert(status: str, message: str) -> None:
    import inspect
    import sys
    import os

    from colorama import init, Fore
    init()

    # Immediate caller frame (0 is this function, 1 is the alert_box, 2 is the caller needed).
    stack = inspect.stack()
    if len(stack) > 2:
        caller = stack[2]
        caller_file = os.path.abspath(caller.filename)
        caller_line = caller.lineno

        # Attempt to find the project root by looking for common repo/project markers.
        def _find_project_root(start_path: str) -> Optional[str]:
            cur = os.path.dirname(start_path)

            while True:
                candidate = os.path.join(cur, "main.py")
                if os.path.exists(candidate):
                    return cur

                parent = os.path.dirname(cur)
                if parent == cur:
                    return None

                cur = parent

        project_root = _find_project_root(caller_file)

        if project_root:
            rel_path = os.path.relpath(caller_file, project_root)
        else:
            # fallback to current working directory if no project root found
            try:
                rel_path = os.path.relpath(caller_file, os.getcwd())
            except Exception:
                rel_path = caller_file

        caller_info = Fore.YELLOW + f"./{rel_path}:{caller_line}" + Fore.RESET
    else:
        caller_info = Fore.YELLOW + "<unknown>" + Fore.RESET

    print(Fore.RED + f"[{status}] {caller_info} {message}", file=sys.stderr)

