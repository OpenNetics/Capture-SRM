
# window/labelled_text.py

#- Imports -----------------------------------------------------------------------------------------

from PySide6.QtWidgets import (
    QLabel, QLineEdit,
    QBoxLayout, QHBoxLayout,
)

from utils.style import (
    TEXT_BOX_STYLE, LABEL_BODY_STYLE,
)


#- LabelledText class ------------------------------------------------------------------------------

# Textfield with label next to it.
class LabelledText:

    # Initialise LabelledText with a label and a textbox.
    def __init__(
        self, title: str, value: str, tip: str, parent_layout: QBoxLayout,
        visible: bool = True
    ) -> None:
        layout = QHBoxLayout()

        # label
        self._text_label = QLabel(title)
        self._text_label.setVisible(visible)
        self._text_label.setStyleSheet(LABEL_BODY_STYLE)
        layout.addWidget(self._text_label)

        # text box
        self._text_input = QLineEdit()
        self._text_input.setVisible(visible)
        self._text_input.setPlaceholderText(value)
        self._text_input.setToolTip(tip)
        self._text_input.setText(value)
        self._text_input.setStyleSheet(TEXT_BOX_STYLE)
        layout.addWidget(self._text_input)

        parent_layout.addLayout(layout)


    # Retrieve value of the text box.
    def text(self) -> str: return self._text_input.text()


    # Toggle visibility of the two components.
    def visibility(self, visible: bool) -> None:
        self._text_label.setVisible(visible)
        self._text_input.setVisible(visible)

