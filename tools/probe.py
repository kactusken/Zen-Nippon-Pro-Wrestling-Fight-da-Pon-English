#!/usr/bin/env python3
"""The game's text areas on screen right now and the room each one has - what the kit's headless
runner (testing/drive.py) checks on every screen it visits. Fill it in per game once the renderer
is known (FRAMEWORK.md section 7, "Room from the game itself").

  python3 <kit>/testing/drive.py run [--image IMG] STEP... check NAME     one screen
  python3 <kit>/testing/drive.py sweep [--image IMG]                      every private/work/sweep/*.steps

REGIONS names the memory areas() reads; drive.py fetches them at each `check` step:
  Saturn  lwram hwram vdp1 vdp2 (big-endian, as the Saturn sees it)
  Dreamcast  ram (16 MB from 0x8C000000, little-endian; Flycast gives no video RAM)
  PS2     ram (32 MB from 0x00000000, little-endian; the core gives no GS video memory)
  SNES    wram vram cgram oam
  GBA     ewram iwram io pal vram oam (little-endian; tools/gbagfx.py bg_cells reads a text
          background's map from vram and io)

areas(mem) gets {region: bytes} and returns one dict per text area in use:
  area   a stable name: the same area on the same screen gets the same name in every run
         (a slot number, a window, a tilemap rectangle)
  used   glyphs (or tiles) the text in it takes now
  room   what the area holds, None if unknown (the next area's start, the window's width...)
  where  optional: screen position or address, for the report
  id     optional: the translation block id it shows (file|key, as in rooms.csv), when the game
         keeps a pointer to the string
  over   optional: True/False to override `used > room` (a pixel measure, a hang flag)
How the game shows its text decides how room is found: a list of text objects with their own
video-memory areas (Fire Pro Wrestling S: slots in work RAM, room = the gap to the next slot's
address), a fixed window (room = its width in tiles), a tilemap (room = blank cells up to the
next non-blank one). Run it on the ORIGINAL first: the Japanese shows each area's real room.
"""
REGIONS = ['wram']
BUFFER = 0xE000         # the text box: 2 lines $300 apart, 11 cells of $40 bytes


def areas(mem):
    """The box's used cells, line by line. English is wrapped to the box by the build, so the room
    check is a formality here; the areas tell the sweep when the text on screen changed."""
    w = mem['wram']
    out = []
    for line in range(2):
        base = BUFFER + line * 0x300
        cells = [w[base + i * 0x40:base + (i + 1) * 0x40] for i in range(11)]
        used = max((i + 1 for i, c in enumerate(cells) if c.count(0xff) != len(c)), default=0)
        if used:
            out.append({'area': f'box{line}', 'used': used, 'room': 11})
    return out
