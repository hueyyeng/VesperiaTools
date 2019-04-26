"""VesperiaTools Exporter."""
import logging
from parsers.parser import (
    Node,
    debug_mesh,
    parse_mesh,
)
from utils.meshes import face_creation, write_mesh_to_obj

logger = logging.getLogger(__name__)


def export_wavefront_obj(input_path, output_path, node=None, debug=False):
    """Export parsed meshes as Wavefront OBJ files.

    Parameters
    ----------
    input_path : str
        Path to SPM package.
    output_path : str
        Path to exported OBJ files.
    node : Node
    debug : bool

    """
    node = Node() if node is None else node
    parse_mesh(input_path, node, debug=False)
    face_creation(node, debug=False)
    if debug:
        debug_mesh(node)
    write_mesh_to_obj(node, output_path=output_path)
    logger.debug({
        "msg": "Successfully export Wavefront OBJs",
        "file_path": input_path,
        "output_path": input_path,
    })
