
# window/style.py


BACKGROUND_COLOR: str = "#101e15"

APPLICATION_NAME: str = "Gesture Tracker v0.0.1"

WINDOW_SIZE: dict = {
    "width": 1200,
    "height": 800
}

GRAPH_HEIGHT: int = 250

BUTTON_STYLE: str = """
    QPushButton {
        background-color: #112719;
        border: 2px solid #0b1e14;
        border-radius: 5px;
        padding: 5% 10%;
        color: #7d8b94;
    }
    QPushButton:pressed {
        background-color: black;
    }
"""

RAW_VALUE_BOX_STYLE: str = "background-color: #121212; color: #7d8b94;"

