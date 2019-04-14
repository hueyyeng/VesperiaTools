import os
import logging
import struct
import subprocess

from constants import HYOUTATOOLS, tales
from exceptions.files import (
    InvalidFileException,
    InvalidFourCCException,
)

logger = logging.getLogger(__name__)


def check_fourcc(fourcc, file_path):
    """Check FOURCC code of a file

    Parameters
    ----------
    fourcc : str
        The expected FOURCC value
    file_path : str
        Path to file

    Returns
    -------
    None

    """
    if not isinstance(file_path, str) or not os.path.isfile(file_path):
        raise InvalidFileException(file_path)
    file_header = open(file_path, "rb").read(32)
    file_fourcc = file_header[:4]
    # Check file's FOURCC with expected FOURCC in bytes representation
    if file_fourcc != fourcc.encode('utf-8'):
        logger.warning({
            "msg": f"Not an {fourcc} file!",
            "fourcc": str(file_fourcc),
            "file_header": str(file_header),
        })
        raise InvalidFourCCException(fourcc, file_fourcc)


def unpack_dat(dat_path, deep_extract=False):
    """Unpack DAT file from SVO package

    Parameters
    ----------
    dat_path : str
        Path to DAT file (e.g. 'path/to/PACKAGE.DAT')
    deep_extract : bool
        True to extract deeper for digit only package (e.g. "0000")

    Returns
    -------
    str
        The extracted package path
        e.g. path/to/package.dec.ext

    """
    # 1. Check if path is valid
    if not os.path.exists(dat_path):
        logger.warning(f"Package path {dat_path} is invalid!")
        raise InvalidFileException(dat_path)

    # 2.1 Decompress TLZC package using HyoutaTools
    check_fourcc('TLZC', dat_path)
    tlzc_command = f"{HYOUTATOOLS} tlzc -d {dat_path}"
    logger.debug({
        "cmd": tlzc_command,
    })
    subprocess.check_call(tlzc_command)

    # 2.2 Unpack FPS4 package using HyoutaTools
    pkg_dir = os.path.split(dat_path)[0]
    pkg_name = os.path.split(dat_path)[1]
    pkg_decompressed = f"{pkg_name}.dec"
    pkg_decompressed_path = os.path.join(pkg_dir, pkg_decompressed)
    check_fourcc('FPS4', pkg_decompressed_path)
    fps4e_command = f"{HYOUTATOOLS} ToVfps4e {pkg_decompressed_path}"
    logger.debug({
        "cmd": fps4e_command,
    })
    subprocess.check_call(fps4e_command)

    pkg_extracted_path = f"{pkg_decompressed_path}.ext"
    extracted_files = os.listdir(pkg_extracted_path)
    if len(extracted_files) == 2:
        # 3.1 Rename 0000 and 0001 only (read: actually TXM and TXV file)
        old_txm = os.path.join(pkg_extracted_path, extracted_files[0])
        old_txv = os.path.join(pkg_extracted_path, extracted_files[1])
        new_txm = os.path.join(pkg_extracted_path, f"{pkg_name}.TXM")
        new_txv = os.path.join(pkg_extracted_path, f"{pkg_name}.TXV")
        os.rename(old_txm, new_txm)
        os.rename(old_txv, new_txv)
    elif deep_extract:
        # 3.2 Handle assets like CH which unpacked as "0000", "0001" and so on
        for file in extracted_files:
            file_path = os.path.join(pkg_extracted_path, file)
            check_fourcc('FPS4', file_path)
            fps4e_command = f"{HYOUTATOOLS} ToVfps4e {file_path}"
            logger.debug({
                "cmd": fps4e_command,
            })
            subprocess.check_call(fps4e_command)

    return pkg_extracted_path


def get_byte_struct(data, endian, offset, fmt):
    """Get byte structure

    Parameters
    ----------
    data : bytes
    endian : str
        little-endian "<" or big-endian ">"
    offset : int
        Hex offset value
    fmt : str
        Format string

    Returns
    -------
    int

    Notes
    -----
    Makes parsing data a lot easier - delguoqing

    """
    size = struct.calcsize(fmt)
    result = struct.unpack(
        endian + fmt,
        data[offset: offset + size],
    )
    if len(result) == 1:
        return result[0]
    return result


