import logging

from PySide6.QtGui import QAction, QActionGroup
from PySide6.QtWidgets import QMenu, QMenuBar

from vesperiatools.vesperiatools_qt import main_window


class LogLevelAction(QAction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setCheckable(True)


class SetLogLevelMenu(QMenu):
    def __init__(self, parent: "main_window.MainWindow"):
        super().__init__(parent)
        self.parent_ = parent
        self.setTitle("&Set Level")

        self.debug_action = LogLevelAction("&Debug", self)
        self.debug_action.setData(logging.DEBUG)
        self.debug_action.triggered.connect(self._set_log_level)

        self.info_action = LogLevelAction("&Info", self)
        self.info_action.setData(logging.INFO)
        self.info_action.triggered.connect(self._set_log_level)

        self.warning_action = LogLevelAction("&Warning", self)
        self.warning_action.setData(logging.WARNING)
        self.warning_action.triggered.connect(self._set_log_level)

        self.addAction(self.debug_action)
        self.addAction(self.info_action)
        self.addAction(self.warning_action)

        group = QActionGroup(parent)
        group.setExclusive(True)
        group.addAction(self.debug_action)
        group.addAction(self.info_action)
        group.addAction(self.warning_action)

        self.info_action.setChecked(True)

    def _set_log_level(self):
        sender: QAction = self.sender()
        sender.setChecked(True)
        self.parent_.set_log_level(sender.data())


class LogMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("&Log")
        self.set_level_menu = SetLogLevelMenu(parent)
        self.addMenu(self.set_level_menu)


class MainMenuBar(QMenuBar):
    def __init__(self, parent: "main_window.MainWindow"):
        super().__init__(parent)
        self.parent_ = parent

        self.file_menu = QMenu("&File")
        self.addMenu(self.file_menu)

        self.exit_action = QAction("E&xit")
        self.file_menu.addAction(self.exit_action)
        self.exit_action.triggered.connect(self.parent_.close)

        self.log_menu = LogMenu(parent)
        self.addMenu(self.log_menu)
