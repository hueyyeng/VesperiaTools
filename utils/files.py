"""Vesperia Tools Files Exceptions"""
import logging
import os
import struct
import subprocess
from exceptions.files import (
    InvalidFileException,
    InvalidFourCCException,
)

from constants import tales
from utils.helpers import get_hyoutatools_path

logger = logging.getLogger(__name__)
log_handler = logging.FileHandler('vesperia_tools_debug.log')
log_handler.setLevel(logging.DEBUG)
logger.addHandler(log_handler)


def check_fourcc(fourcc, file_path):
    """Check FOURCC code of a file

    Parameters
    ----------
    fourcc : str
        The expected FOURCC value
    file_path : str
        Path to file

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


def extract_svo(svo_path, output_path=''):
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
    check_fourcc('FPS4', svo_path)
    logger.debug({
        "msg": "Extracting SVO package",
        "svo_path": svo_path,
    })
    hyoutatools_path = get_hyoutatools_path()
    command = f"{hyoutatools_path} ToVfps4e {svo_path}"
    if output_path:
        command = f"{hyoutatools_path} ToVfps4e {svo_path} {output_path}"
    subprocess.check_call(command)
    logger.info(f"Extract SVO completed.")


def decompress_tlzc(dat_path):
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
    hyoutatools_path = get_hyoutatools_path()
    subprocess.check_call(f"{hyoutatools_path} tlzc -d {dat_path}")
    logger.info(f"Decompress TLZC completed.")


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
        raise InvalidFileException(dat_path)

    # 2.1 Decompress TLZC package using HyoutaTools
    decompress_tlzc(dat_path)

    # 2.2 Unpack FPS4 package using HyoutaTools
    pkg_dir = os.path.split(dat_path)[0]
    pkg_name = os.path.split(dat_path)[1]
    pkg_decompressed = f"{pkg_name}.dec"
    pkg_decompressed_path = os.path.join(pkg_dir, pkg_decompressed)
    check_fourcc('FPS4', pkg_decompressed_path)
    hyoutatools_path = get_hyoutatools_path()
    fps4e_command = f"{hyoutatools_path} ToVfps4e {pkg_decompressed_path}"
    logger.debug({
        "cmd": fps4e_command,
        "file": pkg_decompressed,
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
        for extracted_file in extracted_files:
            file_path = os.path.join(pkg_extracted_path, extracted_file)
            check_fourcc('FPS4', file_path)
            fps4e_command = f"{hyoutatools_path} ToVfps4e {file_path}"
            logger.debug({
                "cmd": fps4e_command,
            })
            subprocess.check_call(fps4e_command)

    logger.info(f"Unpack DAT completed.")
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


def unpack_chara_dat(
        data,
        root=".",
        create_output_dir=False,
        depth=0,
        verbose=1,
        force_save=False,
):
    """Unpack DAT file from chara.svo package

    Parameters
    ----------
    data : str or bytes
        Path to DAT file (e.g. 'path/to/XXX_C###.DAT')
    root : str
        The root path for unpacking
    create_output_dir : bool
        Create output dir using DAT name
    depth : int
        Depth indicator during unpacking.
    verbose : int
    force_save : bool

    """
    # 1.1 Create output directory using input data name
    if create_output_dir:
        unpack_dir_path = os.path.splitext(data)[0]
        root = unpack_dir_path
        if os.path.isfile(data):
            try:
                os.mkdir(unpack_dir_path)
                logger.debug({
                    "msg": "Creating directory using package name",
                    "dir_path": unpack_dir_path,
                })
            except FileExistsError:
                logger.error({
                    "msg": "Output directory already exists!",
                    "dir_path": unpack_dir_path,
                })

    # 1.2 Load mesh file and check if FPS4
    if isinstance(data, str) and os.path.isfile(data):
        logger.debug({"data_path": data})
        check_fourcc("FPS4", data)
        with open(data, "rb") as f:
            data = f.read()

    # 2. If FPS4, need to split further
    file_count = get_byte_struct(data, ">", 0x4, "I")
    file_data_offset = get_byte_struct(data, ">", 0xc, "I")
    header_size = get_byte_struct(data, ">", 0x8, "I")
    logger.debug({
        "file_count": file_count,
        "file_data_offset": file_data_offset,
        "header_size": header_size,
    })
    assert header_size == 0x1C, "Header size should be a constant"

    file_descriptor_flag = get_byte_struct(data, ">", 0x12, "H")
    fdm = tales.FILE_DESCRIPTOR_MINIMUM
    assert file_descriptor_flag & fdm == fdm, "Least bitflag set not matched!"
    assert get_byte_struct(data, ">", 0x14, "I") == 0x0, "Should be reserved!"

    noname_idx = 0
    empty_idx = 0
    last_filename = ""
    mdl_part_count = 0

    file_descriptor_size = get_byte_struct(data, ">", 0x10, "H")
    for i in range(file_count):
        base_offset = offset = header_size + file_descriptor_size * i

        # File Offset
        file_offset = get_byte_struct(data, ">", offset, "I")
        logger.debug({"file_offset": file_offset})
        offset += 4
        if file_offset == 0xFFFFFFFF:
            file_descriptor = get_byte_struct(data, ">", offset, "%dI" % (file_descriptor_size / 4 - 1))
            logger.debug({"file_descriptor": file_descriptor})
            # assert not any(file_descriptor), "Empty file descriptor, other fields should all be zero!"

        # File Size
        offset += 4
        real_file_size = get_byte_struct(data, ">", offset, "I")
        logger.debug({"real_file_size": real_file_size})
        offset += 4

        # File Data
        file_data = data[file_offset: file_offset + real_file_size]

        # File Name
        if file_descriptor_flag & tales.FILE_DESCRIPTOR_FILE_NAME:
            file_name = get_byte_struct(data, ">", offset, "32s").rstrip(b"\x00").upper()
            logger.debug({
                "msg": "file_descriptor_flag & tales.FILE_DESCRIPTOR_FILE_NAME",
                "file_name": file_name,
            })
            offset += 0x20
        else:
            file_name = ""
        if not file_name and (last_filename.endswith(".SPM") or last_filename.endswith(".TXM")):
            file_name = last_filename[:-1] + "V"

        # File Ext
        if "." in file_name and (not file_name.endswith(".DAT")):
            ext = "." + file_name.split(".")[-1]
            logger.debug({
                "msg": "File Extension",
                "ext": ext,
            })
        elif real_file_size > 0:
            file_type = get_byte_struct(file_data, ">", 0x0, "I")
            # Short Ext
            ext = tales.TYPE_2_EXT_PC.get(file_type)
            logger.debug({
                "msg": "Short File Extension",
                "ext": ext,
                "file_type": hex(file_type),
            })
            # Long Ext/Types
            long_getter = get_byte_struct(file_data, ">", 0x0, "8s")
            long_ext_identifier = long_getter.rstrip(b"\x00\x20")
            logger.debug({
                "msg": "Long File Extension/Types",
                "long_ext_identifier": long_ext_identifier,
            })
            if ext is None and long_ext_identifier in tales.LONG_TYPES:
                ext = "." + long_ext_identifier.decode()
                logger.debug({
                    "msg": "Long File Extension/Types Decoded",
                    "ext": ext,
                })
            if ext is None:
                ext = ""
        else:
            ext = ""
        if mdl_part_count > 0 and not file_name:
            file_name = os.path.splitext(last_filename)[0] + ext
        mdl_part_count -= 1

        # Resolve file name by various hint
        # TODO: Figure out why some NONAME file are skipped compared to Python 2 script
        if not file_name:
            if real_file_size == 0:
                file_name = f"EMPTY{empty_idx}"
                logger.debug({"file_name, EMPTY": file_name})
                empty_idx += 1
            else:
                file_name = f"NONAME{noname_idx}{ext}"
                logger.debug({"file_name, NONAME": file_name})
                noname_idx += 1

        # Unknown: bit4
        if file_descriptor_flag & tales.FILE_DESCRIPTOR_BIT4:
            unk = get_byte_struct(data, ">", offset, "I")
            if unk != 0:
                raise Exception(f"unk field = 0x{unk} @ offset = 0x{offset}")
            offset += 0x4

        # Datatype, e.g.MDL
        if file_descriptor_flag & tales.FILE_DESCRIPTOR_DATA_TYPE:
            data_type = get_byte_struct(data, ">", offset, "4s").rstrip(b"\x00")
            offset += 0x4
        else:
            data_type = ""
        if data_type == "MDL":
            mdl_part_count = 9

        # Argument
        arg = ""
        if file_descriptor_flag & tales.FILE_DESCRIPTOR_ARG:
            arg_off = get_byte_struct(data, ">", offset, "I")
            logger.debug({"arg_off": arg_off})
            offset += 0x4
            string_table_offset = get_byte_struct(data, ">", 0x18, "I")
            if arg_off > 0:
                assert arg_off >= string_table_offset, f"Invalid arg offset {hex(arg_off)}"
                arg = data[arg_off: data.find(b"\x00", arg_off)]
                logger.debug({"arg": arg})

        # Path hint
        if arg:
            decoded_arg = arg.decode()
            if ext in (".FPS4", ".T8BTMO"):
                file_name = decoded_arg.replace("/", "_") + ext
            elif ext in tales.KNOWN_EXT:
                if "/" in decoded_arg:
                    file_name = decoded_arg.replace("/", "_") + ext
            elif ext in tales.LONG_TYPES[-6:]:
                env = decoded_arg  # noqa

            # Write arg out for manual inspection
            if not os.path.exists(root):
                os.mkdir(root)
            arg_list_filename = os.path.join(root, "arg_list.txt")
            with open(arg_list_filename, "a+") as f_arg_list:
                f_arg_list.write(f"{file_name} {decoded_arg}\n")

        # Unknown: bit7
        if file_descriptor_flag & tales.FILE_DESCRIPTOR_BIT7:
            unk = get_byte_struct(data, ">", offset, "I")
            if unk != 0:
                raise Exception(f"unk field = {hex(unk)} @ offset = {hex(offset)}")
            offset += 0x4

        indent = f"{'==' * depth}> "
        if verbose > 0:
            line = f"off={hex(base_offset)}, name:{file_name}, {hex(file_offset)}~{hex(file_offset + real_file_size)}"
            if arg:
                line += f", arg:{arg.decode()}"
            if data_type:
                line += f", data_type:{data_type}"
            print(indent + line + "\n")

        # Make output folder
        new_file_path = os.path.join(root, file_name)
        logger.debug({"new_file_path": new_file_path})
        new_root = os.path.join(root, os.path.splitext(file_name)[0])
        file_ext = os.path.splitext(file_name)[1]
        logger.debug({
            "root": root,
            "ext": ext,
            "file_ext": file_ext,
        })
        if ext not in tales.KNOWN_EXT:
            if ext and os.path.exists(root):
                logger.debug({
                    "msg": "Root directory exists",
                    "path": new_file_path,
                    "isdir": os.path.isdir(new_file_path),
                })
                if not os.path.isdir(new_file_path):
                    try:
                        os.mkdir(new_root)
                        logger.debug({
                            "msg": "Creating New Directory",
                            "directory": new_root,
                        })
                    except FileExistsError:
                        logger.warning({
                            "msg": "File/Directory already exists!",
                            "file/directory": new_root,
                        })

        if force_save:
            with open(os.path.join(root, file_name), "wb") as f:
                f.write(file_data)

        if os.path.exists(new_file_path):
            with open(new_file_path, "wb") as f:
                f.write(file_data)
            logger.debug({
                "msg": "Creating File - If Exists and Continue",
                "file": new_file_path,
            })
            continue
        else:
            with open(new_file_path, "wb") as f:
                f.write(file_data)
            logger.debug({
                "msg": "Creating File - If Not Exists",
                "file": new_file_path,
            })

        if os.path.isdir(new_root):
            logger.debug({
                "msg": "Need further split/unpack",
                "new_root": new_root,
            })
            need_split = unpack_chara_dat(  # noqa
                file_data,
                root=new_root,
                depth=depth + 1,
            )

            if (not need_split) and (not force_save):
                with open(os.path.join(root, file_name), "wb") as f:
                    f.write(file_data)

        last_filename = file_name
        logger.debug({"last_filename": last_filename})
