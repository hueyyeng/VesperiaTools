"""Object models for data extraction."""


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
