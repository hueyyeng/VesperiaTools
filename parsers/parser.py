"""Parser for Vesperia data objects."""
import os
import math  # Handle NaN value
import struct
import logging

from .models import Mesh
from utils.binaries import BinaryReader

logger = logging.getLogger(__name__)


class Node:
    """Node for decoded meshes.

    Contains attributes needed for exporting to external format (e.g. Wavefront OBJ)

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    def __init__(self):
        self.name = "NONAME"
        self.children = []
        self.data = {}
        self.offset = None


def debug_mesh(node, verbose=False):
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
        "hashList": node.data['hashList'],  # Important? Probably not for static mesh
    })
    mesh_lists = node.data["meshList"]
    for idx, mesh_list in enumerate(mesh_lists):
        logger.debug("Total meshes for Loop %s : %s" % (idx + 1, len(mesh_list)))
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
        logger.debug("")


def getVertexData(mesh, g, v1, v2, v3, v4, n, debug=False):
    """Get vertex data for skinned mesh.

    Parameters
    ----------
    mesh : mesh
    g : g
    v1 : int
    v2 : int
    v3 : int
    v4 : int
    n : int
    debug : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    for i in range(v1):
        v_offset = g.tell()
        mesh.vertPosList.append(g.f(3))
        mesh.vertNormList.append(g.f(3))
        indice_offset = g.tell()
        if debug:
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
        if debug:
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
        if debug:
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
        if debug:
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


def parse_uv(file_path, node, debug=False):
    """Parse UV coordinates value.

    Parameters
    ----------
    file_path : str
        Path to SPV file (e.g. 'path/to/PACKAGE.SPV')
    node : Node
    debug : bool

    Notes
    -----
    - Based on delguoqing's Python 2 script for Vesperia 360.
    - Currently has known issue with parsing UV for BG meshes.

    """
    readFile = open(file_path, 'rb')
    g = BinaryReader(readFile)

    curOff = g.tell()
    g.seek(curOff)

    # TODO: Figure out BG funky UV packing
    # Parse UV in SPV File
    for meshes in node.data["meshList"]:
        for mesh in meshes:
            unpack_error = False
            if debug:
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
                if debug:
                    logger.debug({
                        "UV": "%f, %f" % (u, v),
                        "offset": g.tell(),
                    })
                mesh.vertUVList.append([u, 1.0 - v])  # Fix UV?
                # mesh.vertUVList.append([u, v])  # Fix UV?
            if unpack_error:
                logger.warning("UV ERROR DURING UNPACKING. USING (0.0, 0.0) FOR AFFECTED UV")

    readFile.close()


