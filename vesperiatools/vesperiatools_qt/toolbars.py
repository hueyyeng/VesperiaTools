from PySide6.QtWidgets import *


class HorizontalToolBar(QWidget):
    width_margin = 0
    height_margin = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        self.setLayout(layout)
        self.useDefaultMargins()

    def layout(self) -> QHBoxLayout:
        return super().layout()

    def addWidget(self, w: QWidget):
        self.layout().addWidget(w)

    def addStretch(self):
        self.layout().addStretch()

    def useNoMargins(self):
        self.layout().setContentsMargins(0, 0, 0, 0)

    def useDefaultMargins(self):
        self.layout().setContentsMargins(
            self.width_margin,
            self.height_margin,
            self.width_margin,
            self.height_margin,
        )


class VerticalToolBar(QWidget):
    width_margin = 6
    height_margin = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.useDefaultMargins()

    def layout(self) -> QVBoxLayout:
        return super().layout()

    def addWidget(self, w: QWidget):
        self.layout().addWidget(w)

    def addStretch(self):
        self.layout().addStretch()

    def useNoMargins(self):
        self.layout().setContentsMargins(0, 0, 0, 0)

    def useDefaultMargins(self):
        self.layout().setContentsMargins(
            self.width_margin,
            self.height_margin,
            self.width_margin,
            self.height_margin,
        )
