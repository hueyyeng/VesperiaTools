"""Parser for Vesperia data objects."""
import os
import math  # Handle NaN value
import struct
import logging
from pathlib import Path
import zlib
import re
from dataclasses import dataclass

from constants.tales import DDS_HEADER, TYPE_2_EXT_PC
from exceptions.files import InvalidFourCCException
from parsers.models import Mesh
from utils.binaries import BinaryReader
from utils.files import check_fourcc

logger = logging.getLogger(__name__)


class Node:
    """Node for object parsing and general data structures.

    Contains attributes needed for exporting to external format (e.g. Wavefront OBJ)

    This also hold pointers of the data element that we want to store when
    parsing an object such as found meshes and materials.

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    def __init__(self):
        self.name = "NONAME"
        self.children = []
        self.data = {}
        self.offset = None


def debug_mesh(
        node: Node,
        verbose=False
):
    """Debug found mesh from SPM package.

    Parameters
    ----------
    node : Node
    verbose : bool
        Toggle verbose level for individual indices

    """
    if not node.data:
        raise Exception("No meshes found!")
    logger.debug("%s>" % ('=' * 200))
    logger.debug({
        "hash_list": node.data['hash_list'],  # Important? Probably not for static mesh
    })
    mesh_lists = node.data["mesh_list"]
    for idx, mesh_list in enumerate(mesh_lists):
        logger.debug("Total meshes for Loop %s : %s" % (idx, len(mesh_list)))
        for mesh in mesh_list:
            logger.debug({
                "MeshName": mesh.name,
                "vertUVList": len(mesh.vertUVList),
                "vertNormList": len(mesh.vertNormList),
                "vertPosList": len(mesh.vertPosList),
                "triangleList": len(mesh.triangleList),
                "indiceList": len(mesh.indiceList),  # Needed for face creation
                "matIDList": len(mesh.matIDList),
                "matList": len(mesh.matList),
            })
            if verbose:
                for face_idx, indice in enumerate(mesh.indiceList):
                    logger.debug("indice %03d : %s" % (face_idx, indice))


def get_vertex_data(
        mesh: object,
        g: BinaryReader,
        v1: int,
        v2: int,
        v3: int,
        v4: int,
        n: int,
        verbose=False,
):
    """Get vertex data for skinned mesh.

    Parameters
    ----------
    mesh : object
    g : BinaryReader
    v1 : int
    v2 : int
    v3 : int
    v4 : int
    n : int
    verbose : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    for i in range(v1):
        v_offset = g.tell()
        mesh.vertPosList.append(g.f(3))
        mesh.vertNormList.append(g.f(3))
        indice_offset = g.tell()
        if verbose:
            logger.debug({
                "v1 v_offset": v_offset,
                "v1 indice_offset": indice_offset,
            })
        mesh.skinIndiceList.append(g.B(4))
        mesh.skinWeightList.append([0, 0, 0, 1])

    for i in range(v2):
        v_offset = g.tell()
        mesh.vertPosList.append(g.f(3))
        mesh.vertNormList.append(g.f(3))
        indice_offset = g.tell()
        if verbose:
            logger.debug({
                "v2 v_offset": v_offset,
                "v2 indice_offset": indice_offset,
            })
        mesh.skinIndiceList.append(g.B(4))
        w1 = g.f(1)[0]
        w2 = 1.0 - w1
        mesh.skinWeightList.append([0, 0, w2, w1])

    for i in range(v3):
        v_offset = g.tell()
        mesh.vertPosList.append(g.f(3))
        mesh.vertNormList.append(g.f(3))
        indice_offset = g.tell()
        if verbose:
            logger.debug({
                "v3 v_offset": v_offset,
                "v3 indice_offset": indice_offset,
            })
        mesh.skinIndiceList.append(g.B(4))
        w1 = g.f(1)[0]
        w2 = g.f(1)[0]
        w3 = 1.0 - w1 - w2
        mesh.skinWeightList.append([0, w3, w2, w1])

    for i in range(v4):
        v_offset = g.tell()
        mesh.vertPosList.append(g.f(3))
        mesh.vertNormList.append(g.f(3))
        indice_offset = g.tell()
        if verbose:
            logger.debug({
                "v4 v_offset": v_offset,
                "v4 indice_offset": indice_offset,
            })
        mesh.skinIndiceList.append(g.B(4))
        w1 = g.f(1)[0]
        w2 = g.f(1)[0]
        w3 = g.f(1)[0]
        w4 = 1.0 - w1 - w2 - w3
        mesh.skinWeightList.append([w4, w3, w2, w1])


