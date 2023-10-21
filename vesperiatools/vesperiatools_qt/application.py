from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from vesperiatools.vesperiatools_qt.main_window import MainWindow
from vesperiatools import settings


class Application(QApplication):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setApplicationName(settings.APP_NAME)
        self.setApplicationDisplayName(settings.APP_NAME)
        self.setApplicationVersion(settings.APP_VERSION)

        self.setWindowIcon(QIcon("icon.png"))

        self.main_window = MainWindow()
        self.main_window.show()

    def notify(self, receiver: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.KeyPress:
            key_event = QKeyEvent(event)
            if key_event.key() == Qt.Key.Key_F2 and self.main_window:
                self.main_window.toggle_theme()
                return True

        if isinstance(receiver, QWidgetItem):
            return False

        return super().notify(receiver, event)
