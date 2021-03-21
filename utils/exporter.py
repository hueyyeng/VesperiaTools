"""VesperiaTools Exporter."""
import logging

from parsers.parser import (
    Node,
    debug_mesh,
    parse_mesh,
)
from utils.meshes import (
    face_creation,
    write_mesh_to_obj,
)

logger = logging.getLogger(__name__)


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
    write_mesh_to_obj(node, output_path=output_path)
    logger.debug({
        "msg": "Successfully export Wavefront OBJs",
        "file_path": input_path,
        "output_path": input_path,
    })
