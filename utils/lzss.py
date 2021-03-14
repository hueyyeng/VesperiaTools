import collections
import argparse


def init_text_buf(text_buf):
    for i in range(0x100):
        text_buf[i * 0x8 + 0x6] = i
    for i in range(4):
        text_buf[0xEFF - i] = 0xFF


def decompress_lz01(data, init_text_buf=None, debug=False):
    N = 4096
    F = 17
    THRESHOLD = 2

    text_buf = [0] * N

    if init_text_buf:
        init_text_buf(text_buf)

    dst_buf = []
    src_buf = collections.deque(map(ord, data))
    src_len = len(src_buf)
    group_idx = 0

    r = N - F - 1  # why?
    flags = 0

    while True:
        try:
            if (flags & 0x100) == 0:
                flags = src_buf.popleft() | 0xFF00

                if debug:
                    src_offset = src_len - len(src_buf) - 1
                    dst_offset = len(dst_buf)
                    size = 0
                    for i in range(8):
                        if flags & (1 << i):
                            size += 1
                        else:
                            size += 2

            if flags & 1:
                c = src_buf.popleft()
                dst_buf.append(c)
                text_buf[r] = c
                r = (r + 1) % N
            else:
                i = src_buf.popleft()
                j = src_buf.popleft()
                offset = i | ((j & 0xF0) << 4)
                length = (j & 0xF) + THRESHOLD + 1
                copy_init = False
                if debug:
                    dst_offset = len(dst_buf)
                    src_offset = src_len - len(src_buf) - 2
                    if dst_offset <= N:
                        if (dst_offset < F and (offset >= N - F + dst_offset or offset < N - F)) or \
                                (dst_offset >= F and dst_offset <= offset + F < N - F):
                            print(
                                "refing init window src@offset=%s, dst@offset=%s, window@%s, size=%s" % (
                                    hex(src_offset),
                                    hex(dst_offset),
                                    hex(offset),
                                    hex(length),
                                )
                            )
                            print(
                                hex(i),
                                hex(j),
                                hex(offset),
                                hex(length),
                            )
                            copy_init = True

                copied = ""
                for k in range(length):
                    c = text_buf[(offset + k) % N]
                    dst_buf.append(c)
                    text_buf[r] = c
                    r = (r + 1) % N
                    if debug:
                        copied += chr(c)
                if debug and copy_init:
                    print("copied: %s" % repr(copied))

            flags >>= 1
        except IndexError:
            break

    return "".join(map(chr, dst_buf))


def decompress_lz03(data, init_text_buf=None, debug=False):
    N = 4096
    F = 17
    THRESHOLD = 2

    text_buf = [0] * N

    if init_text_buf:
        init_text_buf(text_buf)

    dst_buf = []
    src_buf = collections.deque(map(ord, data))
    src_len = len(src_buf)
    group_idx = 0

    r = N - F
    flags = 0

    while True:
        try:
            if (flags & 0x100) == 0:
                flags = src_buf.popleft() | 0xFF00

                if debug:
                    src_offset = src_len - len(src_buf) - 1
                    dst_offset = len(dst_buf)
                    size = 0
                    for i in range(8):
                        if flags & (1 << i):
                            size += 1
                        else:
                            size += 2

            if flags & 1:
                c = src_buf.popleft()
                dst_buf.append(c)
                text_buf[r] = c
                r = (r + 1) % N
            else:
                i = src_buf.popleft()
                j = src_buf.popleft()

                if j & 0xF == 0xF:  # RLE
                    if j == 0x0F:
                        c = src_buf.popleft()
                        length = i + 3 + 0x10
                    else:
                        c = i
                        length = (j >> 4) + 3

                    for k in range(length):
                        dst_buf.append(c)
                        text_buf[r] = c
                        r = (r + 1) % N
                else:
                    offset = i | ((j & 0xF0) << 4)
                    length = (j & 0xF) + THRESHOLD + 1
                    copy_init = False
                    if debug:
                        dst_offset = len(dst_buf)
                        src_offset = src_len - len(src_buf) - 2
                        if dst_offset <= N:
                            if (dst_offset < F and (offset >= N - F + dst_offset or offset < N - F)) or \
                                    (dst_offset >= F and dst_offset <= offset + F < N - F):
                                print("refing init window src@offset=%s, dst@offset=%s, window@%s, size=%s" % (
                                    hex(src_offset), hex(dst_offset), hex(offset), hex(length)))
                                print(hex(i), hex(j), hex(offset), hex(length))
                                copy_init = True

                    copied = ""
                    for k in range(length):
                        c = text_buf[(offset + k) % N]
                        dst_buf.append(c)
                        text_buf[r] = c
                        r = (r + 1) % N
                        if debug:
                            copied += chr(c)
                    if debug and copy_init:
                        print("copied: %s" % repr(copied))
            flags >>= 1
        except IndexError:
            break

    return "".join(map(chr, dst_buf))


if __name__ == '__main__':
    description = "Decompress a LZSS compressed file of Tales of Vesperia."

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-D", action="store_true", default=False, dest="debug", help="debug only.")
    parser.add_argument("-f", action="store", dest="lzss_file", type=argparse.FileType("rb"),
                        help="Input file, the lzss compressed file.")
    parser.add_argument("-o", action="store", dest="out_file", type=argparse.FileType("wb"),
                        help="Output file, the unpacked file.")
    parser.add_argument("-s", action="store", dest="size", type=int, default=0,
                        help="bytes of data you want to decompress, a debug feature, default: the whole file!")

    args = parser.parse_args()

    f = args.lzss_file
    data = f.read()
    f.close()

    _type = ord(data[0])
    if _type == 0x1:
        decompress = decompress_lz01
    elif _type == 0x3:
        decompress = decompress_lz03
    else:
        assert False, "unsupported compress type! %s" % hex(_type)

    if args.size <= 0:
        data = data[9:]
    else:
        data = data[9: 9 + args.size]

    f = args.out_file
    data = decompress(data, init_text_buf=init_text_buf, debug=args.debug)
    f.write(data)
    f.close()