def parse_uv(
        file_path: str,
        node: Node,
        verbose=False,
):
    """Parse UV coordinates value.

    Parameters
    ----------
    file_path : str
        Path to SPV file (e.g. 'path/to/PACKAGE.SPV')
    node : Node
    verbose : bool
        Display mesh's UV values. Default False.

    Notes
    -----
    - Based on delguoqing's Python 2 script for Vesperia 360.
    - Currently has known issue with parsing UV for BG meshes.

    """
    binary_file = open(file_path, 'rb')
    g = BinaryReader(binary_file)

    current_offset = g.tell()
    g.seek(current_offset)

    # TODO: Figure out BG funky UV packing
    # Parse UV in SPV File
    for meshes in node.data["mesh_list"]:
        for mesh in meshes:
            unpack_error = False
            if verbose:
                logger.debug({
                    "Mesh UV:": mesh.name
                })
            for m in range(mesh.vertUVCount):
                offset = g.tell()
                try:
                    f = g.f(5)
                except struct.error:
                    unpack_error = True
                    f = (0.0, 0.0, 0.0)
                offset_diff = g.tell() - offset
                u = 0.0 if math.isnan(f[1]) else f[1]
                v = 0.0 if math.isnan(f[2]) else f[2]
                if verbose:
                    logger.debug({
                        "UV": "%f, %f" % (u, v),
                        "offset": g.tell(),
                    })
                mesh.vertUVList.append([u, 1.0 - v])  # Fix UV?
                # mesh.vertUVList.append([u, v])  # Fix UV?
            if unpack_error:
                logger.warning("UV ERROR DURING UNPACKING. USING (0.0, 0.0) FOR AFFECTED UV")

    g.close()


