#!/usr/bin/env python3
"""The "OTASUKE SELECT" title art -> "PARTNER SELECT".

Build step (translation/text/title.txt holds the word, now PARTNER). The title is made of 16x16 gold
letters, 2x2 tiles each, as 2x2 *metatiles* (4 words: TL TR BL BR) in the block at $C1:8DE8 (unpacks to
7E:1800, entries 101-108 are this title; 101 covers tile columns 0-1) whose tiles are in the block at
$C4:B866 (BG1 chr, shared with the CARD BATTLE and WRESTLER SELECT titles).

PARTNER needs P and N, which the font has not got. P = the R's top half (tiles $07 $08) with two new bottom
tiles; N = the H's stems (tiles $69/$6E) with a drawn diagonal, four new tiles. The six tiles $62-$67 (the
old K and U bottoms) are used by no other title, so they take the new art; the other letters reuse tiles.
Both blocks are repacked and written back in place (they must not grow).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz  # noqa: E402

GFX = 0x4B866          # C4:B866
META = 0x18DE8         # C1:8DE8
FIRST = 101            # first title metatile
PAL = 0x0800           # palette 2
HFLIP = 0x4000

# new tiles (ids), see the module docstring
P_BL, P_BR, N_TL, N_TR, N_BL, N_BR = 0x64, 0x65, 0x62, 0x63, 0x66, 0x67


def get_tile(g, t):
    o = t * 32
    px = [[0] * 8 for _ in range(8)]
    for y in range(8):
        b0, b1, b2, b3 = g[o + y * 2], g[o + y * 2 + 1], g[o + 16 + y * 2], g[o + 17 + y * 2]
        for x in range(8):
            s = 7 - x
            px[y][x] = (b0 >> s & 1) | (b1 >> s & 1) << 1 | (b2 >> s & 1) << 2 | (b3 >> s & 1) << 3
    return px


def put_tile(g, t, px):
    o = t * 32
    for y in range(8):
        b = [0, 0, 0, 0]
        for x in range(8):
            for p in range(4):
                if px[y][x] >> p & 1:
                    b[p] |= 0x80 >> x
        g[o + y * 2], g[o + y * 2 + 1], g[o + 16 + y * 2], g[o + 17 + y * 2] = b


def flip_h(px):
    return [r[::-1] for r in px]


def joined(a, b):
    return [a[y] + b[y] for y in range(8)]


def letter(tl, tr, bl, br):
    return joined(tl, tr) + joined(bl, br)


def split(img):
    return ([r[:8] for r in img[:8]], [r[8:] for r in img[:8]],
            [r[:8] for r in img[8:]], [r[8:] for r in img[8:]])


def draw(g):
    """Write the P and N tiles into the graphics block g."""
    t = lambda i: get_tile(g, i)          # noqa: E731
    # P: R's bowl (tiles 07 08 / 15 16); below the bowl only the stem
    r_bl, r_br = t(0x15), t(0x16)
    p_bl = [row[:] for row in r_bl]
    p_br = [row[:] for row in r_br]
    for y in range(3, 8):                 # image rows 11-15: the leg of the R goes, the stem stays
        for x in range(5, 8):
            p_bl[y][x] = 8
        p_br[y] = [8] * 8
    put_tile(g, P_BL, p_bl)
    put_tile(g, P_BR, p_br)
    # N: H's stems (tiles 69 / 6E, the right one mirrored) and a diagonal in the stem's row colours
    h = letter(t(0x69), flip_h(t(0x69)), t(0x6E), flip_h(t(0x6E)))
    img = [row[:] for row in h]
    for y in range(16):
        for x in range(5, 11):            # the H's crossbar goes
            img[y][x] = 8
    for y in range(16):
        colour = h[y][3] if y > 1 else h[2][3]
        left = int(round(2.5 + 7.0 * y / 15))
        for x in range(left, left + 4):
            if 1 <= x <= 14:
                img[y][x] = colour
    tl, tr, bl, br = split(img)
    for tid, px in ((N_TL, tl), (N_TR, tr), (N_BL, bl), (N_BR, br)):
        put_tile(g, tid, px)


def metatiles(word):
    """The 8 title metatiles (TL TR BL BR) spelling word, 7 letters from tile column 1."""
    if word != 'PARTNER':
        raise SystemExit(f'title.py draws only PARTNER (got {word!r}); add letters in draw() and metatiles()')
    # letters as (TL, TR, BL, BR) tile words
    P = (0x07, 0x08, P_BL, P_BR)
    A = (0x06, 0x06 | HFLIP, 0x14, 0x14 | HFLIP)
    R = (0x07, 0x08, 0x15, 0x16)
    T = (0x0E, 0x0F, 0x1B, 0x1C)
    N = (N_TL, N_TR, N_BL, N_BR)
    E = (0x0C, 0x11, 0x19, 0x1F)
    letters = [P, A, R, T, N, E, R]
    top, bot = {0: 0x03}, {0: 0x03}      # tile column 0 is the frame ($03)
    for i, (tl, tr, bl, br) in enumerate(letters):
        top[1 + 2 * i], top[2 + 2 * i] = tl, tr
        bot[1 + 2 * i], bot[2 + 2 * i] = bl, br
    out = []
    for m in range(8):                    # metatile m covers tile columns 2m, 2m+1
        w = []
        for rowd in (top, bot):
            for c in (2 * m, 2 * m + 1):
                v = rowd.get(c, 0x0B)     # $0B is the blank tile
                w.append((v & 0x3FF) | (v & HFLIP) | PAL)
        out.append([w[0], w[1], w[2], w[3]])
    return out


def build_step(path, files):
    word = Path(path).read_text(encoding='utf-8').strip().splitlines()[-1].strip().upper()
    rom = bytearray(files.get('/rom.sfc'))
    g, glen = lz.unpack(rom, GFX)
    g = bytearray(g)
    draw(g)
    pg = lz.pack(bytes(g))
    if len(pg) > glen:
        raise SystemExit(f'title graphics repack {len(pg)} > original {glen} bytes; relocate the block')
    rom[GFX:GFX + len(pg)] = pg
    rom[GFX + len(pg):GFX + glen] = bytes(glen - len(pg))
    m, mlen = lz.unpack(rom, META)
    m = bytearray(m)
    for i, w in enumerate(metatiles(word)):
        for j, v in enumerate(w):
            m[(FIRST + i) * 8 + j * 2:(FIRST + i) * 8 + j * 2 + 2] = v.to_bytes(2, 'little')
    pm = lz.pack(bytes(m))
    if len(pm) > mlen:
        raise SystemExit(f'title metatile repack {len(pm)} > original {mlen} bytes; relocate the block')
    rom[META:META + len(pm)] = pm
    rom[META + len(pm):META + mlen] = bytes(mlen - len(pm))
    print(f'title: {word} (graphics {len(pg)}/{glen}, metatiles {len(pm)}/{mlen} bytes)')
    files.put('/rom.sfc', bytes(rom))


if __name__ == '__main__':
    sys.exit('use build.py (text step)')