def unpack_chara_dat(dat_path, root=".", depth=0):
    """Unpack DAT file from chara.svo package

    Parameters
    ----------
    dat_path : str
        Path to DAT file (e.g. 'path/to/0000')
    root : str
        The root path for unpacking
    depth : int
        Level of depth for unpacking

    Returns
    -------

    """
    indent = ("==" * depth) + "> "
    # 1. Load mesh file and check if FPS4
    check_fourcc("FPS4", dat_path)
    f = open(dat_path, "rb")
    data = f.read()
    f.close()

    # 2. If FPS4, need to split further
    file_count = get_byte_struct(data, ">", 0x4, "I")
    print("file_count", file_count)
    file_data_offset = get_byte_struct(data, ">", 0xc, "I")
    print("file_data_offset", file_data_offset)
    header_size = get_byte_struct(data, ">", 0x8, "I")
    print("header_size", header_size)
    assert header_size == 0x1C, "Header size should be a constant"

    file_descriptor_size = get_byte_struct(data, ">", 0x10, "H")
    file_descriptor_flag = get_byte_struct(data, ">", 0x12, "H")
    fdm = tales.FILE_DESCRIPTOR_MINIMUM
    assert file_descriptor_flag & fdm == fdm, "Least bitflag set not matched!"
    assert get_byte_struct(data, "<", 0x14, "I") == 0x0, "Should be reserved!"

    string_table_offset = get_byte_struct(data, ">", 0x18, "I")

    noname_idx = 0
    empty_idx = 0
    last_filename = ""
    mdl_part_count = 0

    for i in range(file_count):
        base_offset = offset = header_size + file_descriptor_size * i

        # File Offset
        file_offset = get_byte_struct(data, ">", offset, "I")
        # print("file_offset", file_offset)
        offset += 4
        if file_offset == 0xFFFFFFFF:
            file_descriptor = get_byte_struct(data, "<", offset, "%dI" % (file_descriptor_size / 4 - 1))
            print("file_descriptor", file_descriptor)
            assert not any(file_descriptor), "Empty file descriptor, other fields should all be zero!"
        else:
            # File Size
            real_file_size = get_byte_struct(data, ">", offset, "I")
            print("real_file_size", real_file_size)
            offset += 4
            # File Data
            file_data = data[file_offset: file_offset + real_file_size]
            # # File Name
            print("file_descriptor_flag", file_descriptor_flag, tales.FILE_DESCRIPTOR_FILE_NAME)
            if file_descriptor_flag & tales.FILE_DESCRIPTOR_FILE_NAME:
                file_name = get_byte_struct(data, ">", offset, "32s")
                file_name.rstrip("\x00").upper()
                print("file_name", file_name)
                offset += 0x20
            else:
                file_name = ""
            if not file_name and (last_filename.endswith(".SPM") or last_filename.endswith(".TXM")):
                file_name = last_filename[:-1] + "V"
                print("file_name", file_name)
            # # File Ext
            if "." in file_name and (not file_name.endswith(".DAT")):
                ext = "." + file_name.split(".")[-1]
            elif real_file_size > 0:
                file_type = get_byte_struct(file_data, ">", 0x0, "I")
                print("file_type", file_type)
                # Short Ext
                ext = tales.TYPE_2_EXT.get(file_type)
                print("ext", ext)
                # Long Ext
                if ext is None and get_byte_struct(file_data, ">", 0x0, "8s").rstrip("\x00\x20") in tales.LONG_TYPES:
                    ext = "." + get_byte_struct(file_data, ">", 0x0, "8s").rstrip("\x00\x20")
                elif ext is None:
                    ext = ""
                # == DEBUG EXTENSION TYPE ==
                # ext_debug_msg = (f"Unknown extension type!"
                #                  f" 0x{file_type} or {file_data[:4]} or {file_data[:8]} @ 0x{file_offset}")
                # raise Exception(ext_debug_msg)
            else:
                ext = ""
            if mdl_part_count > 0 and not file_name:
                file_name = os.path.splitext(last_filename)[0] + ext
                print("file_name", file_name)
            mdl_part_count -= 1
            # TODO: Resume refactoring FPS4 splitter
