"""Vesperia Tools Textures"""
import os
import logging
import subprocess

from constants import HYOUTATOOLS
from utils.files import unpack_dat

logger = logging.getLogger(__name__)


def extract_textures_from_package(package_path):
    """Extract DDS textures from TXM and TXV files

    Parameters
    ----------
    package_path : str
        Path to DAT file (e.g. 'path/to/PACKAGE.DAT')
        or directory containing TXM and TXV files.

    Notes
    -----
    Currently uses HyoutaTools to perform extraction.
    Refer to README.md for more details.

    """
    # 1. Verify path is DAT file or directory
    textures_path = package_path
    if not os.path.isdir(package_path) and os.path.splitext(package_path)[1] == ".DAT":
        textures_path = unpack_dat(package_path)

    # 2. Search for TXM files recursively and decode it
    for root, _dirs, files in os.walk(textures_path):
        for file in files:
            if file.endswith(("TXM",)):
                texture_filename = os.path.splitext(file)[0]
                txm_file = f"{os.path.join(root, texture_filename)}.TXM"
                txv_file = f"{os.path.join(root, texture_filename)}.TXV"
                texture_decode_command = f"{HYOUTATOOLS} Tales.Vesperia.Texture.Decode {txm_file} {txv_file}"
                logger.debug({
                    "cmd": texture_decode_command,
                })
                subprocess.check_call(texture_decode_command)

    logger.debug("Extract DDS textures completed")
