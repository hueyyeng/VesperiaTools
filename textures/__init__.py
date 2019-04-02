import os
import logging
import subprocess

from exceptions.files import InvalidFileException
from utils.files import check_fourcc

HYOUTATOOLS = "hyoutatools/HyoutaTools.exe"

logger = logging.getLogger(__name__)


def extract_textures_from_package(package_path):
    """Extract DDS textures from TLZC package

    Parameters
    ----------
    package_path : str
        Path to package (e.g. 'path/to/package.dat')

    Returns
    -------
    bool

    Notes
    -----
    Currently uses HyoutaTools to perform extraction. Refer to
    README.md for more details.

    """
    # 1. Check if path is valid
    if not os.path.exists(package_path):
        logger.warning(f"Package path {package_path} is invalid!")
        raise InvalidFileException(package_path)

    # 2.1 Decompress TLZC package using HyoutaTools
    check_fourcc('TLZC', package_path)
    tlzc_command = f"{HYOUTATOOLS} tlzc -d {package_path}"
    logger.debug({
        "cmd": tlzc_command,
    })
    subprocess.check_call(tlzc_command)

    # 2.2 Unpack FPS4 package using HyoutaTools
    pkg_dir = os.path.split(package_path)[0]
    pkg_decompressed = f"{os.path.split(package_path)[1]}.dec"
    pkg_decompressed_path = os.path.join(pkg_dir, pkg_decompressed)
    check_fourcc('FPS4', pkg_decompressed_path)
    fps4e_command = f"{HYOUTATOOLS} ToVfps4e {pkg_decompressed_path}"
    logger.debug({
        "cmd": fps4e_command,
    })
    subprocess.check_call(fps4e_command)

    # 3. Search for TXM files recursively and decode it
    unpacked_dir_path = f"{pkg_decompressed_path}.ext"
    for root, dirs, files in os.walk(unpacked_dir_path):
        for file in files:
            if file.endswith(("TXM",)):
                texture_filename = os.path.splitext(file)[0]
                txm_file = f"{os.path.join(root, texture_filename)}.TXM"
                txv_file = f"{os.path.join(root, texture_filename)}.TXV"
                texture_decode_command = f"{HYOUTATOOLS} Tales.Vesperia.Texture.Decode {txm_file} {txv_file}"
                logger.debug({
                    "cmd": texture_decode_command,
                })
                subprocess.check_call(texture_decode_command, stdout=subprocess.PIPE)

    logger.debug("Process completed")