def parse_mesh(
        file_path: str,
        node: Node,
        verbose=False,
):
    """Parse mesh data from SPM (and SPV) package.

    The SPM and SPV files must be located in the same directory.

    Parameters
    ----------
    file_path : str
        Path to SPM file (e.g. 'path/to/PACKAGE.SPM')
    node : Node
    verbose : bool
        Display verbose output of mesh parsing. Default False

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    prefix_file_path, ext = os.path.splitext(file_path)
    if ext.lower() == ".spv":
        file_path = prefix_file_path + ".SPM"
    binary_file = open(file_path, "rb")
    node.name = os.path.splitext(os.path.basename(file_path))[0]
    g = BinaryReader(binary_file)
    n = 0

    current_offset = g.tell()
    node.offset = current_offset

    # Handle SPM file
    logger.debug("=== DEBUG MESH PARSER ===")
    g.seek(current_offset)
    B = g.i(4)
    meshes = B[3]
    offset_seek = current_offset + B[2]
    logger.debug({
        "B": B,
        "meshes": B[3],
        "offset_seek": offset_seek,
    })
    g.seek(offset_seek)
    C = g.i(5)
    C1 = []
    logger.debug("Current offset: %s" % g.tell())
    for m in range(meshes):
        a = g.i(8)
        logger.debug({
            "g.i(8)": a,
        })
        C1.append(a)
    for m in range(meshes):
        a = g.i(4)
        logger.debug({
            "g.i(4)": a,
        })
    node.data["mesh_list"] = []

    for _mesh_idx, m in enumerate(range(meshes)):
        logger.debug("%s Looping Mesh %s %s>" % (('=' * 64), (_mesh_idx), ('=' * 64)))
        D = g.i(15)
        logger.debug({
            "D": D,
            "D[13]": D[13],
        })
        tm = g.tell()
        name_offset = tm - 2 * 4 + D[13]
        g.seek(name_offset)
        name = g.find(b"\x00")
        logger.debug({
            "name": name,
            "name_offset": name_offset,
        })

        offset_1 = tm - 1 * 4 + D[14]
        logger.debug("offset_1: %s - 1 * 4 + %s = %s" % (tm, D[14], offset_1))
        g.seek(offset_1)

        mesh_list = []
        node.data["mesh_list"].append(mesh_list)

        offset_2 = tm - 9 * 4 + D[6]
        logger.debug("offset_2: %s - 9 * 4 + %s = %s" % (tm, D[6], offset_2))
        g.seek(offset_2)

        unknown = g.i(1)
        unkCount = unknown[0]
        logger.debug({
            "unknown": unknown,
            "unkCount": unkCount,
        })
        logger.debug({
            "indice_start_offset": g.tell(),
            "D[11]": D[11],
        })
        E = []

        if unkCount >= 1:
            # Original approach. Works great for CH mesh.
            logger.debug("FOUND %s SUBMESHES - Original Approach" % unkCount)
            for i in range(unkCount):
                mesh = Mesh()
                mesh.name = name
                mesh.diffuseID = D[4] - 1
                E1 = g.H(2)
                logger.debug({
                    "E1": E1,
                })
                mesh.vertUVCount = E1[0]
                logger.debug("mesh.vertUVCount: %s" % mesh.vertUVCount)
                mesh_list.append(mesh)
                E.append(E1)

            for i in range(unkCount):
                face_idx = E[i][1]
                indiceList = g.H(face_idx)
                logger.debug("indiceList size: %s face_idx: %s" % (len(indiceList), face_idx))
                mesh = mesh_list[i]
                mesh.indiceList = indiceList

            logger.debug("mesh.indiceList: %s" % len(mesh.indiceList))

        else:
            # Blender combined approach. Faces still incorrectly parsed.
            logger.debug("FOUND %s SUBMESHES - Blender Combined Approach" % unkCount)
            for i in range(unkCount):
                mesh = Mesh()
                mesh.name = name
                mesh.diffuseID = D[4] - 1
                mesh_list.append(mesh)
                E1 = g.H(2)
                logger.debug({
                    "E1": E1,
                })
                mesh.vertUVCount += E1[0]
                E.append(E1)
                logger.debug("mesh.vertUVCount: %s" % mesh.vertUVCount)
            for i in range(unkCount):
                indiceList = g.H(E[i][1])
                mesh = mesh_list[i]
                mesh.indiceList = indiceList

            logger.debug("mesh.indiceList size: %s" % len(mesh.indiceList))

        mesh_offset = tm - 8 * 4 + D[7]
        logger.debug("mesh_offset: %s - 8 * 4 + %s = %s" % (tm, D[7], mesh_offset))
        g.seek(mesh_offset)
        logger.debug("C1[%s]: %s" % (m, C1[m]))
        if D[0] in (1792,):
            logger.debug("VERDICT: Unskinned mesh? %s" % name)
            mesh = mesh_list[0]
            for i in range(C1[m][4]):
                mesh.vertPosList.append(g.f(3))

        elif D[0] in (1024, 1026, 1027):
            logger.debug("VERDICT: BG mesh? %s" % name)
            mesh = mesh_list[0]
            vertices = C1[m][4]
            if vertices == 0:
                # NOTE: Don't bother trying other index values besides D[10]
                logger.debug("No vertices found! Probably BG or static mesh. Using D[10]: %s" % D[10])
                vertices = D[10]

            total_v = []
            total_vn = []
            total_indices = mesh.indiceList
            print("total_indices:", len(total_indices))

            for i in range(vertices):
                # Vertex Position
                v_offset = g.tell()
                vertex = g.f(3)
                if verbose:
                    logger.debug({
                        "v": vertex,
                        "v_offset": v_offset,
                    })
                total_v.append(vertex)
                mesh.vertPosList.append(vertex)

                # Vertex Normal
                vn_offset = v_offset
                if not D[0] in (1024, 1026):
                    vn_offset = v_offset + 888
                g.seek(vn_offset)
                vertex_normal = g.f(3)
                if verbose:
                    logger.debug({
                        "vn": vertex_normal,
                        "vn_offset": vn_offset,
                    })
                total_vn.append(vertex_normal)
                mesh.vertNormList.append(vertex_normal)
                g.seek(v_offset + 12)

            start_vertUVCount = 0
            end_vertUVCount = 0
            start_indiceList = 0
            end_indiceList = 0

            for idx, mesh in enumerate(mesh_list):
                end_vertUVCount += mesh.vertUVCount
                mesh.vertPosList = total_v[start_vertUVCount:end_vertUVCount]
                mesh.vertNormList = total_vn[start_vertUVCount:end_vertUVCount]
                start_vertUVCount += mesh.vertUVCount

                logger.debug({
                    "submesh_name": mesh.name,
                    "v": len(mesh.vertPosList),
                    "vn": len(mesh.vertNormList),
                })

        elif D[0] in (258, 256):
            logger.debug("VERDICT: Skinned mesh? %s" % name)
            mesh = mesh_list[0]

            g.seek(mesh_offset)
            v1 = C1[m][4]
            v2 = C1[m][5]
            v3 = C1[m][6]
            v4 = C1[m][7]
            logger.debug({
                "v1": v1,
                "v2": v2,
                "v3": v3,
                "v4": v4,
            })
            get_vertex_data(mesh, g, v1, v2, v3, v4, n, verbose)
            mesh_range = unkCount - 1
            logger.debug("mesh_range: %s" % mesh_range)
            for x in range(mesh_range):
                logger.debug("Loop Submesh %s" % x)
                mesh = mesh_list[1 + x]
                E = g.i(4)
                v1 = E[0]
                v2 = E[1]
                v3 = E[2]
                v4 = E[3]
                logger.debug({
                    "v1": v1,
                    "v2": v2,
                    "v3": v3,
                    "v4": v4,
                })
                get_vertex_data(mesh, g, v1, v2, v3, v4, n, verbose)

        else:
            logger.warning({
                "msg": "Invalid mesh object.",
                "D[1]": D[1],
                "g.f(12)": g.f(12),
            })
            break

        g.seek(tm)

    F = g.i(C[0])
    node.data["hash_list"] = F

    # Handle SPV file
    spv_file = os.path.splitext(file_path)[0] + ".SPV"
    logger.debug({
        "spv_file": spv_file,
    })
    parse_uv(spv_file, node, verbose=verbose)
    g.close()


def parse_material(
        file_path: str,
        node: Node,
        verbose=False,
):
    """Parse material from MTR package.

    Parameters
    ----------
    file_path : str
        Path to DAT file (e.g. 'path/to/PACKAGE.MTR')
    node : Node
    verbose : bool

    Notes
    -----
    Haven't tested it as the original script by Szkaradek123 is for Blender 2.49.
    Will revisit this in future updates.

    """
    binary_file = open(file_path, 'rb')
    node.name = os.path.splitext(os.path.basename(file_path))[0]
    g = BinaryReader(binary_file)
    current_offset = g.tell()
    node.offset = current_offset

    # Handle MTR file
    material_list = []
    g.seek(current_offset)
    B = g.i(4)
    g.seek(current_offset + B[2])

    count = g.i(1)[0]

    lll = []
    for m in range(B[3]):
        C = g.i(8)
        D = g.i(C[0] * 2)
        logger.debug({
            "[C, D]": [C, D],
        })
        lll.append(C)

    logger.debug({
        "B": B,
        "count": count,
        "lll": lll,
    })

    # Loop through materials
    for m in range(B[3]):
        logger.debug("%s>" % ('=' * 200))
        tm = g.tell()
        C = g.i(8)
        logger.debug({
            "tm": tm,
            "C": C,
        })
        found_material_names = []
        found_material_texture_names = []
        material_name = "UNKNOWN_MAT"
        for i in range(8):
            logger.debug("%s Loop %s %s>" % (('=' * 24), (i + 1), ('=' * 24)))
            logger.debug("Current offset is: %s" % g.tell())
            c = C[i]
            name = None
            if c != 0:
                logger.debug("%s>" % ('=' * 32))
                g.seek(tm + 4 * i + c)
                name = g.find(b"\x00")
                if name and 'MAT' in name:
                    logger.debug("Name found: %s" % name)
                    material_name = name
                elif name:
                    found_material_texture_names.append(name)

        found_material_names.append({
            "mtl": material_name,
            "tex": found_material_texture_names,
        })

        logger.debug({
            "found_material_names": found_material_names,
        })
        material_list.append(found_material_names)
        g.seek(tm + 32)

    node.data["material_list"] = material_list
    logger.debug({
        "material_list": material_list,
    })
    g.close()


def find_substring_offset(
        context: bytes,
        substring: bytes,
):
    """Find offset value between reoccurring substring in a context.

    Currently specific for TXV package.

    Parameters
    ----------
    context : bytes
        Must be bytes str. The data with reoccurring substring.
    substring : bytes
        Must be bytes str. The substring value.

    Returns
    -------
    str

    """
    start = 0
    while True:
        start = context.find(substring, start)
        # use start += 1 to find overlapping matches
        if start == -1:
            return
        yield start
        start += len(substring)


def parse_textures(
        file_path: str,
        node: Node,
        verbose=False,
):
    """Parse textures from TXM (and TXV) package.

    The TXM and TXV files must be located in the same directory.

    Parameters
    ----------
    file_path : str
    node : Node
    verbose : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    file_path = Path(file_path)
    if file_path.is_file() and file_path.suffix.lower() == ".txv":
        file_path = os.path.splitext(file_path)[0] + ".TXM"

    binary_file = open(file_path, 'rb')
    node.name = os.path.splitext(os.path.basename(file_path))[0]
    g = BinaryReader(binary_file)
    g.endian = ">"

    current_offset = g.tell()
    node.offset = current_offset

    # Handle TXM and TXV file
    g.seek(current_offset)
    A = g.unpack("4B3i")
    logger.debug({
        "A": A,
        "A[6]": A[6],
    })
    g.seek(current_offset + 16)

    txv_file = os.path.splitext(file_path)[0] + ".TXV"
    logger.debug("txv_file: %s" % txv_file)
    try:
        with open(txv_file, 'rb') as f:
            txv_content = f.read()
    except FileNotFoundError:
        raise Exception(f"{txv_file} not found! Make sure it is in the same directory")
    dds_offset = list(find_substring_offset(txv_content, DDS_HEADER))
    dds_size = dds_offset[1]-dds_offset[0]
    logger.debug({
        "dds_offset": dds_offset,
        "dds_size": dds_size,
    })

    image_list = []
    for i, m in enumerate(range(A[6])):
        logger.debug("%s>" % ('=' * 200))
        B = g.i(7)
        tm = g.tell()
        g.seek(tm - 4 + B[6])
        name = g.find(b"\x00")
        current_total_offset = current_offset + A[4] + B[0]
        logger.debug({
            "current_offset": current_offset,
            "A[4]": A[4],
            "B[0]": B[0],
            "current_total_offset": current_total_offset,
        })
        g.seek(current_total_offset)

        texture_name = name + ".DDS"
        logger.debug({
            "texture_name": texture_name,
        })

        image_data = {
            "texture_name": texture_name,
            "dds_content": txv_content[dds_offset[i]:dds_offset[i] + dds_size - 4],
        }

        image_list.append(image_data)
        logger.info({
            "msg": "Successfully parsed texture",
            "texture_name": texture_name,
        })
        logger.debug("tm: %s" % tm)
        g.seek(tm)

    node.data["image_list"] = image_list
    g.close()


