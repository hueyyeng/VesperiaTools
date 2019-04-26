import os
import struct
import logging

from .models import (
    Bone,
    Mesh,
    Skeleton,
    Skin,
)
from utils.files import get_byte_struct
from utils.binaries import BinaryReader

logger = logging.getLogger(__name__)

PLATFORM_X360 = 0x4
PLATFORM_PC = 0x10
TYPE_CODE = 0x00010000


class Node:
    def __init__(self):
        self.name = ""
        self.children = []
        self.data = {}
        self.offset = None


def debug_mesh(node, verbose=False):
    if not node.data:
        raise Exception("No meshes found!")
    print("hashList:", node.data['hashList'])  # Important? Probably not for static mesh
    mesh_lists = node.data["meshList"]
    for mesh_list in mesh_lists:
        for mesh in mesh_list:
            print(f"{'='*64}>")
            print("meshName", mesh.name)
            print("vertUVList:", len(mesh.vertUVList))
            print("vertNormList:", len(mesh.vertNormList))
            print("vertPosList:", len(mesh.vertPosList))
            print("faceList:", len(mesh.faceList))
            print("triangleList:", len(mesh.triangleList))
            print("indiceList:", len(mesh.indiceList))  # Needed for face creation
            print("matIDList:", len(mesh.matIDList))
            print("matList:", len(mesh.matList))
            # print("skinIndiceList:", len(mesh.skinIndiceList))
            # print("skinWeightList:", len(mesh.skinWeightList))
            # print("DRAW:", mesh.DRAW)
            # print("TRIANGLE:", mesh.TRIANGLE)
            # print("QUAD:", mesh.QUAD)
            # print("TRISTRIP:", mesh.TRISTRIP)
            # print("SPLIT:", mesh.SPLIT)
            if verbose:
                for i, idx in enumerate(mesh.indiceList):
                    print(f"indice {i:03}: {idx}")


def getBones(g, n):
    # TODO: Currently Blender specific. Might want to look into adapting for Max/Maya?
    n += 4
    A = g.i(5) + g.H(2) + g.i(1)
    boneHashList = g.i(A[3])
    skeleton = Skeleton()
    skeleton.hashList = boneHashList
    for m in range(A[3]):
        bone = Bone()
        B = g.i(8)
        bone.parentID = B[2]
        t = g.tell()
        g.seek(t + B[6] - 8)
        bone.name = g.find('\x00')
        g.seek(t)
        skeleton.boneList.append(bone)
    for m in range(A[4]):
        g.f(4)
        g.f(4)
        g.f(4)
        g.f(4)
    for m in range(A[6]):
        g.i(3)
        g.f(6)
    for m in range(A[3]):
        g.f(3)
        rotMatrix = QuatMatrix(g.f(4)).resize4x4()
        posMatrix = VectorMatrix(g.f(3))
        skeleton.boneList[m].matrix = rotMatrix * posMatrix
        g.f(2)
    skeleton.NICE = True
    skeleton.draw()
    return skeleton


def getVertexData(mesh, g, v1, v2, v3, v4, n, debug=False):
    for i in range(v1):
        v_offset = g.tell()
        mesh.vertPosList.append(g.f(3))
        mesh.vertNormList.append(g.f(3))
        indice_offset = g.tell()
        if debug:
            print(f"v1 v_offset: {v_offset}, indice_offset: {indice_offset}")
        mesh.skinIndiceList.append(g.B(4))
        mesh.skinWeightList.append([0, 0, 0, 1])

    for i in range(v2):
        v_offset = g.tell()
        mesh.vertPosList.append(g.f(3))
        mesh.vertNormList.append(g.f(3))
        indice_offset = g.tell()
        if debug:
            print(f"v2 v_offset: {v_offset}, indice_offset: {indice_offset}")
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
            print(f"v3 v_offset: {v_offset}, indice_offset: {indice_offset}")
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
            print(f"v4 v_offset: {v_offset}, indice_offset: {indice_offset}")
        mesh.skinIndiceList.append(g.B(4))
        w1 = g.f(1)[0]
        w2 = g.f(1)[0]
        w3 = g.f(1)[0]
        w4 = 1.0 - w1 - w2 - w3
        mesh.skinWeightList.append([w4, w3, w2, w1])


def parse_uv(file_path, node, debug=False):
    readFile = open(file_path, 'rb')
    g = BinaryReader(readFile)

    curOff = g.tell()
    g.seek(curOff)

    # Parse UV in SPV File
    import math  # Handle NaN value
    import struct
    for meshes in node.data["meshList"]:
        for mesh in meshes:
            unpack_error = False
            if debug:
                print("Mesh UV:", mesh.name)
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
                    print(f"UV: {u}, {v} // offset:{g.tell()}")
                mesh.vertUVList.append([u, 1.0 - v])  # Fix UV?
            if unpack_error:
                print("WOOPS UV ERROR DURING UNPACKING. USING (0.0, 0.0) FOR AFFECTED UV")

    readFile.close()


