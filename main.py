import logging
import os
import sys
from functools import partial

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from constants.ui import GITHUB_REPO_URL
from constants.path import CONFIG_JSON
from utils.helpers import (
    create_config_json,
    get_hyoutatools_path,
    set_hyoutatools_path,
    get_txm_txv_path,
    set_txm_txm_path,
)
from utils.log import OutLog
from utils.textures import extract_textures

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.build_ui()
        self.populate_lineedit_path()
        self.set_logging()

    def build_ui(self):
        self.setWindowTitle("VesperiaTools")
        self.setGeometry(300,300, 500,500)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.hyouta_layout = QHBoxLayout()
        self.hyouta_label = QLabel("HyoutaToolsCLI.exe Path: ")
        self.hyouta_layout.addWidget(self.hyouta_label)
        self.hyouta_lineedit_path = QLineEdit()
        self.hyouta_layout.addWidget(self.hyouta_lineedit_path)
        self.hyouta_browse_btn = QToolButton()
        self.hyouta_browse_btn.setText("...")
        self.hyouta_browse_btn.clicked.connect(
            partial(
                self.browse_file,
                self.hyouta_lineedit_path,
                "Path to HyoutaToolsCLI.exe",
                "HyoutaToolsCLI.exe (*.exe)",
            )
        )
        self.hyouta_layout.addWidget(self.hyouta_browse_btn)
        self.main_layout.addLayout(self.hyouta_layout)

        self.txm_txv_layout = QHBoxLayout()
        self.txm_txv_label = QLabel("TXM/TXV Path: ")
        self.txm_txv_layout.addWidget(self.txm_txv_label)
        self.txm_txv_lineedit_path = QLineEdit()
        self.txm_txv_layout.addWidget(self.txm_txv_lineedit_path)
        self.txm_txv_browser_btn = QToolButton()
        self.txm_txv_browser_btn.setText("...")
        self.txm_txv_browser_btn.clicked.connect(
            partial(
                self.browse_folder,
                self.txm_txv_lineedit_path,
                "Path to TXM/TXV files",
            )
        )
        self.txm_txv_layout.addWidget(self.txm_txv_browser_btn)
        self.main_layout.addLayout(self.txm_txv_layout)

        self.extract_textures_btn = QPushButton("Extract Textures from TXM/TXV")
        self.extract_textures_btn.clicked.connect(self.run_extract_textures)
        self.main_layout.addWidget(self.extract_textures_btn)

        self.log_label = QLabel("Output log:")
        self.main_layout.addWidget(self.log_label)
        self.log = QPlainTextEdit()
        self.main_layout.addWidget(self.log)

        self.repo_url_label = QLabel()
        self.repo_url_label.setText(
            f"<a href='{GITHUB_REPO_URL}'>{GITHUB_REPO_URL}</a>"
        )
        self.repo_url_label.setOpenExternalLinks(True)
        self.repo_url_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.repo_url_label)

        # self.main_layout.addStretch(1)
        self.show()


    def populate_lineedit_path(self):
        if os.path.exists(CONFIG_JSON):
            self.hyouta_lineedit_path.setText(get_hyoutatools_path())
            self.txm_txv_lineedit_path.setText(get_txm_txv_path())
        else:
            create_config_json()

    def set_logging(self):
        sys.stdout = OutLog(self.log, sys.stdout)
        sys.stderr = OutLog(self.log, sys.stderr, QColor(255, 0, 0))
        formatter = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=formatter)

    def browse_file(
            self,
            lineedit: QLineEdit,
            title: str = None,
            filter: str = None,
    ):
        if not title:
            title = "Select File"
        if not filter:
            filter = "All Files (*)"
        file_path = QFileDialog.getOpenFileName(self, title, filter=filter)
        if file_path[0]:
            lineedit.setText(file_path[0])

    def browse_folder(
            self,
            lineedit: QLineEdit,
            title: str = None,
    ):
        if not title:
            title = "Select Folder"
        folder_path = QFileDialog.getExistingDirectory(self, title)
        if folder_path:
            lineedit.setText(folder_path)

    def run_extract_textures(self):
        if not self.hyouta_lineedit_path.text() or not self.txm_txv_lineedit_path.text():
            QMessageBox.warning(
                self,
                "Warning",
                "Ensure both paths are selected before extracting!",
            )
            return
        set_hyoutatools_path(self.hyouta_lineedit_path.text())
        set_txm_txm_path(self.txm_txv_lineedit_path.text())
        extract_textures(self.txm_txv_lineedit_path.text())


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
