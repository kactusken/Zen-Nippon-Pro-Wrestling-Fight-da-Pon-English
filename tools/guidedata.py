#!/usr/bin/env python3
"""Fill the data block of the player's guide (docs/guide/index.html).

  python3 tools/guidedata.py [--check]

Cards, decks, signature cards and who may equip what come from the original's tables, with the
patch's names from translation/text/. A card's reversal damage and kind come from docs/MATCHES.md,
and the boards from docs/story/board-*.md: both were worked out from the move and board scripts by
the research tools, which are not part of the build. --check only reports whether the page is up
to date (exit 1 if not); tools/check.py runs it.
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pagedata  # noqa: E402
import paths  # noqa: E402

CARD_TABLE, DECKS, SPRITES, ALLOWED = 0x0454, 0x6230, 0x73D0, 0x5D80  # file offsets (HiROM C0:xxxx)
N_CARDS, N_PLAYABLE, N_WRESTLERS = 42, 16, 30

BOARDS = [
    ('sq0-ch1', 0, 'All Japan Pro Wrestling Roll Call!', 'Baba'),
    ('sq1-ch2', 1, 'Rusher Kimura Does His Best', 'Rusher Kimura'),
    ('sq2-kawada', 2, 'The Case of the Exploding Stretch Plum!', 'Kawada'),
    ('sq3-misawa', 3, 'The Case of the Turncoat Foreign Squad', 'Misawa'),
    ('sq4-tsuruta', 4, 'Zebra Mask: Friend or Foe?', 'Tsuruta'),
    ('sq5-hawaii', 5, 'The Case of the Kidnapped President Baba', 'your pick'),
    ('finale', 6, 'Showdown! The Case of the Evil Wrestling Society', 'Baba'),
]
SPACE = re.compile(r'^\s*(\d+) \(\s*(\d+),\s*(\d+)\) (.*?)\s*-> ([\d, ]*|end)\s*(\*?)\s*$')


def card_table(rom):
    """The 43 cards (42 and FALL), by id, from the table and translation/text/cards.csv."""
    with open(paths.PROJECT / 'translation/text/cards.csv', encoding='utf-8') as f:
        names = {int(r[0]): r for r in csv.reader(f) if r and r[0].isdigit()}
    names[N_CARDS] = (N_CARDS, 'フォール', 'FALL', 'Fall')  # drawn in the art, not in the csv
    extra = {}
    for line in (paths.DOCS / 'MATCHES.md').read_text(encoding='utf-8').splitlines():
        c = [x.strip() for x in line.split('|')]
        if len(c) == 13 and c[1].isdigit():
            extra[int(c[1])] = (c[9], c[10])
    if len(extra) != N_CARDS + 1:
        sys.exit(f'docs/MATCHES.md: found {len(extra)} rows of the All cards table, expected 43; '
                 'fix the table or the parser in tools/guidedata.py')
    out = []
    for i in range(N_CARDS + 1):
        b = rom[CARD_TABLE + i * 8:CARD_TABLE + i * 8 + 8]
        rev, kind = extra[i]
        out.append({'id': i, 'label': names[i][2], 'name': names[i][3], 'jp': names[i][1],
                    'power': (b[1] >> 4) * 4, 'rand': max((b[1] & 15) - 1, 0), 'guard': (b[2] >> 4) * 4,
                    'dmg': b[5] * 4, 'cd': (b[0] & 0xF8) * 4, 'rev': rev, 'kind': kind})
    return out


def wrestlers(rom):
    """Everyone with a deck: name, deck, signature, and the cards they may equip."""
    text = (paths.PROJECT / 'translation/text/misc.txt').read_text(encoding='utf-8')
    names = [m[1] for m in re.finditer(r'@ name\d\d\nJP .*\nEN (.*)', text)]
    out = []
    for i in range(N_WRESTLERS):
        row = ALLOWED + (rom[SPRITES + i] & 0x7F) * 48
        flags = rom[row:row + N_CARDS]
        out.append({'i': i, 'name': names[i], 'story': i >= N_PLAYABLE,
                    'deck': [c for c in rom[DECKS + i * 5:DECKS + i * 5 + 5] if c != 0xFF],
                    'sig': [c for c in range(N_CARDS) if flags[c] & 2],
                    'can': [c for c in range(N_CARDS) if not flags[c] & 0x80]})
    return out


def boards(cards):
    """Each board's spaces. A space: [number, x, y, kind, card id or None, next spaces, fork]."""
    out = []
    for key, square, title, hero in BOARDS:
        spaces = []
        for line in (paths.DOCS / 'story' / f'board-{key}.md').read_text(encoding='utf-8').splitlines():
            m = SPACE.match(line)
            if not m:
                continue
            what, card = m[4], None
            if what.startswith('CARD TROUBLE'):
                kind = 'T'
            elif what.startswith('CARD:'):
                kind = 'c'
                c = re.search(r'\(card (\d+)\)', what)
                card = int(c[1]) if c else None
            elif what.startswith('MATCH'):
                kind = 'M'
            elif what.startswith('STORY'):
                kind = 'E'
            elif what.startswith('GOAL'):
                kind = 'G'
            elif what.startswith('START'):
                kind = 'S'
            else:
                kind = '?'
            nxt = [int(x) for x in m[5].replace(',', ' ').split() if x != 'end']
            spaces.append([int(m[1]), int(m[2]), int(m[3]), kind, card, nxt, 1 if m[6] else 0])
        if not spaces or any(s[3] == '?' for s in spaces):
            sys.exit(f'docs/story/board-{key}.md: unreadable spaces; fix the parser in tools/guidedata.py')
        out.append({'key': key, 'square': square, 'title': title, 'hero': hero, 'spaces': spaces})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--check', action='store_true', help='only report whether the page is up to date')
    args = ap.parse_args(paths.configure(sys.argv[1:] if argv is None else argv))
    rom = paths.ROM.read_bytes()
    cards = card_table(rom)
    data = {'cards': cards, 'wrestlers': wrestlers(rom), 'boards': boards(cards)}
    pagedata.write(paths.DOCS / 'guide' / 'index.html', data, check=args.check)
    print(f'guide data: {len(cards)} cards, {len(data["wrestlers"])} wrestlers, {len(data["boards"])} boards')


if __name__ == '__main__':
    main()
