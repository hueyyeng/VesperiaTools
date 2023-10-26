from PySide6.QtWidgets import QFileDialog, QWidget


def browse_file(parent: QWidget, name_filter: str = None) -> str | None:
    title = "Select File"
    if not name_filter:
        name_filter = "All Files (*)"

    file_path = QFileDialog.getOpenFileName(
        parent,
        title,
        filter=name_filter,
    )
    if not file_path:
        return None

    return file_path[0]


def browse_folder(parent: QWidget) -> str | None:
    title = "Select Folder"
    folder_path = QFileDialog.getExistingDirectory(
        parent,
        title,
    )
    return folder_path
