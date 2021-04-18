"""Tales of Vesperia Constants.

Various known value identifier for Vesperia files. Credit: delguoqing

"""


def bit(x):
    return 1 << x


UNPACKED_LEFTOVER_FILES = (
    'EMPTY0',
    'NONAME0.FPS4',
    'NONAME1.FPS4',
    'NONAME2.FPS4',
    'NONAME3.FPS4',
)

# Note 1: PC identifier differs with 360 version.
# Note 2: The PS4/XBO Definitive Edition should share the same identifier?
# Note 3: Haven't check for PS3 and Switch DE.
# TODO: Find a better way to identify TXV files
TYPE_2_EXT_PC = {
    "00040000": ".ANM",
    "00000500": ".BLD",
    "00000600": ".CLS",
    "46505334": ".FPS4",
    "00010000": ".HRC",
    "00000300": ".MTR",
    "00000400": ".SHD",
    "00000100": ".SPM",
    "FFFFFFFF": ".SPV",
    "54525348": ".TER",
    "00020000": ".TXM",
    "00155094": ".TXV",
    "00014094": ".TXV",
    "00055094": ".TXV",
}


TYPE_2_EXT_360 = {
    "00000400": ".ANM",
    "00050000": ".BLD",
    "00060000": ".CLS",
    "46505334": ".FPS4",
    "00000100": ".HRC",
    "00030000": ".MTR",
    "00040000": ".SHD",
    "00010000": ".SPM",
    "54525348": ".TER",
    "00020000": ".TXM",
}


KNOWN_EXT = (
    ".ANM",
    ".BLD",
    ".CLS",
    ".HRC",
    ".MTR",
    ".SHD",
    ".SPM",
    ".SPV",
    ".TXM",
    ".TXV",
)


LONG_TYPES = (
    "SCFOMBIN",
    "T8BTMO",
    "T8BTAT",
    "T8BTSL",
    "TSS",
    "T8BTMA",
    "T8BTEMST",
    "T8BTEMGP",
    "T8BTEMEG",
    "T8BTAS",
    "T8BTSK",
    "T8BTTA",
    "T8BTBS",
    "T8BTVA",
    "T8BTEFF",
    "T8BTBG",
    "T8BTLV",
    "T8BTBTGR",
    "T8BTGR",
    "T8BTEV",
    "TO8FOGD",  # tales of 8, fog data
    "TO8LITD",  # tales of 8, light data
    "TO8PSTD",  # tales of 8, posteffect data
    "TO8SKYD",  # tales of 8, sky data
    "TO8WTRD",  # tales of 8, water data
    "TO8SK2D",  # tales of 8, sky2 data
)

# File descriptor flags
FILE_DESCRIPTOR_FILE_OFFSET = bit(0)
FILE_DESCRIPTOR_FILE_SIZE = bit(1)
FILE_DESCRIPTOR_FILE_REAL_SIZE = bit(2)
FILE_DESCRIPTOR_FILE_NAME = bit(3)
FILE_DESCRIPTOR_BIT4 = bit(4)
FILE_DESCRIPTOR_DATA_TYPE = bit(5)
FILE_DESCRIPTOR_ARG = bit(6)
FILE_DESCRIPTOR_BIT7 = bit(7)  # always 0 a.t.m
FILE_DESCRIPTOR_MINIMUM = sum(map(bit, range(3)))  # should at least have (offset, size, real_size)
FILE_DESCRIPTOR_MASK = sum(map(bit, range(8)))  # used to detect unknown bitflag
VERTEX_FORMAT_UV_CHANNEL_COUNT_MASK = bit(0) + bit(1)  # Vertex Stream format flag

# Platform
PLATFORM_X360 = 0x4
PLATFORM_PC = 0x10
TYPE_CODE = 0x00010000

# Textures
DDS_HEADER = b'\x44\x44\x53\x20\x7C'
