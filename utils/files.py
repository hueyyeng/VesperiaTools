"""Vesperia Tools Files."""
import logging
import os
from pathlib import Path

from constants import tales
from exceptions.files import (
    InvalidFileException,
    InvalidFourCCException,
)

logger = logging.getLogger(__name__)
log_handler = logging.FileHandler("vesperia_tools_debug.log")
log_handler.setLevel(logging.DEBUG)
logger.addHandler(log_handler)


def get_fourcc(file_path: str):
    """Get FourCC code of a file

    Parameters
    ----------
    file_path : str
        Path to file

    Returns
    -------
    str
        The decoded FourCC value

    """
    if not os.path.isfile(file_path):
        raise InvalidFileException(file_path)
    with open(file_path, "rb") as f:
        file_header = f.read(32)
    file_fourcc = file_header[:4]
    return file_fourcc.decode("utf-8")


def check_fourcc(fourcc: str, file_path: str):
    """Check FourCC code of a file

    Parameters
    ----------
    fourcc : str
        The expected FourCC value
    file_path : str
        Path to file

    """
    if not os.path.isfile(file_path):
        raise InvalidFileException(file_path)
    with open(file_path, "rb") as f:
        file_header = f.read(32)
    file_fourcc = file_header[:4].decode("utf-8")

    # Check file's FourCC with expected FourCC in bytes representation
    if file_fourcc != fourcc:
        logger.warning({
            "msg": f"Not an {fourcc} file!",
            "fourcc": str(file_fourcc),
            "file_header": str(file_header),
        })
        raise InvalidFourCCException(fourcc, file_fourcc)


def rename_unknown_files_ext(dir_path: str):
    """Rename Unknown Files Extension

    Parameters
    ----------
    dir_path : str

    """
    for file_path in Path(dir_path).rglob("*"):
        if file_path.is_file() and file_path.suffix:
            with file_path.open("rb") as f:
                file_header = f.read(4).hex()

            # Default to TXV as TXV header has slight variation for 2nd and 3rd bytes
            extension = ".TXV"
            file_header = file_header.upper()
            if file_header in tales.TYPE_2_EXT_PC.keys():
                extension = tales.TYPE_2_EXT_PC[file_header]

            logger.debug({
                "file_path": file_path,
                "extension": extension,
            })
            file_path.rename(file_path.with_suffix(extension))


def cleanup_leftover_files(dir_path, cleanup_files):
    """Cleanup leftover files after decompression

    Parameters
    ----------
    dir_path : str
        Directory path containing the files to be cleanup
    cleanup_files : list or tuple
        List/tuple of file names

    """
    if os.path.splitext(dir_path)[1] == ".dec":
        dir_path = os.path.splitext(dir_path)[0]
    removed_files = []
    files = os.listdir(dir_path)
    for cleanup_file in cleanup_files:
        if cleanup_file in files:
            removed_files.append(cleanup_file)
            file_path = os.path.join(dir_path, cleanup_file)
            logger.debug({
                "msg": "Removing unpacked file",
                "file_path": file_path,
            })
            os.remove(file_path)
    logger.info({
        "msg": "Done cleanup leftover cleanup_files",
        "cleanup_files": removed_files,
    })
