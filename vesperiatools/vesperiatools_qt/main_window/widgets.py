from PySide6.QtGui import *

from vesperiatools.vesperiatools_qt.toolbars import (
    HorizontalToolBar,
    VerticalToolBar,
)


class Sidebar(VerticalToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setFixedWidth(180)


class CentralWidget(HorizontalToolBar):
    def __init__(self, parent=None):
        super().__init__(parent)
