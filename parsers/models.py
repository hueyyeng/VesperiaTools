"""Object models for data extraction."""
from dataclasses import dataclass
from typing import TypedDict, List, Dict


@dataclass
class Package:
    name: str = 'NONAME'
    offset: int = 0


class Mesh:
    """Mesh model."""
    # TODO: Cleanup Blender specific attributes
    def __init__(self):
        self.vertPosList = []
        self.vertNormList = []

        self.indiceList = []
        self.faceList = []
        self.triangleList = []

        self.matList = []
        self.matIDList = []
        self.vertUVList = []
        self.faceUVList = []
        self.faceColList = []
        self.vertColList = []

        self.skinList = []
        self.skinWeightList = []
        self.skinIndiceList = []
        self.skinGroupList = []
        self.skinIDList = []
        self.bindPoseMatrixList = []
        self.boneNameList = []
        self.BINDBONE = None

        self.name = None
        self.mesh = None
        self.object = None
        self.TRIANGLE = False
        self.QUAD = False
        self.TRISTRIP = False
        self.BINDSKELETON = None
        self.BINDPOSESKELETON = None
        self.matrix = None
        self.SPLIT = False
        self.WARNING = False
        self.DRAW = False
        self.BINDPOSE = False
        self.UVFLIP = False
        self.vertUVCount = 0
        self.sceneIDList = None

        self.vertModList = []
        self.mod = False
        self.filename = None
        self.BUFFER = 0

        self.RAW = 0

    def create_face(self, matID=0):
        """Create Face

        Parameters
        ----------
        matID : int

        Notes
        -----
        - Based on delguoqing's Python 2 script for Vesperia 360.

        """
        group_idx = 1
        clockwise = False
        indices = len(self.indiceList) - 2
        for i in range(indices):
            # 0xFFFF == 65535
            a, b, c = self.indiceList[i: i + 3]
            is_new_group = (i == 0 or a == 0xFFFF)
            write_face = 0xFFFF not in (a, b, c)

            if is_new_group:
                group_idx += 1
                clockwise = True

            if write_face:
                if clockwise:
                    self.triangleList.append({
                        "group": group_idx,
                        "triangle": [a, b, c],
                    })
                    self.matIDList.append(matID)
                else:
                    triangle = [c, b, a]  # delguoqing
                    self.triangleList.append({
                        "group": group_idx,
                        "triangle": triangle,
                    })
                    self.matIDList.append(matID)
                clockwise = not clockwise


class TMaterial(TypedDict):
    mtl: str
    tex: List[str]


class TImage(TypedDict):
    texture_name: str
    dds_content: bytes


class TNodeData(TypedDict):
    name: str
    offset_start: int
    offset_end: int
    hash_list: List[int]
    mesh_list: List[Mesh]
    material_list: List[List[TMaterial]]
    image_list: List[TImage]


class Node:
    """Node for object parsing and general data structures.

    Contains attributes needed for exporting to external format (e.g. Wavefront OBJ)

    This also hold pointers of the data element that we want to store when
    parsing an object such as found meshes and materials.

    Notes
    -----
    - Based on Szkaradek123's Python 2 script for Blender 2.49.

    """
    def __init__(self):
        self.name = "NONAME"
        self.children = []
        data: TNodeData = {
            "name": "",
            "offset_start": 0,
            "offset_end": 0,
            "hash_list": [],
            "mesh_list": [],
            "material_list": [],
            "image_list": [],
        }
        self.data: Dict[str, TNodeData] = {
            "_": data,
        }
        self.offset = None
