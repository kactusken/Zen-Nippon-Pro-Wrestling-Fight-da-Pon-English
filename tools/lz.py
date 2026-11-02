#!/usr/bin/env python3
"""The game's LZ compression (decompressor at $C0:B2B9): reader and writer.

  lz.py info ROM OFFSET            size and packed length of the block at a file offset
  lz.py test ROM OFFSET            decode, re-encode with pack(), decode again and compare

Block: type byte (0 raw, otherwise LZ), u16 unpacked size. Raw: the bytes follow. LZ: repeating
groups of a u16 flag word, read from bit 0; flag 0 = one literal byte, flag 1 = a u16 match:
bits 0-10 distance - 1, bits 11-15 length - 3. A flag word of 0 stands for 16 literals, or for fewer
if the block ends first. The game restores the byte just past the output when done.
"""
import struct
import sys


def unpack(rom, off):
    """Return (data, packed length) of the block at file offset off."""
    kind = rom[off]
    size = struct.unpack_from('<H', rom, off + 1)[0] or 0x10000
    p = off + 3
    if kind == 0:
        return bytes(rom[p:p + size]), 3 + size
    out = bytearray()
    while len(out) < size:
        flags = struct.unpack_from('<H', rom, p)[0]
        p += 2
        for bit in range(16):
            if len(out) >= size:
                break
            if flags >> bit & 1:
                w = struct.unpack_from('<H', rom, p)[0]
                p += 2
                dist, n = (w & 0x7ff) + 1, (w >> 11) + 3
                for _ in range(n):
                    if len(out) >= size:
                        break
                    out.append(out[-dist] if dist <= len(out) else 0)
            else:
                out.append(rom[p])
                p += 1
    return bytes(out), p - off


def pack(data):
    """Compress with a greedy longest match (deterministic; nearest distance wins ties)."""
    size = len(data)
    out = bytearray([1]) + struct.pack('<H', size & 0xffff)
    heads = {}
    pos = 0

    def add(i):
        if i + 3 <= size:
            heads.setdefault(data[i:i + 3], []).append(i)

    while pos < size:
        flags = 0
        group = bytearray()
        for bit in range(16):
            if pos >= size:
                break
            best, bdist = 0, 0
            for j in reversed(heads.get(data[pos:pos + 3], [])):
                if pos - j > 0x800:
                    break
                n = 3
                while n < 34 and pos + n < size and data[j + n] == data[pos + n]:
                    n += 1
                if n > best:
                    best, bdist = n, pos - j
                    if n == 34:
                        break
            if best >= 3:
                flags |= 1 << bit
                group += struct.pack('<H', (bdist - 1) | (best - 3) << 11)
                for i in range(pos, pos + best):
                    add(i)
                pos += best
            else:
                group.append(data[pos])
                add(pos)
                pos += 1
        out += struct.pack('<H', flags) + group
    return bytes(out)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 3 or argv[0] not in ('info', 'test'):
        print(__doc__)
        return 2
    rom = open(argv[1], 'rb').read()
    off = int(argv[2], 0)
    data, n = unpack(rom, off)
    print(f'unpacked {len(data):#x}, packed {n:#x}')
    if argv[0] == 'test':
        again = pack(data)
        same = unpack(again, 0)[0] == data
        print(f'repacked {len(again):#x}, round trip {"ok" if same else "FAILED"}')
        return 0 if same else 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
