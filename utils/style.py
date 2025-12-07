
# window/style.py

BACKGROUND_COLOR: str = "#101e15"

FONT_COLOR: str = "#7d8b94"

APPLICATION_NAME: str = "Gesture Tracker v0.1.0"

WINDOW_SIZE: dict[str,int] = {
    "width": 1200,
    "height": 800
}

GRAPH_HEIGHT: int = 250

RAW_VALUE_BOX_STYLE: str = f"background-color: #121212; color: {FONT_COLOR};"

TEXT_BODY: str = f"color: {FONT_COLOR}"
TEXT_HEAD: str = f"color: {FONT_COLOR}; font-size: 14px; font-weight: bold;"

BUTTON_STYLE: str = """
    QPushButton {
        background-color: #112719;
        border: 2px solid #0b1e14;
        border-radius: 15px;
        padding: 5% 10%;
        color: #7d8b94;
    }
    QPushButton:pressed {
        background-color: black;
    }
"""

COMBOBOX_STYLE: str = """
    QComboBox {
        background-color: #112719;
        border: 2px solid #0b1e14;
        border-radius: 15px;
        padding: 5% 15%;
        color: #7d8b94;
    }

    QComboBox::drop-down {
        border-left-width: 0;
    }
    QComboBox::down-arrow:on {
        top: 0;
        left: 0;
    }
"""

