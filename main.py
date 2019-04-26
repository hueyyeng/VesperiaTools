import os
import glob
import logging
from utils.exporter import export_wavefront_obj
from utils.files import unpack_dat

logging.basicConfig(level=logging.DEBUG)


BG_SINGLE_MESH_SPM = "I:\TOV\PC\map\CAOT00.DAT.dec.ext\MDL_CAO_T00_T03HOUSE.SPM"
# DAT_FILE =
tmp_path = "I:/TOV/_tmp"


export_wavefront_obj(BG_SINGLE_MESH_SPM, tmp_path)

# packages = glob.glob("I:/TOV/PC/map/C*.DAT")
# for package in packages:
#     unpack_dat(package, deep_extract=True)
