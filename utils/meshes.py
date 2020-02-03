"""Utilities when dealing with meshes."""
import re
import os
import logging

logger = logging.getLogger(__name__)


def face_creation(node, debug=False):
    """Create faces from decoded mesh attributes.

    Parameters
    ----------
    node : Node
    debug : bool

    Notes
    -----
    - Based on delguoqing's Python 2 script for Vesperia 360.

    """
    mesh_lists = node.data["meshList"]
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
                logger.debug("")
            if debug:
                for triangle_idx, triangle in enumerate(mesh.triangleList):
                    logger.debug({
                        "triangle_idx": triangle_idx,
                        "triangle_value": triangle,
                    })


def round_float_value(value, decimal):
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


def write_mesh_to_obj(node, output_path):
    """Write out decoded mesh as Wavefront OBJ file.

    Parameters
    ----------
    node : Node
    output_path : str
        The chosen output directory path.

    Notes
    -----
    - Based on delguoqing's Python 2 script for Vesperia 360.

    """
    # TODO: Write out function to combine all OBJs and add face number with consecutive mesh total vertices
    if node.name != 'NONAME':
        package_dir_path = os.path.join(output_path, node.name)
        os.makedirs(package_dir_path, exist_ok=True)
        output_path = package_dir_path

    mesh_lists = node.data["meshList"]
    for mesh_list_idx, mesh_list in enumerate(mesh_lists):
        logger.debug("%s>" % ('=' * 200))
        logger.debug("Loop %s" % (mesh_list_idx+1))

        mesh_names = []
        for mesh_idx, mesh in enumerate(mesh_list):
            v = mesh.vertPosList
            vn = mesh.vertNormList
            uvs = mesh.vertUVList
            faces = mesh.triangleList
            logger.debug({
                "total v": len(v),
                "total vn": len(vn),
                "total uvs": len(uvs),
                "total faces": len(faces),
            })

            mesh_name = mesh.name
            mesh_names.append(mesh.name)
            mode = 'w'

            if mesh_idx > 0:
                logger.debug("%s ==> %s" % (mesh_names[mesh_idx-1], mesh_name))
            if mesh_idx > 0 and mesh_name == mesh_names[mesh_idx-1]:
                mesh_name = f"{mesh_name}_{mesh_idx}"
                logger.debug("Current mesh has same name as prior mesh! Using %s" % mesh_name)
                # mode = 'a'

            valid_mesh_name = str(mesh_name).strip().replace(' ', '_')
            valid_mesh_name = re.sub(r'(?u)[^-\w.]', '', valid_mesh_name)
            write_output_path = os.path.join(output_path, valid_mesh_name) + ".obj"
            logger.debug({
                "write_output_path": write_output_path,
                "mode": mode,
            })

            # Write mesh attributes into OBJ file
            with open(write_output_path, mode) as f:
                f.write(f"# submesh {mesh_idx+1}: {valid_mesh_name}" + "\n")
                f.write(f"g {valid_mesh_name}" + "\n")
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
                    if face_idx == 0:
                        f.write(f"# group {face['group']}" + "\n")
                    if face_idx > 0 and face['group'] != faces[face_idx-1]['group']:
                        f.write(f"# group {face['group']}" + "\n")
                    a = face['triangle'][0] + 1
                    b = face['triangle'][1] + 1
                    c = face['triangle'][2] + 1
                    f.write(f"f {a}/{a}/{a} {b}/{b}/{b} {c}/{c}/{c}" + "\n")

            logger.debug("Export %s successful" % write_output_path)
            logger.debug("")
