"""Utilities when dealing with meshes."""
import logging
import os
import re

from parsers.parser import Node

logger = logging.getLogger(__name__)


def face_creation(node: Node, verbose=False):
    """Create faces from decoded mesh attributes.

    Parameters
    ----------
    node : Node
    verbose : bool
        Display mesh's triangles values. Default False.

    Notes
    -----
    - Based on delguoqing's Python 2 script for Vesperia 360.

    """
    mesh_lists = node.data["mesh_list"]
    for mesh_list in mesh_lists:
        for mesh in mesh_list:
            if len(mesh.vertPosList) > 0:
                logger.debug("Creating faces for %s" % mesh.name)
                mesh.create_face()
                logger.debug({
                    "mesh.name": mesh.name,
                    "mesh.vertPosList": len(mesh.vertPosList),
                    "mesh.triangleList": len(mesh.triangleList)
                })
            if verbose:
                for triangle_idx, triangle in enumerate(mesh.triangleList):
                    logger.debug({
                        "triangle_idx": triangle_idx,
                        "triangle_value": triangle,
                    })


def round_float_value(value: float, decimal: int):
    """Round float value to a specific decimal points.

    Parameters
    ----------
    value : float
        The float value.
    decimal : int
        The decimal value of the rounded float value.
        E.g. Use 3 for 1.234 or 5 for 1.23456

    Returns
    -------
    float
        The rounded float value with specified decimal points.

    """
    rounded_value = "{:.%sf}" % decimal
    return rounded_value.format(value)


def write_mesh_to_obj(node: Node, output_path: str):
    """Write out decoded mesh as Wavefront OBJ file.

    Parameters
    ----------
    node : Node
    output_path : str
        The chosen output directory path.

    Returns
    -------
    str
        The output path.

    Notes
    -----
    - Based on delguoqing's Python 2 script for Vesperia 360.

    """
    if node.name != 'NONAME':
        package_dir_path = os.path.join(output_path, node.name)
        os.makedirs(package_dir_path, exist_ok=True)
        output_path = package_dir_path

    mesh_lists = node.data["mesh_list"]
    for mesh_list_idx, mesh_list in enumerate(mesh_lists):
        logger.debug("%s>" % ('=' * 200))
        logger.debug("Outer Loop %s" % mesh_list_idx)

        mesh_list_size = len(mesh_list)
        logger.debug("Mesh List Size: %s" % mesh_list_size)

        processed_mesh_names = []
        for mesh_idx, mesh in enumerate(mesh_list):
            logger.debug("Inner Loop %s" % mesh_idx)
            vertices_pos = mesh.vertPosList
            vertices_normal = mesh.vertNormList
            vertices_uvs = mesh.vertUVList
            faces = mesh.triangleList
            logger.debug({
                "total vertices_pos": len(vertices_pos),
                "total vertices_normal": len(vertices_normal),
                "total vertices_uvs": len(vertices_uvs),
                "total faces": len(faces),
            })

            mesh_name = mesh.name
            processed_mesh_names.append(mesh.name)
            write_mode = 'w'

            if mesh_list_size == 1 and mesh_name in processed_mesh_names:
                logger.debug("Current mesh has same name as prior found mesh! Using %s" % mesh_name)
                write_mode = "a"

            if mesh_idx > 0:
                logger.debug("%s ==> %s" % (processed_mesh_names[mesh_idx-1], mesh_name))
            if mesh_idx > 0 and mesh_name == processed_mesh_names[mesh_idx-1]:
                mesh_name = f"{mesh_name}_{mesh_idx}"
                logger.debug("Current mesh has same name as prior mesh! Using %s" % mesh_name)
                # write_mode = 'a'

            valid_mesh_name = str(mesh_name).strip().replace(' ', '_')
            valid_mesh_name = re.sub(r'(?u)[^-\w.]', '', valid_mesh_name)
            write_output_path = os.path.join(output_path, valid_mesh_name) + ".obj"
            logger.debug({
                "write_output_path": write_output_path,
                "write_mode": write_mode,
            })

            # Write mesh attributes into OBJ file
            with open(write_output_path, write_mode) as f:
                f.write(f"# submesh {mesh_idx+1}: {valid_mesh_name}" + "\n")
                f.write(f"o {valid_mesh_name}" + "\n")
                f.write("s 1" + "\n")

                for vertex in vertices_pos:
                    x = round_float_value(vertex[0], 6)
                    y = round_float_value(vertex[1], 6)
                    z = round_float_value(vertex[2], 6)
                    f.write(f"v {x} {y} {z}" + "\n")

                for vertex in vertices_normal:
                    x = round_float_value(vertex[0], 6)
                    y = round_float_value(vertex[1], 6)
                    z = round_float_value(vertex[2], 6)
                    f.write(f"vn {x} {y} {z}" + "\n")

                for uv in vertices_uvs:
                    u = round_float_value(uv[0], 6)
                    vertices_pos = round_float_value(uv[1], 6)
                    f.write(f"vt {u} {vertices_pos}" + "\n")

                for face_idx, face in enumerate(faces):
                    if face_idx == 0:
                        f.write(f"# group {face['group']}" + "\n")
                    if face_idx > 0 and face['group'] != faces[face_idx-1]['group']:
                        f.write(f"# group {face['group']}" + "\n")
                    a = face['triangle'][0] + 1
                    b = face['triangle'][1] + 1
                    c = face['triangle'][2] + 1
                    f.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}" + "\n")

            logger.debug("Export %s submesh successful" % write_output_path)

        logger.debug("Done exporting %s" % node.name)
        return output_path
