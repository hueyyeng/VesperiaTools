import os
import glob
import logging
from constants.tales import UNPACKED_LEFTOVER_FILES
from parsers.parser import (
    Node,
    debug_mesh,
    parse_material,
    parse_mesh,
    parse_textures,
    parse_uv,
)
from textures import extract_textures_from_package
from utils.files import (
    unpack_dat,
    unpack_chara_dat,
    cleanup_leftover_files,
)

logging.basicConfig(level=logging.DEBUG)


# packages = glob.glob("I:/TOV/PC/map/Z*.DAT")
# for package in packages:
#     extract_textures_from_package(package)

# == Extract textures ==
map_path = "I:/TOV/PC/map/XRGD00.DAT"
# ch_tex_path = "I:/TOV/PC/_tmp/tmp/NONAME0"
ch_tex_path = "I:/TOV/PC/_tmp/_splitter/EP_490_060.DAT/NONAME0"
# common_tex_path = "I:/TOV/PC/_tmp/_splitter/BTL_COMMON.DAT.ext/0002.ext/OBJ_B500_LINE_00.dec.ext"
# extract_textures_from_package(ch_tex_path)

# == Unpack DAT ==
# chara_path = "I:/TOV/PC/chara/EP_490_060.DAT"
chara_path = "I:/TOV/PC/_tmp/EST_C000.DAT"
# btl_chara_path = "I:/TOV/PC/_tmp/_splitter/BTL_EP_490_060_0.DAT"
# common_path = "I:/TOV/PC/npc/CAQ_T01.DAT.dec.ext/0002"
# unpack_dat(chara_path, decompress_only=False, deep_extract=True)

# == Unpack CH DAT and cleanup unpacked leftover files ==
chara_360 = "I:/TOV/360/_tmp/COMMONPARTS.DAT.dec"
# chara_PC = "I:/TOV/PC/_tmp/BTL_ENEMY_1721.DAT.dec"
chara_PC = "I:/TOV/PC/_tmp/_splitter/BTL_ENEMY_1721.DAT.dec"
# chara_PC = "I:/TOV/PC/_tmp/_DLC/EST_C000.dat.dec"
# unpack_chara_dat(chara_PC, create_output_dir=True)
# cleanup_leftover_files(chara_PC, UNPACKED_LEFTOVER_FILES)


# ========   PC Version Extraction   ============

# == Parse Material ==
chara_material_PC_path = "I:/TOV/PC/_tmp/_DLC/EST_C000.dat/NONAME0/PC_EST_C000_HEAD_EST_C000_HEAD.MTR"
chara_material_360_path = "I:/TOV/360/_tmp/COMMONPARTS.DAT/NONAME0/PC_EST_C000_HEAD_EST_C000_HEAD.MTR"
# parse_material(chara_material_360_path, endian=">")
# parse_material(chara_material_PC_path2, endian="<")


# == Parse Textures ==
chara_txm_PC_path = "I:/TOV/PC/_tmp/_splitter/BTL_ENEMY_1721.DAT/NONAME0/PC_EST_C001_HEAD_EST_C001_HEAD.TXM"
chara_txm_PC_path2 = "I:/TOV/PC/_tmp/_splitter/BTL_ENEMY_1721.DAT/NONAME0/PC_EST_C000_HAIR_EST_C000_HAIR.TXM"
chara_txv_PC_path = "I:/TOV/PC/_tmp/_splitter/BTL_ENEMY_1721.DAT/NONAME0/PC_EST_C001_HEAD_EST_C001_HEAD.TXV"


# == Chain Parsing ==
# TODO: Figure out MTR, HRC, ANM, TXM, SPM one stop solution
# Credit: Szkaradek123 from Xentax forum

BG_SINGLE_MESH_SPM = "I:\TOV\PC\map\BOAT01.DAT.dec.ext\MDL_BOA_T01_R.SPM"
DOG = "I:/TOV/PC/map/CAOI01_00.DAT.dec.ext/MDL_CAP_I01_00_DOG.SPM"
MDL_CAP_I01_SPM = "I:/TOV/PC/map/CAOI01_00.DAT.dec.ext/MDL_CAP_I01_00.SPM"
POR_T01_HUNE_SPM = "I:/TOV/PC/map/PORT03.DAT.dec.ext/MDL_POR_T01_HUNE.SPM"
POR_T02_SAKU01_SPM = "I:/TOV/PC/map/PORT03.DAT.dec.ext/POR_T02_SAKU01.SPM"
POR_T02_MOVE01_SPM = "I:/TOV/PC/map/PORT03.DAT.dec.ext/POR_T02_MOVE01.SPM"
MOL_CAPI00_00_S_SPM = "I:/TOV/PC/map/CAPI00_00.DAT.dec.ext/MOL_CAPI00_00_S.SPM"
CAQ_T10_BG_SPM = "I:/TOV/PC/map/CAQT10.DAT.dec.ext/MDL_CAQ_T10_BG.SPM"
CAQ_T10_SPM = "I:/TOV/PC/map/CAQT10.DAT.dec.ext/MDL_CAQ_T10.SPM"
EST_HAIR_SPM = "I:/TOV/PC/_tmp/_splitter/BTL_ENEMY_1721.DAT/NONAME0/PC_EST_C000_HAIR_EST_C000_HAIR.SPM"
EST_FOOT_L_SPM = "I:/TOV/PC/_tmp/_splitter/BTL_ENEMY_1721.DAT/NONAME0/PC_EST_C000_FOOT_L_EST_C000_FOOT_L.SPM"
EST_LEG_SPM = "I:/TOV/PC/_tmp/_splitter/BTL_ENEMY_1721.DAT/NONAME0/PC_EST_C000_LEG_EST_C000_LEG.SPM"
EST_HEAD_SPM = "I:/TOV/PC/_tmp/_splitter/BTL_ENEMY_1721.DAT/NONAME0/PC_EST_C001_HEAD_EST_C001_HEAD.SPM"

