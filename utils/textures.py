"""Vesperia Tools Textures"""
import logging
from pathlib import Path

from parsers.models import Node

logger = logging.getLogger(__name__)


def write_to_dds(node: Node, output_path: str):
    output_path = Path(output_path)

    if node.name != 'NONAME':
        output_path = output_path / node.name

    for image in node.data["image_list"]:
        texture_name = image["texture_name"]
        texture_path = output_path / texture_name
        texture_path.parent.mkdir(exist_ok=True)
        dds_content = image["dds_content"]
        texture_path.write_bytes(dds_content)

    logger.info("Writing DDS textures completed.")
