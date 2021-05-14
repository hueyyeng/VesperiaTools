"""Vesperia Tools Files."""
import logging
import os
import struct
import subprocess

from constants import tales
from exceptions.files import (
    InvalidFileException,
    InvalidFourCCException,
)
from utils.helpers import get_path

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
    if not isinstance(file_path, str) or not os.path.isfile(file_path):
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
    if not isinstance(file_path, str) or not os.path.isfile(file_path):
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
    file_names = os.listdir(dir_path)
    for file_name in file_names:
        file_path = os.path.join(
            dir_path,
            file_name,
        )

        with open(file_path, "rb") as f:
            file_header = f.read(4).hex()

        file_header = file_header.upper()
        if file_header in tales.TYPE_2_EXT_PC.keys():
            file_path_basename = os.path.splitext(file_path)[0]
            file_path_rename = f"{file_path_basename}{tales.TYPE_2_EXT_PC[file_header]}"
            os.rename(file_path, file_path_rename)


def extract_svo(svo_path: str, output_path=''):
    """Extract SVO package

    Parameters
    ----------
    svo_path : str
        Path to SVO file (e.g. 'path/to/PACKAGE.SVO')
    output_path: str
        Path to extracted SVO output. Default value extract to hyoutatools directory.

    Notes
    -----
    Currently uses HyoutaTools (Windows only) to perform decompression.
    Refer to README.md for more details.

    """
    check_fourcc("FPS4", svo_path)
    logger.debug({
        "msg": "Extracting SVO package",
        "svo_path": svo_path,
    })
    hyoutatools_path = get_path("hyoutatools_path")
    command = f"{hyoutatools_path} ToVfps4e {svo_path}"
    if output_path:
        command = f"{hyoutatools_path} ToVfps4e {svo_path} {output_path}"
    subprocess.check_call(command)
    logger.info(f"Extract SVO completed.")


def decompress_tlzc(dat_path: str):
    """Decompress TLZC package

    Parameters
    ----------
    dat_path : str
        Path to DAT file (e.g. 'path/to/PACKAGE.DAT')

    Notes
    -----
    Currently uses HyoutaTools (Windows only) to perform decompression.
    Refer to README.md for more details.

    """
    check_fourcc('TLZC', dat_path)
    logger.debug({
        "msg": "Decompressing TLZC package",
        "dat_path": dat_path,
    })
    hyoutatools_path = get_path("hyoutatools_path")
    subprocess.check_call(f"{hyoutatools_path} tlzc -d {dat_path}")
    logger.info(f"Decompress TLZC completed.")


def unpack_dat(dat_path, deep_extract=False):
    """Unpack DAT file from SVO package

    Parameters
    ----------
    dat_path : str
        Path to DAT file (e.g. 'path/to/PACKAGE.DAT')
    deep_extract : bool
        True to extract deeper for digit only package (e.g. "0000").
        Default False.

    """
    # 1. Check if path is valid
    if not os.path.exists(dat_path):
        raise InvalidFileException(dat_path)

    hyoutatools_path = get_path("hyoutatools_path")
    fourcc = get_fourcc(dat_path)

    # 2.1 Decompress TLZC package using HyoutaTools
    if fourcc == "TLZC":
        decompress_tlzc(dat_path)
        split_dat_path = os.path.split(dat_path)
        pkg_dir = split_dat_path[0]
        pkg_name = split_dat_path[1]
        pkg_decompressed = f"{pkg_name}.dec"
        pkg_decompressed_path = os.path.join(pkg_dir, pkg_decompressed)
        check_fourcc('FPS4', pkg_decompressed_path)

        # 2.2 Unpack FPS4 package using HyoutaTools
        fps4e_command = f"{hyoutatools_path} ToVfps4e {pkg_decompressed_path}"
        logger.debug({
            "cmd": fps4e_command,
            "file": pkg_decompressed,
        })
        subprocess.check_call(fps4e_command)

        pkg_extracted_path = f"{pkg_decompressed_path}.ext"
        extracted_files = os.listdir(pkg_extracted_path)
        if len(extracted_files) == 2:
            # 2.3 Rename 0000 and 0001 only (read: actually TXM and TXV file)
            old_txm = os.path.join(pkg_extracted_path, extracted_files[0])
            old_txv = os.path.join(pkg_extracted_path, extracted_files[1])
            new_txm = os.path.join(pkg_extracted_path, f"{pkg_name}.TXM")
            new_txv = os.path.join(pkg_extracted_path, f"{pkg_name}.TXV")
            os.rename(old_txm, new_txm)
            os.rename(old_txv, new_txv)
        elif deep_extract:
            # 2.4 Handle assets like CH which unpacked as "0000", "0001" and so on
            for extracted_file in extracted_files:
                file_path = os.path.join(pkg_extracted_path, extracted_file)
                check_fourcc('FPS4', file_path)
                fps4e_command = f"{hyoutatools_path} ToVfps4e {file_path}"
                logger.debug({
                    "cmd": fps4e_command,
                })
                subprocess.check_call(fps4e_command)

    # 3. Exit early if not FPS4
    elif fourcc != "FPS4":
        raise Exception(f"Not compatible {fourcc} format for unpacking.")

    # 4. Unpack FPS4 DAT files
    fps4e_command = f"{hyoutatools_path} ToVfps4e {dat_path}"
    logger.debug({
        "cmd": fps4e_command,
        "file": dat_path,
    })
    subprocess.check_call(fps4e_command)

    logger.info(f"Unpack DAT completed.")


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
