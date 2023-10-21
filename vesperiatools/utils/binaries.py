import array
import logging
import struct

logger = logging.getLogger(__name__)


def half_to_float(h):
    s = int((h >> 15) & 0x00000001)  # sign
    e = int((h >> 10) & 0x0000001f)  # exponent
    f = int(h & 0x000003ff)  # fraction

    if e == 0:
        if f == 0:
            return int(s << 31)
        else:
            while not (f & 0x00000400):
                f <<= 1
                e -= 1
            e += 1
            f &= ~0x00000400
    elif e == 31:
        if f == 0:
            return int((s << 31) | 0x7f800000)
        else:
            return int((s << 31) | 0x7f800000 | (f << 13))

    e = e + (127 - 15)
    f = f << 13
    return int((s << 31) | (e << 23) | f)


def convert_half_to_float(h):
    id = half_to_float(h)
    structure = struct.pack('I', id)
    return struct.unpack('f', structure)[0]


class BinaryUnpacker():
    def __init__(self, data, log=None):
        self.endian = '<'
        self.offset = 0
        self.data = data
        self.len = len(data) - self.offset
        self.log = True
        self.logData = ""

    def q(self, n):
        data = struct.unpack(self.endian + n * 'q', self.data[self.offset:self.offset + (n * 8)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 8
        return data

    def i(self, n):
        data = struct.unpack(self.endian + n * 'i', self.data[self.offset:self.offset + (n * 4)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 4
        return data

    def I(self, n):
        data = struct.unpack(self.endian + n * 'I', self.data[self.offset:self.offset + (n * 4)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 4
        return data

    def B(self, n):
        data = struct.unpack(self.endian + n * 'B', self.data[self.offset:self.offset + (n * 1)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 1
        return data

    def b(self, n):
        data = struct.unpack(self.endian + n * 'b', self.data[self.offset:self.offset + (n * 1)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 1
        return data

    def h(self, n):
        data = struct.unpack(self.endian + n * 'h', self.data[self.offset:self.offset + (n * 2)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 2
        return data

    def H(self, n):
        data = struct.unpack(self.endian + n * 'H', self.data[self.offset:self.offset + (n * 2)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 2
        return data

    def f(self, n):
        data = struct.unpack(self.endian + n * 'f', self.data[self.offset:self.offset + (n * 4)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 4
        return data

    def d(self, n):
        data = struct.unpack(self.endian + n * 'd', self.data[self.offset:self.offset + (n * 8)])
        if self.log:
            self.logData += str(self.offset) + ' ' + str(data) + '\n'
        self.offset += n * 8
        return data

    def half(self, n, h='h'):
        data = []
        for id in range(n):
            data.append(convert_half_to_float(struct.unpack(self.endian + h, self.data[self.offset:self.offset + 2])[0]))
            self.offset += 2
        if self.log:
            self.logData += str(self.offset - n * 2) + ' ' + str(data) + '\n'
        return data

    def short(self, n, h='h', exp=12):
        data = []
        for id in range(n):
            data.append(struct.unpack(self.endian + h, self.data[self.offset:self.offset + 2]) * 2 ** -exp)
        if self.log:
            self.logData += str(self.offset - n * 2) + ' ' + str(data) + '\n'
        return data

    def seek(self, off, a=0):
        if a == 0:
            self.offset = off
        if a == 1:
            self.offset += off

    def dataSize(self):
        return len(self.data)

    def tell(self):
        return self.offset


class BinaryReader():
    """general BinaryReader"""

    def __init__(self, input_file):
        self.input_file = input_file
        self.endian = '<'
        self.debug = False
        self.stream = {}
        self.logfile = None
        self.log = False
        self.xorKey = None
        self.xorOffset = 0
        self.xorData = ''
        self.logskip = False
        self.ARRAY = False

    def close(self):
        self.input_file.close()

    def XOR(self, data):
        self.xorData = ''
        for m in range(len(data)):
            ch = ord(chr(data[m] ^ self.xorKey[self.xorOffset]))
            self.xorData += struct.pack('B', ch)
            if self.xorOffset == len(self.xorKey) - 1:
                self.xorOffset = 0
            else:
                self.xorOffset += 1

    def q(self, n):
        offset = self.input_file.tell()
        data = struct.unpack(self.endian + n * 'q', self.input_file.read(n * 8))
        if self.debug:
            logger.debug({
                "data": data,
            })
        if self.log:
            if self.logfile is not None and self.logskip is not True:
                self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
        return data

    def i(self, n):
        if self.input_file.mode == 'rb':
            offset = self.input_file.tell()
            if self.xorKey is None:
                if self.ARRAY is False:
                    data = struct.unpack(self.endian + n * 'i', self.input_file.read(n * 4))
                else:
                    data = array.array('i')
                    data.fromfile(self.input_file, n)
                    if self.endian == ">":
                        data.byteswap()
            else:
                data = struct.unpack(self.endian + n * 4 * 'B', self.input_file.read(n * 4))
                self.XOR(data)
                data = struct.unpack(self.endian + n * 'i', self.xorData)

            if self.debug:
                logger.debug({
                    "data": data,
                })
            if self.log:
                if self.logfile is not None and self.logskip is not True:
                    self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
            return data

        if self.input_file.mode == 'wb':
            for m in range(len(n)):
                data = struct.pack(self.endian + 'i', n[m])
                self.input_file.write(data)

    def I(self, n):
        offset = self.input_file.tell()
        if self.xorKey is None:
            data = struct.unpack(self.endian + n * 'I', self.input_file.read(n * 4))
        else:
            data = struct.unpack(self.endian + n * 4 * 'B', self.input_file.read(n * 4))
            self.XOR(data)
            data = struct.unpack(self.endian + n * 'I', self.xorData)
        if self.debug:
            logger.debug({
                "data": data,
            })
        if self.log:
            if self.logfile is not None and self.logskip is not True:
                self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
        return data

    def B(self, n):
        if self.input_file.mode == 'rb':
            offset = self.input_file.tell()
            if self.xorKey is None:
                if self.ARRAY == False:
                    data = struct.unpack(self.endian + n * 'B', self.input_file.read(n))
                else:
                    data = array.array('B')
                    data.fromfile(self.input_file, n)
                    if self.endian == ">": data.byteswap()


            else:
                data = struct.unpack(self.endian + n * 'B', self.input_file.read(n))
                self.XOR(data)
                data = struct.unpack(self.endian + n * 'B', self.xorData)
            if self.debug:
                logger.debug({
                    "data": data,
                })
            if self.log:
                if self.logfile is not None and self.logskip is not True:
                    self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
            return data
        if self.input_file.mode == 'wb':
            for m in range(len(n)):
                data = struct.pack(self.endian + 'B', n[m])
                self.input_file.write(data)

    def b(self, n):
        if self.input_file.mode == 'rb':
            offset = self.input_file.tell()
            if self.xorKey is None:
                if not self.ARRAY:
                    data = struct.unpack(self.endian + n * 'b', self.input_file.read(n))
                else:
                    data = array.array('b')
                    data.fromfile(self.input_file, n)
                    if self.endian == ">": data.byteswap()
            else:
                data = struct.unpack(self.endian + n * 'b', self.input_file.read(n))
                self.XOR(data)
                data = struct.unpack(self.endian + n * 'b', self.xorData)
            if self.debug:
                logger.debug({
                    "data": data,
                })
            if self.log:
                if self.logfile is not None and self.logskip is not True:
                    self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
            return data
        if self.input_file.mode == 'wb':
            for m in range(len(n)):
                data = struct.pack(self.endian + 'b', n[m])
                self.input_file.write(data)

    def h(self, n):
        if self.input_file.mode == 'rb':
            offset = self.input_file.tell()
            if self.xorKey is None:
                if not self.ARRAY:
                    data = struct.unpack(self.endian + n * 'h', self.input_file.read(n * 2))
                else:
                    data = array.array('h')
                    data.fromfile(self.input_file, n)
                    if self.endian == ">": data.byteswap()


            else:
                data = struct.unpack(self.endian + n * 2 * 'B', self.input_file.read(n * 2))
                self.XOR(data)
                data = struct.unpack(self.endian + n * 'h', self.xorData)
            if self.debug:
                logger.debug({
                    "data": data,
                })
            if self.log:
                if self.logfile is not None and self.logskip is not True:
                    self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
            return data
        if self.input_file.mode == 'wb':
            for m in range(len(n)):
                data = struct.pack(self.endian + 'h', n[m])
                self.input_file.write(data)

    def H(self, n):
        if self.input_file.mode == 'rb':
            offset = self.input_file.tell()
            if self.xorKey is None:
                if self.ARRAY == False:
                    data = struct.unpack(self.endian + n * 'H', self.input_file.read(n * 2))
                else:
                    data = array.array('H')
                    data.fromfile(self.input_file, n)
                    if self.endian == ">":
                        data.byteswap()
            else:
                data = struct.unpack(self.endian + n * 2 * 'B', self.input_file.read(n * 2))
                self.XOR(data)
                data = struct.unpack(self.endian + n * 'H', self.xorData)
            if self.debug:
                logger.debug({
                    "data": data,
                })
            if self.log:
                if self.logfile is not None and self.logskip is not True:
                    self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
            return data
        if self.input_file.mode == 'wb':
            for m in range(len(n)):
                data = struct.pack(self.endian + 'H', n[m])
                self.input_file.write(data)

    def f(self, n):
        if self.input_file.mode == 'rb':
            offset = self.input_file.tell()
            if self.xorKey is None:
                if not self.ARRAY:
                    data = struct.unpack(self.endian + n * 'f', self.input_file.read(n * 4))
                else:
                    data = array.array('f')
                    data.fromfile(self.input_file, n)
                    if self.endian == ">": data.byteswap()

            else:
                data = struct.unpack(self.endian + n * 4 * 'B', self.input_file.read(n * 4))
                self.XOR(data)
                data = struct.unpack(self.endian + n * 'f', self.xorData)
            if self.debug:
                logger.debug({
                    "data": data,
                })
            if self.log:
                if self.logfile is not None and self.logskip is not True:
                    self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
            return data

        if self.input_file.mode == 'wb':
            for m in range(len(n)):
                data = struct.pack(self.endian + 'f', n[m])
                self.input_file.write(data)

    def d(self, n):
        if self.input_file.mode == 'rb':
            offset = self.input_file.tell()
            if self.xorKey is None:
                data = struct.unpack(self.endian + n * 'd', self.input_file.read(n * 8))
            else:
                data = struct.unpack(self.endian + n * 4 * 'B', self.input_file.read(n * 8))
                self.XOR(data)
                data = struct.unpack(self.endian + n * 'd', self.xorData)
            if self.debug:
                logger.debug({
                    "data": data,
                })
            if self.log:
                if self.logfile is not None and self.logskip is not True:
                    self.logfile.write('offset ' + str(offset) + '	' + str(data) + '\n')
            return data
        if self.input_file.mode == 'wb':
            for m in range(len(n)):
                data = struct.pack(self.endian + 'd', n[m])
                self.input_file.write(data)

    def half(self, n, h='h'):
        array = []
        offset = self.input_file.tell()
        for id in range(n):
            array.append(convert_half_to_float(struct.unpack(self.endian + h, self.input_file.read(2))[0]))
        if self.debug:
            logger.debug({
                "array": array,
            })
        if self.log:
            if self.logfile is not None and self.logskip is not True:
                self.logfile.write('offset ' + str(offset) + '	' + str(array) + '\n')
        return array

    def short(self, n, h='h', exp=12):
        array = []
        offset = self.input_file.tell()
        for id in range(n):
            array.append(struct.unpack(self.endian + h, self.input_file.read(2))[0] * 2 ** -exp)
        if self.debug:
            logger.debug({
                "array": array,
            })
        if self.log:
            if self.logfile is not None and self.logskip is not True:
                self.logfile.write('offset ' + str(offset) + '	' + str(array) + '\n')
        return array

    def i12(self, n):
        array = []
        offset = self.input_file.tell()
        for id in range(n):
            if self.endian == '>':
                var = '\x00' + self.input_file.read(3)
            if self.endian == '<':
                var = self.input_file.read(3) + '\x00'
            array.append(struct.unpack(self.endian + 'i', var)[0])
        if self.debug:
            logger.debug({
                "array": array,
            })
        if self.log:
            if self.logfile is not None and self.logskip is not True:
                self.logfile.write('offset ' + str(offset) + '	' + str(array) + '\n')
        return array

    def find(self, values=b"\x00", size=100, all=None):
        start = self.input_file.tell()
        s = ""
        while True:
            data = self.input_file.read(size + len(values))
            off = data.find(values)

            if start >= self.fileSize():
                logger.debug({
                    "msg": "start >= fileSize",
                    "start": start,
                    "fileSize": self.fileSize(),
                })
                break
            if off >= 0:
                decoded_name = data[:off].decode()
                s += decoded_name
                self.input_file.seek(start + off + len(values))
                logger.debug({
                    "msg": "off >= 0",
                    "off": off,
                })
                break
            else:
                self.input_file.seek(-len(values), 1)
                s += data
                start += size
                logger.debug({
                    "s": s,
                    "start": start,
                })

        if self.debug:
            logger.debug({
                "s": s,
            })
        if self.log:
            if self.logfile is not None and self.logskip is not True:
                self.logfile.write('offset ' + str(start) + '	' + s + '\n')
        return s

    def string(self, values="\x00", size=100):
        start = self.input_file.tell()
        s = ""
        while (True):
            data = self.input_file.read(size + len(values))
            off = data.find(values)
            if off >= 0:
                s += data[:off]
                self.input_file.seek(start + off + len(values))
                break
            else:
                self.input_file.seek(-len(values), 1)
                s += data
                start += size
            if self.input_file.tell() >= self.fileSize():
                break

        if self.debug:
            logger.debug({
                "s": s,
            })
        if self.log:
            if self.logfile is not None and self.logskip is not True:
                self.logfile.write('offset ' + str(start) + '	' + s + '\n')
        return s

    def findAll(self, var, size=100):
        found_list = []
        while True:
            start = self.input_file.tell()
            data = self.input_file.read(size)
            off = data.find(var)
            if off >= 0:
                found_list.append(start + off)
                self.input_file.seek(start + off + len(var))
            else:
                start += size
                self.input_file.seek(start)
            if self.input_file.tell() > self.fileSize():
                break
        return found_list

    def fileSize(self):
        back = self.input_file.tell()
        self.input_file.seek(0, 2)
        tell = self.input_file.tell()
        # self.inputFile.seek(0)
        self.input_file.seek(back)
        return tell

    def seek(self, off, a=0):
        self.input_file.seek(off, a)

    def seekpad(self, pad, type=0):
        """ 16-byte chunk alignment"""
        size = self.input_file.tell()
        seek = (pad - (size % pad)) % pad
        if type == 1:
            if seek == 0:
                seek += pad
        self.input_file.seek(seek, 1)

    def read(self, count):
        back = self.input_file.tell()
        if self.xorKey is None:
            return self.input_file.read(count)
        else:
            data = struct.unpack(self.endian + count * 'B', self.input_file.read(count))
            self.XOR(data)
            return self.xorData

    def bytes(self, count):
        back = self.input_file.tell()
        if self.xorKey is None:
            return self.input_file.read(count)
        else:
            data = struct.unpack(self.endian + count * 'B', self.input_file.read(count))
            self.XOR(data)
            return self.xorData

    def unpack(self, values):
        # "5i6hi"
        count = ""
        type = None
        out = []
        for value in values:
            if value.isdigit():
                count += value
            else:
                type = value
            if type:
                if len(count) == 0:
                    count = 1
                else:
                    count = int(count)
                if type == 'i':
                    out.extend(self.i(count))
                elif type == 'I':
                    out.extend(self.I(count))
                elif type == 'h':
                    out.extend(self.h(count))
                elif type == 'H':
                    out.extend(self.H(count))
                elif type == 'f':
                    out.extend(self.f(count))
                elif type == 'b':
                    out.extend(self.b(count))
                elif type == 'B':
                    out.extend(self.B(count))
                elif type == 'd':
                    out.extend(self.d(count))
                elif type == 'q':
                    out.extend(self.q(count))
                elif type == 'half':
                    out.extend(self.half(count))
                elif type == 'short':
                    out.extend(self.short(count))
                elif type == '_':
                    self.seek(count, 1)
                else:
                    print('are you sure ?:', type)
                type = None
                count = ""
        return out

    def write(self, string):
        self.input_file.write(string)

    def tell(self):
        val = self.input_file.tell()
        if self.debug:
            print('Current offset is:', val)
        return val

    def word(self, long):
        if long < 10000:
            if self.input_file.mode == 'rb':
                offset = self.input_file.tell()
                s = ''
                for j in range(0, long):
                    if self.xorKey is None:
                        lit = struct.unpack('c', self.input_file.read(1))[0]
                    else:
                        data = struct.unpack(self.endian + 'B', self.input_file.read(1))
                        self.XOR(data)
                        lit = struct.unpack(self.endian + 'c', self.xorData)[0]
                    lit = lit.decode()
                    if ord(lit) != 0:
                        s += lit
                if self.debug:
                    logger.debug({
                        "s": s,
                    })
                if self.log:
                    if self.logfile is not None and self.logskip is not True:
                        self.logfile.write('offset ' + str(offset) + '	' + s + '\n')
                return s
            if self.input_file.mode == 'wb':
                self.input_file.write(long)
        else:
            logger.debug({
                "msg": "WARNING! Too long!",
            })

    def decode(self, list):
        litery = 'qwertyuiopasdfghjklzxcvbnm'
        new = []
        for item in list:
            if chr(item).lower() in litery:
                new.append(chr(item))
            else:
                new.append(item)
        return new