def parse_svo(
        svo_path: str,
        verbose=False,
):
    """Parse SVO package

    Parameters
    ----------
    svo_path : str
        Path to SVO file (e.g. 'path/to/PACKAGE.SVO')
    verbose : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    check_fourcc("FPS4", svo_path)
    svo_path = Path(svo_path)
    svo_size = svo_path.stat().st_size
    binary_file = open(svo_path, "rb")
    g = BinaryReader(binary_file)
    g.endian = ">"
    g.word(4)
    A = g.i(6)

    filesizes = []
    filenames = []
    for member in range(A[0]):
        offset = g.tell()
        B = g.i(3)
        filesizes.append(B)
        name = g.find(b"\x00")
        filenames.append(name)
        g.seek(offset + 44)

    offset = A[2]
    for idx, member in enumerate(range(A[0])):
        g.seek(offset)
        data = g.read(filesizes[member][1])
        g.seek(offset + filesizes[member][1])
        g.seekpad(128)
        offset = g.tell()
        if filenames[member]:
            logger.info(f"Progress completion: {round((offset / svo_size * 100), 2)}%")
            parsed_svo_path = svo_path.parent / svo_path.name.split('.')[0] / filenames[member]
            parsed_svo_path.parent.mkdir(parents=True, exist_ok=True)
            logger.debug({
                "msg": "Parsing SVO package",
                "package_name": filenames[member],
                "parsed_svo_path": str(parsed_svo_path),
            })
            with parsed_svo_path.open("wb") as f:
                f.write(data)

    g.close()
    logger.info(f"Parsed SVO {svo_path.name} completed.")


def parse_dat(
        dat_path: str,
        verbose=False,
):
    """Parse DAT file from SVO package

    Parameters
    ----------
    dat_path : str
        Path to DAT file (e.g. 'path/to/PACKAGE.DAT')
    verbose : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    check_fourcc("TLZC", dat_path)
    dat_path = Path(dat_path)
    binary_file = open(dat_path, "rb")
    g = BinaryReader(binary_file)
    g.word(4)
    g.i(5)

    dec_path = dat_path.parent / f"{dat_path.name}.dec"
    with open(dec_path, "wb") as dec_file:
        data = g.read(g.fileSize() - g.tell())
        data = zlib.decompress(data)
        dec_file.write(data)

    g.close()
    logger.info(f"Parse DAT as {dat_path.name}.dec completed.")


