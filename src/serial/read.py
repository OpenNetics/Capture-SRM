
# serial/read.py

#- Global Variables --------------------------------------------------------------------------------

SelectedPort = ""
BaudRate = ""


#- Declarations ------------------------------------------------------------------------------------

def select_port(port: str) -> None:
    global SelectedPort
    SelectedPort = port


def select_baud_rate(baud: str) -> None:
    global BaudRate
    BaudRate = baud


def port() -> str:
    print(f"Selected Port: {SelectedPort}")
    return SelectedPort


def baud_rate() -> str:
    print(f"Selected Baud Rate: {BaudRate}")
    return BaudRate