def parse_mesh(file_path, node, debug=False):
    """Parse mesh data from SPM (and SPV) package.

    The SPM and SPV files must be located in the same directory.

    Parameters
    ----------
    file_path : str
        Path to SPM file (e.g. 'path/to/PACKAGE.SPM')
    node : Node
    debug : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    readFile = open(file_path, 'rb')
    node.name = os.path.splitext(os.path.basename(file_path))[0]
    g = BinaryReader(readFile)
    n = 0

    curOff = g.tell()
    node.offset = curOff

    # Handle SPM file
    logger.debug("=== DEBUG MESH PARSER ===")
    g.seek(curOff)
    B = g.i(4)
    meshes = B[3]
    offset_seek = curOff + B[2]
    logger.debug({
        "B": B,
        "total_meshes": B[3],
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
    node.data["meshList"] = []

    for i, m in enumerate(range(B[3])):
        logger.debug("")
        logger.debug("%s Looping Mesh %s %s>" % (('=' * 64), (i + 1), ('=' * 64)))
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

        meshList = []
        node.data["meshList"].append(meshList)

        offset_2 = tm - 9 * 4 + D[6]
        logger.debug("offset_2: %s - 9 * 4 + %s = %s" % (tm, D[6], offset_2))
        g.seek(offset_2)

        unknown = g.i(1)
        unkCount = unknown[0]
        logger.debug({
            "unknown": unknown,
            "unkCount": unkCount,
        })
        E = []

        # TODO: Maybe combine more than 1 unkCount mesh into giganto mesh?
        # if unkCount == 1:
        if unkCount >= 1:
            # Original approach. Works great for CH mesh.
            logger.debug("FOUND %s SUBMESHES" % unkCount)
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
                meshList.append(mesh)
                E.append(E1)

            for i in range(unkCount):
                face_idx = E[i][1]
                indiceList = g.H(face_idx)
                logger.debug("indiceList size: %s face_idx: %s" % (len(indiceList), face_idx))
                mesh = meshList[i]
                mesh.indiceList = indiceList

            logger.debug("mesh.indiceList: %s" % len(mesh.indiceList))

        else:
            # Combined approach. Faces still incorrectly parsed.
            logger.debug("FOUND %s SUBMESHES" % unkCount)
            mesh = Mesh()
            mesh.name = name
            mesh.diffuseID = D[4] - 1
            for i in range(unkCount):
                E1 = g.H(2)
                logger.debug({
                    "E1": E1,
                })
                mesh.vertUVCount += E1[0]
                E.append(E1)
            logger.debug("mesh.vertUVCount: %s" % mesh.vertUVCount)

            indiceList = ()
            for i in range(unkCount):
                face_idx = E[i][1]
                indices = g.H(face_idx)
                # logger.debug(indices)
                logger.debug("indices size: %s face_idx: %s" % (len(indices), face_idx))
                indiceList += indices
                # indiceList.append(indices)
            # mesh.indiceList = indiceList[0]
            mesh.indiceList = indiceList
            meshList.append(mesh)

            logger.debug("mesh.indiceList: %s" % len(mesh.indiceList))

        mesh_offset = tm - 8 * 4 + D[7]
        logger.debug("mesh_offset: %s - 8 * 4 + %s = %s" % (tm, D[7], mesh_offset))
        g.seek(mesh_offset)
        logger.debug("C1[%s]: %s" % (m, C1[m]))
        if D[0] in (1792,):
            logger.debug("VERDICT: Unskinned mesh? %s" % name)
            mesh = meshList[0]
            vertices = C1[m][4]
            if vertices == 0:
                # NOTE: Don't bother trying other index values besides D[10]
                logger.debug("No vertices found! Probably BG or static mesh. Using D[10]: %s" % D[10])
                vertices = D[10]
            for i in range(vertices):
                # Vertex Position
                v_offset = g.tell()
                vertex = g.f(3)
                if debug:
                    logger.debug({
                        "v": vertex,
                        "v_offset": v_offset,
                    })
                mesh.vertPosList.append(vertex)

                # Vertex Normal
                vn_offset = v_offset
                if not D[0] in (1024, 1026):
                    vn_offset = v_offset + 888
                g.seek(vn_offset)
                vertex_normal = g.f(3)
                if debug:
                    logger.debug({
                        "vn": vertex_normal,
                        "vn_offset": vn_offset,
                    })
                mesh.vertNormList.append(vertex_normal)
                g.seek(v_offset + 12)

        elif D[0] in (1024, 1026, 1027):
            logger.debug("VERDICT: BG mesh? %s" % name)
            mesh = meshList[0]
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
                if debug:
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
                if debug:
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

            for idx, mesh in enumerate(meshList):
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
            mesh = meshList[0]

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
            getVertexData(mesh, g, v1, v2, v3, v4, n, debug)
            mesh_range = unkCount - 1
            logger.debug("mesh_range: %s" % mesh_range)
            for x in range(mesh_range):
                logger.debug("Loop Subesh %s" % x)
                mesh = meshList[1 + x]
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
                getVertexData(mesh, g, v1, v2, v3, v4, n, debug)

        else:
            logger.warning({
                "msg": "Invalid mesh object.",
                "D[1]": D[1],
                "g.f(12)": g.f(12),
            })
            break

        g.seek(tm)

    F = g.i(C[0])
    node.data["hashList"] = F
    readFile.close()

    # Handle SPV file
    spv_file = os.path.splitext(file_path)[0] + ".SPV"
    logger.debug({
        "spv_file": spv_file,
    })
    parse_uv(spv_file, node, debug=debug)


def parse_material(file_path, node):
    """Parse material from MTR package.

    Parameters
    ----------
    file_path : str
        Path to DAT file (e.g. 'path/to/PACKAGE.MTR')
    node : Node

    Notes
    -----
    Haven't tested it as the original script by Szkaradek123 is for Blender 2.49.
    Will revisit this in future updates.

    """
    readFile = open(file_path, 'rb')
    g = BinaryReader(readFile)

    curOff = g.tell()
    node.offset = curOff

    # Handle MTR file
    diffuseList = []
    g.seek(curOff)
    B = g.i(4)
    g.seek(curOff + B[2])

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

    # Loop through materials?
    for m in range(B[3]):
        logger.debug("%s>" % ('=' * 200))
        tm = g.tell()
        C = g.i(8)
        logger.debug({
            "tm": tm,
            "C": C,
        })
        imageList = []
        for i in range(8):
            logger.debug("%s Loop %s %s>" % (('=' * 24), (i + 1), ('=' * 24)))
            logger.debug("Current offset is: %s" % g.tell())
            c = C[i]
            name = None
            if c != 0:
                logger.debug("%s>" % ('=' * 32))
                g.seek(tm + 4 * i + c)
                name = g.find(b"\x00")
                if name:
                    logger.debug("Name found: %s" % name)
            imageList.append(name)

        logger.debug({
            "total_images": len(imageList),
            "imageList": imageList,
        })
        diffuseList.append(imageList[1])
        g.seek(tm + 32)

    node.data["diffuseList"] = diffuseList
    logger.debug({
        "diffuseList": diffuseList,
    })
    readFile.close()


def find_substring_offset(context, substring):
    """Find offset value between reoccurring substring in a context.

    Currently specific for TXV package.

    Parameters
    ----------
    context : bytes str
        The data with reoccurring substring
    substring : bytes str
        The substring value

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