def parse_fps4(
        g: BinaryReader,
        n: int,
        parent_node: Node,
        verbose=False,
):
    """Parse FPS4 package

    Parameters
    ----------
    g : BinaryReader
    n : int
    parent_node : Node
    verbose : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    node = parent_node
    current_offset = g.tell()
    node.offset = current_offset
    fourcc = g.word(4)

    if fourcc != "FPS4":
        raise InvalidFourCCException("FPS4", fourcc)

    n += 4
    A = g.unpack("3i2H2i")
    logger.debug({
        "current_offset": current_offset,
        "fourcc": fourcc,
        "A": A,
        "n": n,
    })
    g.seek(current_offset + A[1])
    B = []
    for m in range(A[0]):
        B.append(g.i(A[3] // 4))

    for idx, b in enumerate(B):
        logger.debug({
            "msg": f"Loop B - {idx:04}",
        })
        if b[0] > 0:
            logger.debug({
                "b": b,
            })
            name = None
            if len(b) > 3:
                g.seek(current_offset + b[3])
                name = g.find(b"\x00")

            g.seek(current_offset + b[0])
            logger.debug({
                "name": name,
                "size": b[1],
                "n": n,
            })
            node.data[f"{idx:04}"] = {
                "name": name,
                "offset_start": b[0],
                "offset_end": b[0] + b[1],
            }

    logger.info(f"Parsed FPS4 completed")


def parse_dec_ext(
        dec_ext_path: str,
        verbose=False,
):
    """Parse unknown extracted files from parsed DAT.dec

    Parameters
    ----------
    dec_ext_path : str
        Path to unknown file (e.g. 'path/to/PACKAGE.DAT.dec.ext/0000')
    verbose : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    dec_ext_path = Path(dec_ext_path)

    binary_file = open(dec_ext_path, "rb")

    g = BinaryReader(binary_file)
    g.endian = ">"
    n = 0
    node = Node()
    parse_fps4(g, n, node)
    g.close()

    with open(dec_ext_path, "rb") as dec_ext_file:
        dec_ext_content = dec_ext_file.read()

    dec_ext_ext_path = Path(f"{dec_ext_path}.ext")
    for k, v in node.data.items():
        unknown_file_path = dec_ext_ext_path / f"{v['name']}.{k}"
        unknown_file_path.parent.mkdir(parents=True, exist_ok=True)
        with unknown_file_path.open("wb") as f:
            f.write(dec_ext_content[v["offset_start"]:v["offset_end"]])

    logger.info(f"Parse unknown files as {dec_ext_ext_path.name}.dec.ext completed.")