def parse_mesh(file_path, node, debug=False):
    readFile = open(file_path, 'rb')
    node.name = os.path.splitext(os.path.basename(file_path))[0]
    g = BinaryReader(readFile)
    n = 0

    curOff = g.tell()
    node.offset = curOff

    # Handle SPM file
    print("=== DEBUG ===")
    g.seek(curOff)
    B = g.i(4)
    meshes = B[3]
    offset_seek = curOff + B[2]
    print("B:", B)
    print("Total Meshes:", B[3], "offset_seek:", offset_seek)
    # g.seek(offset_seek)
    g.seek(16)
    C = g.i(5)
    C1 = []
    print(f"Current offset: {g.tell()}")
    for m in range(meshes):
        a = g.i(8)
        print("g.i(8):", a)
        C1.append(a)
    for m in range(meshes):
        a = g.i(4)
        print("g.i(4):", a)
    node.data["meshList"] = []

    for i, m in enumerate(range(B[3])):
        print(f"{'='*32} Looping Mesh {i+1} {'='*32}>")
        D = g.i(15)
        print("D:", D, "D[13]:", D[13])
        tm = g.tell()
        name_offset = tm - 2 * 4 + D[13]
        g.seek(name_offset)
        name = g.find(b"\x00")
        print("name:", name, "name_offset:", name_offset)  # Name

        offset_1 = tm - 1 * 4 + D[14]
        print(f"offset_1: {tm} - 1 * 4 + {D[14]} = {offset_1}")
        g.seek(offset_1)

        meshList = []
        node.data["meshList"].append(meshList)

        offset_2 = tm - 9 * 4 + D[6]
        print(f"offset_2: {tm} - 9 * 4 + {D[6]} = {offset_2}")
        g.seek(offset_2)

        unknown = g.i(1)
        unkCount = unknown[0]
        print("unknown", unknown, "unkCount", unkCount)
        E = []
        for i in range(unkCount):
            mesh = Mesh()
            skin = Skin()
            mesh.name = name
            mesh.skinList.append(skin)
            mesh.diffuseID = D[4] - 1
            meshList.append(mesh)
            E1 = g.H(2)
            mesh.vertUVCount = E1[0]
            print("mesh.vertUVCount:", mesh.vertUVCount)
            E.append(E1)

        for i in range(unkCount):
            face_idx = E[i][1]
            indiceList = g.H(face_idx)
            print(f"indiceList size: {len(indiceList)} face_idx:{face_idx}")
            mesh = meshList[i]
            mesh.indiceList = indiceList

        mesh_offset = tm - 8 * 4 + D[7]
        print(f"mesh_offset: {tm} - 8 * 4 + {D[7]} = {mesh_offset}")
        g.seek(mesh_offset)
        print(f"C1[{m}]:", C1[m])
        if D[0] in (1792, 1024, 1026):
            print(f"VERDICT: Unskinned mesh? {name}")
            mesh = meshList[0]
            vertices = C1[m][4]
            if vertices == 0:
                # print(f"No vertices found! Probably BG or static mesh. Using D[8]: {D[8]}")
                # vertices = D[8]
                print(f"No vertices found! Probably BG or static mesh. Using D[10]: {D[10]}")
                vertices = D[10]
            for i in range(vertices):
                # Vertex Position
                v_offset = g.tell()
                vertex = g.f(3)
                if debug:
                    print("v:", vertex, "offset:", v_offset)
                mesh.vertPosList.append(vertex)

                # Vertex Normal
                vn_offset = v_offset
                if not D[0] in (1024, 1026):
                    vn_offset = v_offset + 888
                g.seek(vn_offset)
                vertex_normal = g.f(3)
                if debug:
                    print("vn:", vertex_normal, "offset:", vn_offset)
                mesh.vertNormList.append(vertex_normal)
                g.seek(v_offset + 12)

        elif D[0] in (258, 256):
            print(f"VERDICT: Skinned mesh? {name}")
            mesh = meshList[0]

            g.seek(mesh_offset)
            v1 = C1[m][4]
            v2 = C1[m][5]
            v3 = C1[m][6]
            v4 = C1[m][7]
            print("v", v1, v2, v3, v4)
            getVertexData(mesh, g, v1, v2, v3, v4, n, debug)
            mesh_range = unkCount - 1
            print("mesh_range:", mesh_range)
            for x in range(mesh_range):
                print(f"Loop Submesh {x}")
                mesh = meshList[1 + x]
                E = g.i(4)
                v1 = E[0]
                v2 = E[1]
                v3 = E[2]
                v4 = E[3]
                print("v", v1, v2, v3, v4)
                getVertexData(mesh, g, v1, v2, v3, v4, n, debug)

        else:
            print("D[1] =", D[1])
            print("g.f(12)) =", g.f(12))
            break

        g.seek(tm)

    F = g.i(C[0])
    node.data["hashList"] = F
    readFile.close()

    # Handle SPV file
    spv_file = os.path.splitext(file_path)[0] + ".SPV"
    print("spv_file:", spv_file)
    parse_uv(spv_file, node, debug=debug)
    print("\n")


