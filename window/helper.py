
# window/helper.py

#- Imports -----------------------------------------------------------------------------------------

from random import randint

from PySide6.QtWidgets import (
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)

from .style import BUTTON_STYLE


#- Lib ---------------------------------------------------------------------------------------------

def new_color() -> ( int, int, int ):
    return ( randint( 0, 255 ), randint( 60, 255 ), randint( 0, 200 ) )


def spaced_element() -> QSpacerItem:
    return QSpacerItem( 20, 20, QSizePolicy.Expanding, QSizePolicy.Preferred )


#- Class Helper ------------------------------------------------------------------------------------

def create_button( self, text: str, callback: callable ) -> QPushButton:
    button = QPushButton( text )
    button.setStyleSheet( BUTTON_STYLE )
    button.clicked.connect( callback )
    return button