@dataclass
class Package:
    name: str = 'NONAME'
    offset: int = 0


def get_package_names(
        file_path: Path,
        generic_pattern=False,
):
    """Get package names

    Parameters
    ----------
    file_path : Path
    generic_pattern : bool
        Use generic regex pattern for package name. Default False.

    Returns
    -------
    list
        List of found package names matching the regex pattern

    """
    asset_name = file_path.name.split(".")[0]
    asset_name_underscore = "_".join([asset_name[:3], asset_name[3:]])
    if "_" in asset_name:
        asset_name_split = asset_name.split("_")
        if len(asset_name_split) > 4:
            asset_name_underscore = "_".join([
                asset_name_split[1][-3:],
                asset_name_split[2],
                asset_name_split[3],
            ])
        if 2 < len(asset_name_split) <= 4:
            asset_name_underscore = "_".join([
                asset_name_split[0][-3:],
                asset_name_split[1],
                asset_name_split[2],
            ])
        if len(asset_name_split) == 2:
            asset_name_underscore = "_".join([
                f"{asset_name_split[0][:3]}_{asset_name_split[0][3:]}",
                asset_name_split[1],
            ])
        logger.debug({
            "msg": "Split Asset Name",
            "asset_name_split": asset_name_split,
            "asset_name_underscore": asset_name_underscore,
        })
    with file_path.open("rb") as f:
        data = f.read()

    package_names = []
    current_offset = 0
    package_name_pattern = "".join([
        r"(\w_\w{3}_|\w{3}_|)",
        f"({asset_name_underscore}" + r"_\w{1,3}|" + f"{asset_name_underscore})",
        r"[.]\w{3}",
    ])
    if generic_pattern:
        package_name_pattern = r"([A-Z_\d]+)[.]\w{3}"
    print("package_name_pattern", package_name_pattern)
    logger.info({
        "msg": "Possible package name pattern",
        "pattern": package_name_pattern,
    })
    pattern = re.compile(package_name_pattern.encode())
    while True:
        match = pattern.search(data[current_offset:])
        if match is None:
            break
        package = Package()
        package.name = match.group(0).decode()
        package.offset = current_offset
        package_names.append(package)
        current_offset += match.end()

    return package_names


