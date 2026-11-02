#!/usr/bin/env python3
"""The event script's messages: bank $C4 offsets $CD20-$FFF3, 862 strings.

  script.py dump        write translation/script/events.txt from the original
  script.py widths      the widest English lines

A message runs to its terminator, $0B or $00. The event scripts point at the first byte, which is
often $05 (clear the box). Nothing is repointed: bank $D0 starts with a copy of the original area,
each message's first three bytes there become $0E lo hi (jump, a code the build adds), and the
English sits at $D0:0000 up. All five text reads are moved from bank $C4 to $D0 (build.py).

Control codes: 00 end; 0B end; 02 new line (scrolls when the box is full); 05 clear; 08 a 16 px
space; 09 reset the name index; 0A the wrestler's name; 01 xx a character from the second page.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import blocks  # noqa: E402
import paths  # noqa: E402

START, END = 0xCD20, 0xFFF4
BANK = 0x40000
TEXT_BANK = 0x100000          # $D0
CODE_BANK = 0x110000          # $D1: renderer, widths, font, names
BOX_WIDTH = 176
MAX_LINES = 2
ELLIPSIS = 0x7F
TBL = Path(__file__).resolve().parent / 'font.tbl'
FONT = Path(__file__).resolve().parent / 'fonts' / 'vwf.txt'


def table():
    out = {}
    for line in TBL.read_text(encoding='utf-8').splitlines():
        k, v = line.split('=', 1)
        out[int(k, 16)] = v
    return out


def messages(rom):
    """[(offset in the bank, length, leading code or None, [codes and text], end code)]"""
    t = table()
    bank = rom[BANK:BANK + 0x10000]
    out, a = [], START
    while a < END:
        i, s = a, ''
        while True:
            c = bank[i]
            i += 1
            if c == 1:
                s += t[0x100 | bank[i]]
                i += 1
            elif c in (0, 0xb):
                break
            elif c == 2:
                s += '\n'
            elif c == 5:
                s += '\f'
            elif c == 8:
                s += '　'
            elif c < 0x10:
                s += f'<{c:x}>'
            else:
                s += t[c]
        out.append((a, i - a, s, c))
        a = i
    return out


def load_font():
    """{code: (advance, 16 row bytes)}"""
    glyphs, lines = {}, FONT.read_text(encoding='utf-8').splitlines()
    i = 0
    while i < len(lines):
        m = re.match(r'char ([0-9a-f]+) width (\d+)', lines[i])
        if not m:
            i += 1
            continue
        code = int(m[1], 16)
        code = ELLIPSIS if code == 0x2026 else code
        rows = [int(r.ljust(8, '.').replace('#', '1').replace('.', '0'), 2) for r in lines[i + 1:i + 17]]
        glyphs[code] = (int(m[2]), bytes(rows))
        i += 17
    return glyphs


def bar_tile(c):
    i = ord(c) - 65
    if c == '-' or c == ' ':
        return 0x30F4 if c == '-' else 0x3000
    if c == 'Y':
        return 0x30F2
    if c == 'Z':
        return 0x30F3
    if not 0 <= i < 24:
        raise SystemExit(f'name bar letter {c!r}: only A-Z and -')
    return 0x3000 | (0xC0 + (i // 8) * 0x10 + i % 8)


def text_width(s, glyphs):
    s = s.replace('<a>', 'WWWWWWWW').replace('<9>', '')
    return sum(glyphs[ELLIPSIS if ch == '…' else ord(ch)][0] for ch in s)


def wrap(text, glyphs, width=BOX_WIDTH):
    lines, line = [], ''
    for word in text.split():
        trial = line + ' ' + word if line else word
        if text_width(trial, glyphs) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def encode(lines):
    out = bytearray()
    for n, line in enumerate(lines):
        if n:
            out.append(2)
        for part in re.split(r'(<[9a]>)', line):
            if part in ('<9>', '<a>'):
                out.append(int(part[1], 16))
                continue
            for ch in part:
                if ch == '…':
                    out.append(ELLIPSIS)
                elif 0x20 <= ord(ch) < 0x7f:
                    out.append(ord(ch))
                else:
                    raise SystemExit(f'character {ch!r} has no glyph, in: {line}')
    return out


def dump():
    rom = paths.ROM.read_bytes()
    rom = rom[len(rom) % 0x8000:]
    path = paths.TRANSLATION / 'script' / 'events.txt'
    head = ['# Event dialogue. One block per message; EN lines are joined and wrapped by the build',
            f'# to {BOX_WIDTH} px, about 30 characters, two lines on screen.',
            '# The @ line: address, then clear (the box empties first), newline or more (carries on',
            '# in the same box), then the end code. Not for editing.',
            '# <9><a> is the wrestler\'s name: keep both, in that order. Only A-Z a-z 0-9, ASCII',
            '# punctuation and the ellipsis character.', '']
    out = head
    for a, n, s, end in messages(rom):
        how = 'clear' if s[:1] == '\f' else 'newline' if s[:1] == '\n' else 'more'
        body = s.lstrip('\f\n').replace('\f', '\n')
        out.append(f'@ {a:04x} {how} {end:x}')
        out += ['JP ' + line for line in body.split('\n')]
        out.append('')
    path.parent.mkdir(exist_ok=True)
    if path.exists():
        print('kept', path)
    else:
        path.write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'{path}: {sum(1 for x in out if x.startswith("@"))} blocks')


def build_step(path, files):
    """Text step for build.py: expand the ROM, write bank $D0 and $D1."""
    import snes
    import asm65816
    rom = bytearray(files.get('/rom.sfc'))
    r = snes.Rom(rom)
    r.expand(0x200000)
    rom = r.data
    glyphs = load_font()
    # D1: the renderer
    src = (paths.ROOT / 'tools' / 'asm' / 'vwf.asm').read_text(encoding='utf-8')
    src = (src.replace('WIDTHS,X', '$D10C00,X').replace('FONT,X', '$D10D00,X')
           .replace('PROMPTS,X', '$D11400,X').replace('PROMPTCELLS,X', '$D11410,X')
           .replace('PROMPTSTEP,X', '$D11420,X'))
    code, _ = asm65816.assemble(src, 0xD10000)
    if len(code) > 0xB00:
        raise SystemExit(f'renderer too big: {len(code):#x}')
    rom[CODE_BANK:CODE_BANK + len(code)] = code
    for c in range(0x20, 0x80):
        adv, rows = glyphs[c] if c in glyphs else (8, bytes(16))
        rom[CODE_BANK + 0xC00 + c - 0x20] = adv
        rom[CODE_BANK + 0xD00 + (c - 0x20) * 16:CODE_BANK + 0xD00 + (c - 0x20) * 16 + 16] = rows
    # the cells the scenario bubble's tilemap counts: 22
    rom[CODE_BANK + 0xB00:CODE_BANK + 0xB17] = b'A' * 22 + b'\x0b'
    misc = {b.id: b for b in blocks.BlockFile(paths.TRANSLATION / 'text' / 'misc.txt').blocks}
    # password strings: original cells 14, 11, 9
    at = 0x1440
    for i, cells in enumerate((14, 11, 9)):
        en = ' '.join(misc[f'password{i}'].tagged('EN')) or 'Password'
        if text_width(en, glyphs) > cells * 16:
            raise SystemExit(f'password{i}: wider than its {cells} cells')
        data = bytes(encode([en])) + b'\0'
        rom[CODE_BANK + at:CODE_BANK + at + len(data)] = data
        rom[CODE_BANK + 0x1400 + i * 2:CODE_BANK + 0x1402 + i * 2] = at.to_bytes(2, 'little')
        rom[CODE_BANK + 0x1410 + i * 2:CODE_BANK + 0x1412 + i * 2] = cells.to_bytes(2, 'little')
        rom[CODE_BANK + 0x1420 + i * 2:CODE_BANK + 0x1422 + i * 2] = (cells * 0x40).to_bytes(2, 'little')
        at += len(data)
    # battle name bars: 16-bit pointers at $D1:1700, words tile | $3000 ending in 0 (6 px per letter,
    # 4 after I); letters A-H $C0, I-P $D0, Q-X $E0, Y $F2, Z $F3, - $F4
    # the table is by sprite row; rows $12-$14 share one bar, Hyperspace Mask's
    at = 0x1780
    for i, bar in enumerate(list(range(18)) + [18, 18, 18, 19, 20, 21, 22]):
        en = ' '.join(misc[f'bar{bar:02d}'].tagged('EN'))
        data = b''.join(bar_tile(c).to_bytes(2, 'little') for c in en) + b'\0\0'
        rom[CODE_BANK + 0x1700 + i * 2:CODE_BANK + 0x1702 + i * 2] = at.to_bytes(2, 'little')
        rom[CODE_BANK + at:CODE_BANK + at + len(data)] = data
        at += len(data)
    # wrestler names: u16 count, u16 codes, $000B (the table the name code reads)
    at = 0x2000
    for i in range(32):
        en = ' '.join(misc[f'name{i:02d}'].tagged('EN')) or '-'
        cells = (text_width(en, glyphs) + 15) // 16
        data = cells.to_bytes(2, 'little') + b''.join(ord(c).to_bytes(2, 'little') for c in en) + b'\x0b\0'
        rom[CODE_BANK + 0x1480 + i * 2:CODE_BANK + 0x1482 + i * 2] = at.to_bytes(2, 'little')
        rom[CODE_BANK + at:CODE_BANK + at + len(data)] = data
        at += len(data)
    # D0: copy of the original text area, then the English
    orig = bytes(rom[BANK:BANK + 0x10000])
    rom[TEXT_BANK + 0xCD00:TEXT_BANK + 0x10000] = orig[0xCD00:]
    done = {}
    bl = {b.id: b for b in blocks.BlockFile(path).blocks}
    at, missing = 0, 0
    for a, n, s, end in messages(rom[:0x100000]):
        b = bl[f'{a:04x}']
        en = b.tagged('EN')
        if not en:
            missing += 1
            continue
        lines = wrap(' '.join(en), glyphs)
        data = encode(lines) + bytes([end])
        how = b.meta.split()[0] if b.meta else 'more'
        data = (bytes([5]) if how == 'clear' else bytes([2])) + bytes(data)
        key = bytes(data)
        if key in done:
            where = done[key]
        else:
            where, done[key] = at, at
            rom[TEXT_BANK + at:TEXT_BANK + at + len(data)] = data
            at += len(data)
        if n < 3:
            raise SystemExit(f'message {a:04x} is {n} bytes: no room for the jump')
        rom[TEXT_BANK + a:TEXT_BANK + a + 3] = bytes([0x0E, where & 255, where >> 8])
    if at > 0xCD00:
        raise SystemExit(f'English is {at:#x} bytes, bank $D0 holds {0xCD00:#x}')
    print(f'text: {at:#x} bytes of English, {missing} messages left in Japanese')
    files.put('/rom.sfc', bytes(rom))


def main(argv=None):
    argv = paths.configure(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ['dump']:
        dump()
    elif argv[:1] == ['widths']:
        g = load_font()
        rows = []
        for b in blocks.BlockFile(paths.TRANSLATION / 'script' / 'events.txt').blocks:
            for line in wrap(' '.join(b.tagged('EN')), g):
                rows.append((text_width(line, g), line))
        for w, line in sorted(rows)[-10:]:
            print(w, line)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
