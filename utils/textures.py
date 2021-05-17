"""Vesperia Tools Textures"""
import logging
from pathlib import Path

from parsers.parser import Node

logger = logging.getLogger(__name__)


def write_to_dds(node: Node, output_path: str):
    output_path = Path(output_path)
    output_path.mkdir(exist_ok=True)

    if node.name != 'NONAME':
        output_path = output_path / node.name

    for image in node.data["image_list"]:
        texture_name = image["texture_name"]
        texture_path = output_path / texture_name
        dds_content = image["dds_content"]
        with open(texture_path, 'wb') as dds_file:
            dds_file.write(dds_content)

    logger.info("Writing DDS textures completed.")
