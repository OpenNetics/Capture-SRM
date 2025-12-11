
# window/style.py

#- Imports -----------------------------------------------------------------------------------------

APPLICATION_NAME: str = "Gesture Tracker v0.1.0"


#- Dimensions --------------------------------------------------------------------------------------

WINDOW_SIZE: dict[str,int] = {
    "width": 1200,
    "height": 800
}

GRAPH_HEIGHT: int = 250
SCROLL_HEIGHT:int = 450
ZOOM_SLIDER_WIDTH: int = 150


#- Color Scheme ------------------------------------------------------------------------------------

BACKGROUND_COLOR: str = "#050505"
FONT_COLOR: str = "#c6c6c6"
ACCENT_COLOR: str = "#ff4252"
LABEL_COLOR: str = "#91917e"
BORDER_COLOR: str = "#11211c"
BACKGROUND_HIGHLIGHT_COLOR: str = "#101112"


#- Object Styles -----------------------------------------------------------------------------------

RAW_VALUE_BOX_STYLE: str = f"""
    background-color: {BACKGROUND_HIGHLIGHT_COLOR};
    color: {FONT_COLOR};
    border: 0;
"""

TEXT_BOX_STYLE: str = f"""
    padding: 5% 10%;
    background-color: {BACKGROUND_HIGHLIGHT_COLOR};
    border-radius: 5px;
"""

LABEL_BODY_STYLE: str = f"""
    color: {FONT_COLOR}
"""

LABEL_HEAD_STYLE: str = f"""
    color: {ACCENT_COLOR};
    font-size: 14px;
"""

BUTTON_STYLE: str = f"""
    QPushButton {{
        background-color: {BACKGROUND_COLOR};
        border: 2px solid {BORDER_COLOR};
        border-radius: 15px;
        padding: 5% 10%;
        color: {LABEL_COLOR};
    }}
    QPushButton:hover {{
        background-color: {BORDER_COLOR};
    }}
    QPushButton:pressed {{
        color: white;
        background-color: {ACCENT_COLOR};
    }}
"""

COMBOBOX_STYLE: str = f"""
    QComboBox {{
        background-color: {BACKGROUND_HIGHLIGHT_COLOR};
        border: 2px solid {BORDER_COLOR};
        border-radius: 15px;
        padding: 5% 15%;
        color: {LABEL_COLOR};
    }}
    QComboBox::drop-down {{
        border-left-width: 0;
    }}
    QComboBox::down-arrow:on {{
        top: 0;
        left: 0;
    }}
"""

SCROLL_BAR_STYLE: str = f"""
    QScrollBar:vertical {{
        width: 10px;
    }}
    QScrollBar::handle:vertical {{
        background: {ACCENT_COLOR};
        border-radius: 5px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        background: none; /* hide the arrows */
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none; /* hide the page scroll areas */
    }}
"""

