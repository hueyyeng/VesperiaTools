"""Vesperia Tools Textures"""
import logging
import os
import subprocess

from utils.files import unpack_dat
from utils.helpers import get_hyoutatools_path

logger = logging.getLogger(__name__)


def extract_textures(package_path: str):
    """Extract DDS textures from TXM and TXV files

    Parameters
    ----------
    package_path : str
        Path to DAT file (e.g. 'path/to/PACKAGE.DAT')
        or directory containing TXM and TXV files.

    Notes
    -----
    Currently uses HyoutaToolsCLI (Windows only) to perform extraction.
    Refer to README.md for more details.

    """
    # 1. Verify path is DAT file or directory
    textures_path = package_path
    if not os.path.isdir(package_path) and os.path.splitext(package_path)[1] == ".DAT":
        textures_path = unpack_dat(package_path)

    # 2. Search for TXM files recursively and decode it
    hyoutatools_path = get_hyoutatools_path()
    found_txm_txv = 0
    for root, _dirs, files in os.walk(textures_path):
        for file in files:
            if file.endswith(("TXM",)):
                texture_filename = os.path.splitext(file)[0]
                txm_file = os.path.normpath(
                    f"{os.path.join(root, texture_filename)}.TXM"
                )
                txv_file = os.path.normpath(
                    f"{os.path.join(root, texture_filename)}.TXV"
                )
                if os.path.exists(txm_file) and os.path.exists(txv_file):
                    found_txm_txv += 1
                texture_decode_command = f"{hyoutatools_path} Tales.Vesperia.Texture.Decode {txm_file} {txv_file}"
                logger.debug({
                    "cmd": texture_decode_command,
                })
                subprocess.check_call(texture_decode_command)

    if not found_txm_txv:
        logger.debug(
            "No valid textures found! Please ensure both TXM and TXV files of "
            "the same name exists in the directory."
        )
    else:
        logger.info(f"Extract DDS textures completed. Found {found_txm_txv} TXM/TXV pairing files.")
