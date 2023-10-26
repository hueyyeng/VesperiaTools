from PySide6.QtCore import Signal, QSettings, QByteArray
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QDialog

from vesperiatools import settings


class Dialog(QDialog):
    """Custom Dialog that remembers... size and position"""

    visibility = Signal(bool)

    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.settings = QSettings(
            settings.VT,
            self.__class__.__name__,
        )

    def hide(self):
        self.visibility.emit(False)
        self.save_position()
        super().hide()

    def show(self):
        self.visibility.emit(True)
        self.load_position()
        super().show()

    def closeEvent(self, event: QCloseEvent):
        self.visibility.emit(False)
        self.save_position()
        event.accept()

    def load_position(self):
        geometry: QByteArray = self.settings.value("geometry")
        position: QByteArray = self.settings.value("position")

        if geometry:
            self.restoreGeometry(geometry)
        if position:
            self.move(position)

    def save_position(self):
        geometry = self.saveGeometry()
        position = self.pos()

        self.settings.setValue("geometry", geometry)
        self.settings.setValue("position", position)