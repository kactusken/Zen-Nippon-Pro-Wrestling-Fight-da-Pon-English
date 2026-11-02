#!/usr/bin/env python3
"""Card labels: translation/text/cards.csv into the card art (LZ block at $C7:0000, 42 cards of
4x5 tiles, label in x 1-29, y 1-6, colour 15 paper, colour 1 ink).

Build step: unpack, clean the frame edges, redraw the labels, pack into bank $D2, point the table entry at $C0:E700 there.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lz  # noqa: E402

BLOCK = 0x70000
TABLE_ENTRY = 0xE700
NEW = 0x120000
FONT = Path(__file__).resolve().parent / 'fonts' / 'label.txt'


def font():
    out = {}
    for line in FONT.read_text(encoding='utf-8').splitlines():
        if line.startswith('#') or len(line) < 3:
            continue
        out[line[0]] = line[2:].split('/')
    return out


def width(s, f):
    return sum(len(f[c][0]) + 1 for c in s) - 1 if s else 0


def setpx(d, card, x, y, v):
    t = (y // 8) * 4 + x // 8
    o = card * 0x280 + t * 32
    yy, m = y % 8, 0x80 >> (x % 8)
    for i, a in enumerate((o + yy * 2, o + yy * 2 + 1, o + 16 + yy * 2, o + 17 + yy * 2)):
        d[a] = d[a] | m if v >> i & 1 else d[a] & ~m & 255


def mend_frame(d, card):
    """The art leaks stray pixels into the white frame (top row x 1-29, left column y 1-38):
    Coconut, Kawazu, Stretch Plum, Spin Kick, Lariat. Repaint both as paper (15), and row 7."""
    for x in range(1, 30):
        setpx(d, card, x, 0, 15)
    for y in range(1, 39):
        setpx(d, card, 0, y, 15)
    for x in range(1, 30):             # the gap under the label: Kawazu had leftover dither
        setpx(d, card, x, 7, 15)


def draw(d, card, s, f):
    for y in range(1, 7):
        for x in range(1, 30):
            setpx(d, card, x, y, 15)
    w = width(s, f)
    if w > 29:
        raise SystemExit(f'card {card}: "{s}" is {w} px, the label holds 29')
    x = 1 + (29 - w) // 2
    for c in s:
        rows = f[c]
        for yy, row in enumerate(rows):
            for xx, p in enumerate(row):
                if p == '#':
                    setpx(d, card, x + xx, 2 + yy, 1)
        x += len(rows[0]) + 1


def build_step(path, files):
    rom = bytearray(files.get('/rom.sfc'))
    d = bytearray(lz.unpack(rom, BLOCK)[0])
    f = font()
    with open(path, encoding='utf-8', newline='') as fh:
        rows = [r for r in csv.DictReader(c for c in fh if not c.startswith('#'))]
    n = 0
    for card in range(42):
        mend_frame(d, card)
    for r in rows:
        if r['en']:
            draw(d, int(r['card']), r['en'], f)
            n += 1
    packed = lz.pack(bytes(d))
    if len(packed) > 0x10000:
        raise SystemExit('card block over a bank')
    rom[NEW:NEW + len(packed)] = packed
    rom[TABLE_ENTRY:TABLE_ENTRY + 3] = bytes([NEW & 255, NEW >> 8 & 255, 0xD2])
    for at in (0xD4F3,):               # LDA #$00C7 for the block at C7:0000. NOT $D735: that loads the
        if rom[at] != 0xC7:            # YOU LOSE picture from C7:C9AE (patching it garbled the screen)
            raise SystemExit(f'unexpected byte at {at:#x}')
        rom[at] = 0xD2
    print(f'cards: {n} labels, block {len(packed):#x} bytes')
    files.put('/rom.sfc', bytes(rom))