def parse_dec(
        dec_path: str,
        verbose=False,
):
    """Parse DEC file from parsed DAT

    Parameters
    ----------
    dec_path : str
        Path to DEC file (e.g. 'path/to/PACKAGE.DAT.dec')
    verbose : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    dec_path = Path(dec_path)

    # 1. Search for possible package names
    package_names = get_package_names(dec_path)

    # 2. Parse data
    binary_file = open(dec_path, "rb")

    g = BinaryReader(binary_file)
    g.endian = ">"
    n = 0
    node = Node()
    parse_fps4(g, n, node)
    g.close()

    # 3. Write out parsed data
    is_tex_package = False
    if "TEX" in dec_path.name:
        is_tex_package = True

    with open(dec_path, "rb") as dec_file:
        dec_content = dec_file.read()

    dec_ext_path = Path(f"{dec_path}.ext")
    dec_ext_path.mkdir(exist_ok=True)

    print("package_names", len(package_names))
    print("node.data.keys", len(node.data.keys()), node.data.keys())
    for idx, pn in enumerate(package_names):
        print(idx, pn.name)

    if len(package_names) < len(node.data.keys()):
        package_names = get_package_names(
            dec_path,
            generic_pattern=True,
        )[:len(node.data.keys())]
    print("package_names", len(package_names))
    print("node.data.keys", len(node.data.keys()), node.data.keys())
    for idx, pn in enumerate(package_names):
        print(idx, pn.name)

    verify_fourcc = True
    for idx, (k, v) in enumerate(node.data.items()):
        if len(package_names) == len(node.data.keys()):
            k = package_names[idx].name
            verify_fourcc = False

        print("\n\nk 1", k)
        fourcc = dec_content[v["offset_start"]:v["offset_start"]+4].hex().upper()
        fourcc_dds = dec_content[v["offset_start"]:v["offset_start"]+8].hex().upper()
        basename = k.split('.')[0]
        if is_tex_package:
            input_file = dec_path.name.split('.')
            k = '.'.join([
                input_file[0],
                input_file[1],
            ])
        if verify_fourcc and fourcc in TYPE_2_EXT_PC.keys():
            k = f"{basename}{TYPE_2_EXT_PC[fourcc]}"
        if DDS_HEADER.hex() in fourcc_dds:
            k = f"{basename}.TXV"
        print("k 2", k)
        with (dec_ext_path / k).open("wb") as f:
            f.write(dec_content[v["offset_start"]:v["offset_end"]])

    logger.info(f"Parse DAT dec as {dec_path.name}.ext completed.")