node = Node()
node2 = Node()
node3 = Node()
# parse_material(chara_material_PC_path, node)
# parse_mesh(chara_mesh_PC_path, node)
# parse_textures(chara_txm_PC_path, node, output_path="I:/TOV/PC/_tmp/_test/", debug=True)

# =============

tmp_path = "I:/TOV/_tmp"


def face_creation(node, debug=False):
    # Handle face creation using delguoqing method
    mesh_lists = node.data["meshList"]
    for mesh_list in mesh_lists:
        for mesh in mesh_list:
            print("mesh.name:", mesh.name, "mesh.vertPosList:", len(mesh.vertPosList))
            if len(mesh.vertPosList) > 0:
                print(f"Creating faces for {mesh.name}")
                mesh.create_face()
                print(f"Total triangles: {len(mesh.triangleList)}")
            if debug:
                for i, triangle in enumerate(mesh.triangleList):
                    print(f"Triangle {i}: {triangle}")


def round_float_value(value, precision):
    rounded_value = "{:.%sf}" % precision
    return rounded_value.format(value)


def export_obj(node, split=False, output_path=None):
    mesh_lists = node.data["meshList"]
    mesh_names = []
    for mesh_list_idx, mesh_list in enumerate(mesh_lists):
        print(f"{'='*64}>")
        print(f"Loop {mesh_list_idx+1}")

        for mesh_idx, mesh in enumerate(mesh_list):
            v = mesh.vertPosList
            vn = mesh.vertNormList
            uvs = mesh.vertUVList
            faces = mesh.triangleList
            print("vertices:", len(v), "uvs", len(uvs))

            mesh_name = mesh.name
            mesh_names.append(mesh.name)
            print(mesh_names)
            mode = 'w'

            if mesh_list_idx > 0:
                print(f"previous name: {mesh_name} >>> new name: {mesh_names[mesh_list_idx-1]}")
            if mesh_list_idx > 0 and mesh_name == mesh_names[mesh_list_idx-1]:
                if split:
                    mesh_name = f"{mesh_name}_{mesh_list_idx}"
                else:
                    print("Detected mesh with same name! Appending to existing file.")
                    mode = 'a'

            # write_output_path = os.path.join(output_path, node.name) + ".obj"
            # if split:
            #     if mesh_idx > 0 and mesh_name == mesh_names[mesh_idx - 1]:
            #         # mesh_name = f"{mesh_name}_{mesh_idx}"
            #         print("Detected mesh with same name! Appending to existing file.")
            #         mode = 'a'
            #     write_output_path = os.path.join(output_path, mesh_name) + ".obj"

            write_output_path = os.path.join(output_path, mesh_name) + ".obj"
            print(write_output_path)

            # Write mesh attributes into OBJ file
            with open(write_output_path, mode) as f:
                f.write(f"# submesh {mesh_idx+1}: {mesh_name}" + "\n")
                f.write(f"g {mesh_name}" + "\n")
                f.write("s 1" + "\n")
                for vertex in v:
                    x = round_float_value(vertex[0], 6)
                    y = round_float_value(vertex[1], 6)
                    z = round_float_value(vertex[2], 6)
                    f.write(f"v {x} {y} {z}" + "\n")
                for vertex in vn:
                    x = round_float_value(vertex[0], 6)
                    y = round_float_value(vertex[1], 6)
                    z = round_float_value(vertex[2], 6)
                    f.write(f"vn {x} {y} {z}" + "\n")
                for uv in uvs:
                    u = round_float_value(uv[0], 6)
                    v = round_float_value(uv[1], 6)
                    f.write(f"vt {u} {v}" + "\n")
                for face_idx, face in enumerate(faces):
                    if face_idx > 0 and face['group'] != faces[face_idx-1]['group']:
                        f.write(f"# group {face['group']}" + "\n")
                    a = face['triangle'][0] + 1
                    b = face['triangle'][1] + 1
                    c = face['triangle'][2] + 1
                    f.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}" + "\n")

            print(f"Export {write_output_path} successful")


# parse_mesh(EST_LEG_SPM, node3, debug=False)
# parse_mesh(EST_HEAD_SPM, node3, debug=False)

parse_mesh(BG_SINGLE_MESH_SPM, node2, debug=False)
# parse_mesh("I:\TOV\PC\_tmp\_splitter\EP_490_060.DAT\\NONAME0\ENPC_ARE_C000_HEAD_ARE_C000_HEAD.SPM", node2, debug=False)

# SAKU01 NameOffset: 7692
# parse_mesh(POR_T02_SAKU01_SPM, node2, debug=False)

# HUNE NameOffset: 672
# parse_mesh(POR_T01_HUNE_SPM, node2, debug=False)

# MOVE01 NameOffset: 42552
# Food for thought: D[13] + 136 offset for valid SPM file?
# parse_mesh(POR_T02_MOVE01_SPM, node2, debug=False)
face_creation(node2, debug=False)
debug_mesh(node2)
export_obj(node2, split=False, output_path=tmp_path)

# parse_mesh(EST_HEAD_SPM, node, debug=False)
# face_creation(node, debug=False)
# debug_mesh(node, verbose=False)
# export_obj(node, split=True, output_path=tmp_path)