def parse_material(file_path, node):
    readFile = open(file_path, 'rb')
    g = BinaryReader(readFile)

    curOff = g.tell()
    node.offset = curOff

    # Handle MTR file
    diffuseList = []
    g.seek(curOff)
    B = g.i(4)
    print("B", B)
    g.seek(curOff + B[2])

    count = g.i(1)[0]
    # print("count", count)

    lll = []
    for m in range(B[3]):
        C = g.i(8)
        D = g.i(C[0] * 2)
        lll.append(C)
    # print("lll", lll)
    for m in range(B[3]):
        tm = g.tell()
        # print("tm", tm)
        C = g.i(8)
        # print("C", C)
        imageList = []
        for i in range(8):
            print(f"== Loop {i+1} ==")
            print("Current offset is:", g.tell())
            c = C[i]
            name = None
            if c != 0:
                # print("c", c)
                g.seek(tm + 4 * i + c)
                name = g.find(b"\x00")
                if name:
                    print(f"name found: '{name}'")
                print("="*12 + ">")
            imageList.append(name)
        print(f"imageList {len(imageList)}:", imageList)
        print("=" * 12 + ">")
        diffuseList.append(imageList[1])

        g.seek(tm + 32)
    node.data["diffuseList"] = diffuseList
    print("diffuseList", diffuseList)
    readFile.close()
    return


def parse_skeleton(file_path, node):
    # TODO: Currently Blender specific. Might want to look into adapting for Max/Maya?
    readFile = open(file_path, 'rb')
    g = BinaryReader(readFile)

    curOff = g.tell()
    node.offset = curOff

    # Handle HRC file
    g.seek(curOff)
    skeleton = getBones(g, n)
    node.data["skeleton"] = skeleton

    readFile.close()


def find_substring_offset(context, substring):
    # TODO: Write docstring as this is currently specific for TXV file
    start = 0
    while True:
        start = context.find(substring, start)
        if start == -1: return
        yield start
        start += len(substring)  # use start += 1 to find overlapping matches


def parse_textures(file_path, node, output_path, debug=False):
    # TODO: Can be handle using HyoutaTools. Maybe omit Noesis as PNG conversion are optional?
    readFile = open(file_path, 'rb')
    g = BinaryReader(readFile)
    g.endian = ">"

    curOff = g.tell()
    node.offset = curOff

    # Handle TXM and TXV file
    g.seek(curOff)
    A = g.unpack("4B3i")
    print(A)
    print("A[6]", A[6])
    g.seek(curOff + 16)

    dds_header = b'\x44\x44\x53\x20\x7C'
    if not debug:
        txv_file = os.path.splitext(file_path)[0] + ".TXV"
        print(txv_file)
        try:
            with open(txv_file, 'rb') as f:
                txv_content = f.read()
        except FileNotFoundError:
            raise Exception(f"{txv_file} not found! Make sure it is in the same directory")
        dds_offset = list(find_substring_offset(txv_content, dds_header))
        dds_size = dds_offset[1]-dds_offset[0]
        print("dds_offset", dds_offset)
        print("dds_size", dds_size)

    node.data["imageList"] = {}
    for i, m in enumerate(range(A[6])):
        B = g.i(7)
        tm = g.tell()
        g.seek(tm - 4 + B[6])
        name = g.find(b"\x00")
        print(A, B)
        g.seek(curOff + A[4] + B[0])
        print("curOff + A[4] + B[0]:", curOff + A[4] + B[0])

        write_name = name + ".DDS"
        print(write_name, i)
        node.data["imageList"][name] = output_path + write_name

        if not debug:
            with open(output_path + write_name, 'wb') as f:
                gg = BinaryReader(f)
                # DDS file must start with DDS header
                dds_content = txv_content[dds_offset[i]:dds_offset[i] + dds_size - 4]
                gg.write(dds_content)

        print("tm", tm)
        print(f"{'='*32}>")
        g.seek(tm)

    readFile.close()


def parse_animation(file_path, node):
    # TODO: Currently Blender specific? Code looks incomplete.
    readFile = open(file_path, 'rb')
    g = BinaryReader(readFile)

    curOff = g.tell()
    node.offset = curOff

    # Handle ANM file
    g.seek(curOff)
    B = g.i(4)
    print(B)
    g.seek(curOff + B[2])
    C = g.B(4)
    for m in range(B[3]):
        tm = g.tell()
        D = g.unpack("4B2i")
        g.seek(tm + D[5] + 8)
        # print g.i(5)
        if D[4] == 257:
            v = g.unpack("i3f")
        if D[4] == 258:
            v = g.unpack("2i12B")
        if D[4] == 514:
            v = g.unpack("2i")
        if D[4] == 529:
            v = g.unpack("i2f")
        if D[4] == 530:
            v = g.unpack("i2f")
        if D[4] == 531:
            v = g.unpack("2i")
        if D[4] == 532:
            v = g.unpack("2i")
        if D[4] == 262:
            v = g.unpack("2i")

        g.seek(tm + 12)

    readFile.close()