def parse_textures(file_path, node, output_path, debug=False):
    """Parse textures from TXM (and TXV) package.

    The TXM and TXV files must be located in the same directory.

    Parameters
    ----------
    file_path : str
    node : Node
    output_path : str
    debug : bool

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    # TODO: Can be handle using HyoutaTools. Maybe omit Noesis as PNG conversion are optional?
    readFile = open(file_path, 'rb')
    g = BinaryReader(readFile)
    g.endian = ">"

    curOff = g.tell()
    node.offset = curOff

    # Handle TXM and TXV file
    g.seek(curOff)
    A = g.unpack("4B3i")
    logger.debug({
        "A": A,
        "A[6]": A[6],
    })
    g.seek(curOff + 16)

    dds_header = b'\x44\x44\x53\x20\x7C'
    txv_file = os.path.splitext(file_path)[0] + ".TXV"
    logger.debug("txv_file: %s" % txv_file)
    try:
        with open(txv_file, 'rb') as f:
            txv_content = f.read()
    except FileNotFoundError:
        raise Exception(f"{txv_file} not found! Make sure it is in the same directory")
    dds_offset = list(find_substring_offset(txv_content, dds_header))
    dds_size = dds_offset[1]-dds_offset[0]
    logger.debug({
        "dds_offset": dds_offset,
        "dds_size": dds_size,
    })

    node.data["imageList"] = {}
    for i, m in enumerate(range(A[6])):
        logger.debug("%s>" % ('=' * 200))
        B = g.i(7)
        tm = g.tell()
        g.seek(tm - 4 + B[6])
        name = g.find(b"\x00")
        current_total_offset = curOff + A[4] + B[0]
        logger.debug({
            "curOff": curOff,
            "A[4]": A[4],
            "B[0]": B[0],
            "current_total_offset": current_total_offset,
        })
        g.seek(current_total_offset)

        write_name = name + ".DDS"
        node.data["imageList"][name] = output_path + write_name
        logger.debug({
            "output_path": output_path,
            "write_name": write_name,
        })

        with open(output_path + write_name, 'wb') as f:
            dds_file = BinaryReader(f)
            # DDS file must start with DDS header
            dds_content = txv_content[dds_offset[i]:dds_offset[i] + dds_size - 4]
            dds_file.write(dds_content)

        logger.debug("tm: %s" % tm)
        g.seek(tm)

    readFile.close()
