"""Materials Utils."""
import logging
import os

from parsers.models import Node

logger = logging.getLogger(__name__)


def write_to_mtl(node: Node, output_path: str):
    """Write out decoded material as Wavefront OBJ MTL file.

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

    material_lists = node.data["material_list"]
    for material_list_idx, material_list in enumerate(material_lists):
        logger.debug("%s>" % ('=' * 200))
        logger.debug("Outer Loop %s" % material_list_idx)

        material_list_size = len(material_list)
        logger.debug("Material List Size: %s" % material_list_size)

        for material in material_list:
            material_name = material["mtl"]
            textures = material["tex"]
            write_output_path = os.path.join(output_path, material_name) + ".mtl"
            with open(write_output_path, "w") as f:
                f.write(f"newmtl {material_name}" + "\n")
                for texture in textures:
                    tex_type = "Kd"
                    if texture.endswith("H"):
                        # TODO: Revisit in future to decide either Ks or Ns for highlight
                        tex_type = "Ns"

                    tex_format = "dds"
                    f.write(f"map_{tex_type} {texture}.{tex_format}" + "\n")

            logger.debug("Export %s submaterial successful" % write_output_path)

    logger.debug("Done exporting %s materials" % node.name)
    return output_path
