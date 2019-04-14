def bit(x):
    return 1 << x


TYPE_2_EXT = {
    0x54525348: ".TER",
    0x00000400: ".ANM",
    0x00030000: ".MTR",
    0x00050000: ".BLD",
    0x00060000: ".CLS",
    0x00000100: ".HRC",
    0x00040000: ".SHD",
    0x00010000: ".SPM",
    0x00020000: ".TXM",
    0x46505334: ".FPS4",
}

LONG_TYPES = {
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
}

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
