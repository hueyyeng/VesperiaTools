import os
import logging

from utils.files import get_byte_struct

logger = logging.getLogger(__name__)

PLATFORM_X360 = 0x4
TYPE_CODE = 0x00010000


def parse_mesh(file_path, endian="<", ref_data=None, mat_data=None):
    """Model mesh parser

    Parameters
    ----------
    file_path : str
        Path to Vesperia mesh file (SPM file)
    endian : str
        little-endian "<" or big-endian ">"
        Default is little-endian
    ref_data : bytes or None
    mat_data : bytes or None

    Returns
    -------
    None

    """
    # 1. Load mesh file
    f = open(file_path, "rb")
    data = f.read()
    f.close()

    # 2. Verify file structure integrity
    type_code = get_byte_struct(data, endian, 0x0, "I")
    assert type_code == TYPE_CODE, "This might not be a Tales of Vesperia mesh block!"
    total_size = get_byte_struct(data, endian, 0x4, "I")
    assert total_size == len(data), "Block size doesn't match, data may be corrupted!"
    logger.debug({
        "msg": f"Assert {os.path.split(file_path)[1]} Data Structure",
        "type_code": type_code,
        "total_size": total_size,
    })
    platform = get_byte_struct(data, endian, 0x8, "I")
    assert platform in (PLATFORM_X360, 0x3, 0x2), "This file is not from Xbox 360 version!"
    # TODO: Resume refactoring delguoqing mesh parser
