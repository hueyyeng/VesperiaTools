"""VesperiaTools Exporter."""
import logging
import os

from parsers.parser import (
    Node,
    debug_mesh,
    parse_mesh,
    parse_material,
    parse_textures,
)
from utils.materials import write_to_mtl
from utils.meshes import (
    face_creation,
    write_to_obj,
)

logger = logging.getLogger(__name__)


def join_mtl_files(mtl_files_path: str, mtl_name: str = None):
    """Join MTL files

    As Vesperia store meshes in SPM as split submeshes, this will join
    the separated exported OBJ material files into one MTL file.

    Parameters
    ----------
    mtl_files_path : str
        The path containing the OBJ material files for joining
    mtl_name : str or None
        The joined MTL name. If None, will default to 'all.mtl'

    Notes
    -----
    - Based on delguoqing's Python 2 script for Vesperia 360

    """
    file_names = os.listdir(mtl_files_path)
    mtls = set()
    for file_name in file_names:
        mtl_file_path = os.path.join(mtl_files_path, file_name)
        if file_name.endswith("all.mtl"):
            continue

        with open(mtl_file_path, "r") as mtl_file:
            mtls.add(mtl_file.read())

    if not mtl_name:
        mtl_name = "all.mtl"

    joined_mtl_path = os.path.join(
        mtl_files_path,
        mtl_name,
    )
    with open(joined_mtl_path, "w") as joined_mtl_file:
        for mtl in mtls:
            joined_mtl_file.write(mtl)


def export_wavefront_mtl(
    input_path: str,
    output_path: str,
    node: Node = None,
    verbose=False,
):
    node = Node() if node is None else node
    parse_material(input_path, node, verbose=False)
    write_to_mtl(node, output_path)


def join_obj_files(obj_files_path: str, obj_name: str = None):
    """Join OBJ files

    As Vesperia store meshes in SPM as split submeshes, this will join
    the separated exported OBJ submeshes into one OBJ file.

    Parameters
    ----------
    obj_files_path : str
        The path containing the OBJ submeshes files for joining
    obj_name : str or None
        The joined OBJ name. If None, will default to 'all.obj'

    Notes
    -----
    - Based on delguoqing's Python 2 script for Vesperia 360

    """
    file_names = os.listdir(obj_files_path)

    lines = []
    v_base = vn_base = vt_base = 0

    # TODO: Work on material handling in future pull request
    # lines.append("mtllib all.mtl\n")

    for file_name in file_names:
        if file_name.endswith("all.obj"):
            continue
        v = vt = vn = 0

        obj_file_path = os.path.join(obj_files_path, file_name)
        obj_file = open(obj_file_path, "r")
        obj_file.readline()  # drop the mtllib line

        line = obj_file.readline()
        while line != "":
            if not line.startswith("f"):
                lines.append(line)
            else:
                vertex_data_list = line.split(" ")[1:]
                new_line = "f "
                for vertex_data in vertex_data_list:
                    _v, _vt, _vn = map(int, vertex_data.split("/"))
                    new_line += "%d/%d/%d " % (_v + v_base, _vt + vt_base, _vn + vn_base)
                lines.append(new_line + "\n")

            if line.startswith("v "):
                v += 1
            elif line.startswith("vn "):
                vn += 1
            elif line.startswith("vt "):
                vt += 1
            line = obj_file.readline()

        v_base += v
        vt_base += vt
        vn_base += vn
        obj_file.close()

    if not obj_name:
        obj_name = "all.obj"
    joined_obj_path = os.path.join(
        obj_files_path,
        obj_name,
    )
    with open(joined_obj_path, "w") as joined_obj_file:
        joined_obj_file.writelines(lines)


def export_wavefront_obj(
        input_path: str,
        output_path: str,
        node: Node = None,
        verbose=False,
):
    """Export parsed meshes as Wavefront OBJ files.

    Parameters
    ----------
    input_path : str
        Path to SPM package.
    output_path : str
        Path to exported OBJ files.
    node : Node or None
        Node object. Default None.
    verbose : bool
        Set True for verbose debug mesh output. Default False.

    """
    node = Node() if node is None else node
    parse_mesh(input_path, node, verbose=False)
    face_creation(node, verbose=False)
    if verbose:
        debug_mesh(node)
    exported_obj_path = write_to_obj(node, output_path=output_path)
    logger.debug({
        "msg": "Successfully export Wavefront OBJs",
        "file_path": input_path,
        "output_path": output_path,
    })
    join_obj_files(exported_obj_path)
    logger.debug({
        "msg": "Successfully joined OBJs as all.obj",
        "exported_obj_path": exported_obj_path,
    })
