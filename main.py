import logging
from textures import extract_textures_from_package

logging.basicConfig(level=logging.DEBUG)

path = "I:/TOV/PC/map/SHAT14.DAT"
extract_textures_from_package(path)
