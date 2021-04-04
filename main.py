import logging
import os
import sys
from functools import partial

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from constants.path import CONFIG_JSON
from constants.ui import GITHUB_REPO_URL
from utils.exporter import export_wavefront_obj
from utils.files import extract_svo, unpack_dat
from utils.helpers import (
    create_config_json,
    get_path,
    set_dat_path,
    set_hyoutatools_path,
    set_obj_path,
    set_spm_spv_path,
    set_svo_path,
    set_txm_txm_path,
)
from utils.log import OutLog
from utils.textures import extract_textures
from viewer.obj_viewer import show_viewer

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.build_ui()
        self.build_ui_hyouta()
        self.build_ui_txm_txv_path()
        self.build_ui_extract_textures()
        self.build_ui_dat_path()
        self.build_ui_unpack_dat()
        self.build_ui_svo_path()
        self.build_ui_extract_svo()
        self.build_ui_spm_spv_path()
        self.build_ui_export_spm_spv()
        self.build_ui_obj_path()
        self.build_ui_obj_viewer()
        self.build_ui_log()
        self.build_ui_repo_url()
        self.populate_lineedit_path()
        self.set_logging()
        self.show()

    def build_ui(self):
        self.setWindowTitle("VesperiaTools")
        self.setGeometry(300,300, 500,500)
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

    def build_ui_hyouta(self):
        self.hyouta_layout = QHBoxLayout()
        self.hyouta_label = QLabel("HyoutaToolsCLI.exe Path: ")
        self.hyouta_layout.addWidget(self.hyouta_label)
        self.hyouta_path_lineedit = QLineEdit()
        self.hyouta_layout.addWidget(self.hyouta_path_lineedit)
        self.hyouta_browse_btn = QToolButton()
        self.hyouta_browse_btn.setText("...")
        self.hyouta_browse_btn.clicked.connect(
            partial(
                self.browse_file,
                self.hyouta_path_lineedit,
                "Path to HyoutaToolsCLI.exe",
                "HyoutaToolsCLI.exe (*.exe)",
            )
        )
        self.hyouta_layout.addWidget(self.hyouta_browse_btn)
        self.main_layout.addLayout(self.hyouta_layout)

    def build_ui_txm_txv_path(self):
        self.txm_txv_layout = QHBoxLayout()
        self.txm_txv_label = QLabel("TXM/TXV Path: ")
        self.txm_txv_layout.addWidget(self.txm_txv_label)
        self.txm_txv_path_lineedit = QLineEdit()
        self.txm_txv_path_lineedit.setToolTip(
            "The TXM/TXV path must contains both TXM and TXV files "
            "of the same name."
            "\n\n"
            "E.g.: CAPTEX.TXM and CAPTEX.TXV"
        )
        self.txm_txv_layout.addWidget(self.txm_txv_path_lineedit)
        self.txm_txv_browser_btn = QToolButton()
        self.txm_txv_browser_btn.setText("...")
        self.txm_txv_browser_btn.clicked.connect(
            partial(
                self.browse_folder,
                self.txm_txv_path_lineedit,
                "Path to TXM/TXV files",
            )
        )
        self.txm_txv_layout.addWidget(self.txm_txv_browser_btn)
        self.main_layout.addLayout(self.txm_txv_layout)

    def build_ui_extract_textures(self):
        self.extract_textures_layout = QHBoxLayout()
        self.extract_textures_btn = QPushButton(" Extract Textures from TXM/TXV ")
        self.extract_textures_btn.clicked.connect(self.run_extract_textures)
        self.extract_textures_layout.addStretch(0)
        self.extract_textures_layout.addWidget(self.extract_textures_btn)
        self.main_layout.addLayout(self.extract_textures_layout)

    def build_ui_dat_path(self):
        self.dat_path_layout = QHBoxLayout()
        self.dat_path_label = QLabel("DAT Path: ")
        self.dat_path_layout.addWidget(self.dat_path_label)
        self.dat_path_lineedit = QLineEdit()
        self.dat_path_layout.addWidget(self.dat_path_lineedit)
        self.dat_path_browse_btn = QToolButton()
        self.dat_path_browse_btn.setText("...")
        self.dat_path_browse_btn.clicked.connect(
            partial(
                self.browse_file,
                self.dat_path_lineedit,
                "Path to DAT files",
                "DAT Files (*.dat)",
            )
        )
        self.dat_path_layout.addWidget(self.dat_path_browse_btn)
        self.main_layout.addLayout(self.dat_path_layout)

    def build_ui_unpack_dat(self):
        self.unpack_dat_layout = QHBoxLayout()
        self.unpack_dat_deep_checkbox = QCheckBox("Deep Extract")
        self.unpack_dat_deep_checkbox.setToolTip(
            'Handle assets like CH which unpacked as "0000", "0001" and so on'
        )
        self.unpack_dat_btn = QPushButton("Unpack DAT")
        self.unpack_dat_btn.clicked.connect(self.run_unpack_dat)
        self.unpack_dat_layout.addStretch(0)
        self.unpack_dat_layout.addWidget(self.unpack_dat_deep_checkbox)
        self.unpack_dat_layout.addWidget(self.unpack_dat_btn)
        self.main_layout.addLayout(self.unpack_dat_layout)

    def build_ui_svo_path(self):
        self.svo_path_layout = QHBoxLayout()
        self.svo_path_label = QLabel("SVO Path: ")
        self.svo_path_layout.addWidget(self.svo_path_label)
        self.svo_path_lineedit = QLineEdit()
        self.svo_path_layout.addWidget(self.svo_path_lineedit)
        self.svo_path_browse_btn = QToolButton()
        self.svo_path_browse_btn.setText("...")
        self.svo_path_browse_btn.clicked.connect(
            partial(
                self.browse_file,
                self.svo_path_lineedit,
                "Path to SVO files",
                "SVO Files (*.svo)",
            )
        )
        self.svo_path_layout.addWidget(self.svo_path_browse_btn)
        self.main_layout.addLayout(self.svo_path_layout)

    def build_ui_extract_svo(self):
        self.extract_svo_layout = QHBoxLayout()
        self.extract_svo_btn = QPushButton("Extract SVO")
        self.extract_svo_btn.clicked.connect(self.run_extract_svo)
        self.extract_svo_layout.addStretch(0)
        self.extract_svo_layout.addWidget(self.extract_svo_btn)
        self.main_layout.addLayout(self.extract_svo_layout)

    def build_ui_spm_spv_path(self):
        self.spm_spv_path_layout = QHBoxLayout()
        self.spm_spv_path_label = QLabel("SPM/SPV Path: ")
        self.spm_spv_path_layout.addWidget(self.spm_spv_path_label)
        self.spm_spv_path_lineedit = QLineEdit()
        self.spm_spv_path_layout.addWidget(self.spm_spv_path_lineedit)
        self.spm_spv_path_browse_btn = QToolButton()
        self.spm_spv_path_browse_btn.setText("...")
        self.spm_spv_path_browse_btn.clicked.connect(
            partial(
                self.browse_file,
                self.spm_spv_path_lineedit,
                "Path to SPM files",
                "SPM/SPV Files (*.spm *.spv)",
            )
        )
        self.spm_spv_path_layout.addWidget(self.spm_spv_path_browse_btn)
        self.main_layout.addLayout(self.spm_spv_path_layout)

    def build_ui_export_spm_spv(self):
        self.export_spm_spv_layout = QHBoxLayout()
        self.export_spm_spv_btn = QPushButton(" Export SPM/SPV as Wavefront OBJ ")
        self.export_spm_spv_btn.clicked.connect(self.run_export_spm_spv)
        self.export_spm_spv_layout.addStretch(0)
        self.export_spm_spv_layout.addWidget(self.export_spm_spv_btn)
        self.main_layout.addLayout(self.export_spm_spv_layout)

    def build_ui_obj_path(self):
        self.obj_path_layout = QHBoxLayout()
        self.obj_path_label = QLabel("OBJ Path: ")
        self.obj_path_layout.addWidget(self.obj_path_label)
        self.obj_path_lineedit = QLineEdit()
        self.obj_path_layout.addWidget(self.obj_path_lineedit)
        self.obj_path_browse_btn = QToolButton()
        self.obj_path_browse_btn.setText("...")
        self.obj_path_browse_btn.clicked.connect(
            partial(
                self.browse_file,
                self.obj_path_lineedit,
                "Path to OBJ files",
                "OBJ Files (*.obj)",
            )
        )
        self.obj_path_layout.addWidget(self.obj_path_browse_btn)
        self.main_layout.addLayout(self.obj_path_layout)

    def build_ui_obj_viewer(self):
        self.obj_viewer_layout = QHBoxLayout()
        self.obj_viewer_btn = QPushButton(" View Wavefront OBJ ")
        self.obj_viewer_btn.clicked.connect(self.run_obj_viewer)
        self.obj_viewer_layout.addStretch(0)
        self.obj_viewer_layout.addWidget(self.obj_viewer_btn)
        self.main_layout.addLayout(self.obj_viewer_layout)

    def build_ui_log(self):
        self.log_label = QLabel("Output log:")
        self.main_layout.addWidget(self.log_label)
        self.log = QPlainTextEdit()
        self.main_layout.addWidget(self.log)

    def build_ui_repo_url(self):
        self.repo_url_label = QLabel()
        self.repo_url_label.setText(
            f"<a href='{GITHUB_REPO_URL}'>{GITHUB_REPO_URL}</a>"
        )
        self.repo_url_label.setOpenExternalLinks(True)
        self.repo_url_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.repo_url_label)

    def populate_lineedit_path(self):
        if os.path.exists(CONFIG_JSON):
            self.hyouta_path_lineedit.setText(get_path("hyoutatools_path"))
            self.txm_txv_path_lineedit.setText(get_path("txm_txv_path"))
            self.dat_path_lineedit.setText(get_path("dat_path"))
            self.svo_path_lineedit.setText(get_path("svo_path"))
            self.spm_spv_path_lineedit.setText(get_path("spm_spv_path"))
            self.obj_path_lineedit.setText(get_path("obj_path"))
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
        existing_path = lineedit.text() if lineedit.text() else os.path.expanduser("~")
        file_path = QFileDialog.getOpenFileName(
            self,
            title,
            existing_path,
            filter=filter,
        )
        if file_path[0]:
            lineedit.setText(os.path.normpath(file_path[0]))

    def browse_folder(
            self,
            lineedit: QLineEdit,
            title: str = None,
    ):
        if not title:
            title = "Select Folder"
        folder_path = QFileDialog.getExistingDirectory(self, title)
        if folder_path:
            lineedit.setText(os.path.normpath(folder_path))

    def run_extract_textures(self):
        if not self.hyouta_path_lineedit.text() or not self.txm_txv_path_lineedit.text():
            QMessageBox.warning(
                self,
                "Warning",
                "Ensure both HyoutaToolsCLI.exe and TXV/TXV paths are selected before extracting!",
            )
            return
        self.update_config_json()
        extract_textures(self.txm_txv_path_lineedit.text())

    def run_unpack_dat(self):
        if not self.hyouta_path_lineedit.text() or not self.dat_path_lineedit.text():
            QMessageBox.warning(
                self,
                "Warning",
                "Ensure both HyoutaToolsCLI.exe and DAT paths are selected before extracting!",
            )
            return
        self.update_config_json()
        unpack_dat(
            self.dat_path_lineedit.text(),
            deep_extract=self.unpack_dat_deep_checkbox.isChecked(),
        )

    def run_extract_svo(self):
        if not self.hyouta_path_lineedit.text() or not self.svo_path_lineedit.text():
            QMessageBox.warning(
                self,
                "Warning",
                "Ensure both HyoutaToolsCLI.exe and SVO paths are selected before extracting!",
            )
            return
        self.update_config_json()
        extract_svo(self.svo_path_lineedit.text())

    def run_export_spm_spv(self):
        spm_spv_path = self.spm_spv_path_lineedit.text()
        if not spm_spv_path:
            QMessageBox.warning(
                self,
                "Warning",
                "Please specify SPM/SPV path before exporting!",
            )
            return
        self.update_config_json()
        output_path, _ = os.path.split(spm_spv_path)
        export_wavefront_obj(spm_spv_path, output_path)

    def run_obj_viewer(self):
        obj_path = self.obj_path_lineedit.text()
        if not obj_path:
            QMessageBox.warning(
                self,
                "Warning",
                "Please specify OBJ path before viewing!",
            )
            return
        self.update_config_json()
        show_viewer(obj_path)

    def update_config_json(self):
        set_hyoutatools_path(self.hyouta_path_lineedit.text())
        set_txm_txm_path(self.txm_txv_path_lineedit.text())
        set_dat_path(self.dat_path_lineedit.text())
        set_svo_path(self.svo_path_lineedit.text())
        set_spm_spv_path(self.spm_spv_path_lineedit.text())
        set_obj_path(self.obj_path_lineedit.text())

    def closeEvent(self, event):
        self.update_config_json()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
