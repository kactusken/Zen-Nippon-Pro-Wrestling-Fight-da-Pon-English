# Technical notes - Zen Nippon Pro Wrestling - Fight da Pon

**Conventions:** numbers in hex with `0x`; addresses are RAM addresses unless marked as file
offsets; `u16`/`u32` little-endian unless marked BE. Findings are marked *verified in game* or
*from the code*.

## Contents
- [Image](#image) · [Disc layout](#disc-layout) · [Executable and memory](#executable-and-memory)
- [Archives and compression](#archives-and-compression) · [Text](#text) · [Images](#images)
- [Open questions](#open-questions)

## Image
`Zennihon Pro Wrestling - Fight da Pon! (J).smc`, 1048576 bytes, SHA-1 `52aa5ce4612b81c90fd07f6c3dc9a712afb32668`.

No-Intro: *Zen-Nihon Pro Wres - Fight da Pon! (Japan)*, matched by `datcheck.py` (headerless, CRC32
`379645bd`). No SRAM (cart type `$00`): the title screen offers GAME START and PASSWORD, so progress
is kept in passwords - *verified in game* for the menu (2026-11-01); the format is in
[STORY.md](STORY.md#6-password-code-c05443-5570-confirmed-headless-both-ways).

**Prior art (2026-11-01).** No English translation or partial patch turned up, and no tools for
this game's formats. Web searches only; romhacking.net, Data Crystal and GameFAQs were not read
directly. Released in Japan 1994-06-25, published by Masaya, developed by Natsume, cartridge
SHVC-JF (Giant Bomb, arcade-history listing via search). Listings describe its battles as
turn-based; *from the code* they are real time, played with cards on a cooldown ([MATCHES.md](MATCHES.md)).

## Disc layout
| | |
|---|---|
| Title | `NCS FIGHT DA PON` |
| Map | HiROM FastROM (`$31`), header at `0xffc0` |
| Size | 0x100000 bytes (8 Mbit), 16 banks of 64 KB |
| ROM | $C0:0000 - $CF:FFFF |
| Cart | type `$00`, SRAM 0 KB |
| Reset | $00:8000 |
| Checksum | `0xa565` (fixed by tools/disc.py on every build) |

## Executable and memory
All code is in bank $C0, including $C0:0000-7FFF, with no JSL in reached code. The game rules are in
[MATCHES.md](MATCHES.md) (RAM map in its section 9) and [STORY.md](STORY.md) (states and flags in its section 7).

## Archives and compression

## Text
*Verified in game* (2026-11-01) unless marked.

- Encoding: one byte per character, $10-$FF; $01 xx is the second page, code $100 | xx. Table in
  `tools/font.tbl`. Control codes below $10: $00 and $0B end a message, $02 new line, $05 clear,
  $08 a 16 px space, $09 and $0A a wrestler's name, $06/$07/$0C-$0F take one byte.
- Font: 16x16 1bpp, inverted, 32 bytes a glyph, at $C8:C01C (code * 32).
- Messages: bank $C4 from $CD20 to $FFF3, 862 strings, reached by event opcodes $2C and $42 (pointer
  at +3), by the tables $C0:42CF and $C0:44A3 and by literals at $C0:7679, 7756, 7763.
- Box: buffer $7E:E000, 2 lines $300 apart, 11 cells of $40 bytes each (TL TR BL BR tiles, 2bpp, high
  plane is the glyph). A line that is full scrolls up.
- Password strings at $C0:4DD1, table $C0:4DCB.
- Wrestler names: $C0:3D75 table, u16 count, u16 codes, $000B. Battle name bars: $C0:142F table, words
  (sprite tile | $3000) ending in 0.
- Name cell layouts: $C0:3D3D table of byte offsets per cell count (1-6 cells); the original spread 2 and 3 cells
  apart (one kana a cell), patched contiguous at $C0:3D4D/$3D51 (*seen headless* on Otasuke Select, awaiting owner). The tilemap
  writer is $C0:413B (cell = 4 tiles TL TR BL BR from tile $80), the name drawing $C0:4293.
- Staff credits use their own routine ($C0:64FB).

### How the English gets in
Bank $D0 starts with a copy of the original text area; each message's first 3 bytes there are a
jump (new code $0E lo hi) to the English at $D0:0000 up, so no pointer changes. The jump reads on at once ($D1:0010, back to $C0:1956): the end test at $C0:4379 looks at the byte before the pointer, which after a bare jump would be another message's end code (*seen headless*, card screens). The five text reads
go to bank $D0. Bank $D1 holds the renderer (`tools/asm/vwf.asm`), widths, font (`tools/fonts/vwf.txt`)
and names. ROM expanded to 16 Mbit.

### Bugs of the original game, fixed in the patch
*Seen headless*, on the original with the owner's state and on the build. Before a scene's first line the portrait tick $C0:E0E6 draws the portrait object while its fields are cleared: tile base 0, so portrait frames land on the first wrestler's sprite tiles ($7F:0000). The board's gauge also stays on BG3 until then. The hook at $D1:0014 skips the tick in that case and clears the gauge once. Seen in square 3's hospital scene.

## Images
- LZ blocks: `tools/lz.py`. Move cards: block at $C7:0000, unpacks to $7F:4000; 42 cards of 4x5 tiles,
  $280 bytes each, label in the top row. Rebuilt in bank $D2 (`tools/cards.py`); read by $C0:D4ED,
  the table $C0:E6E0.

## Title art
The Otasuke Select title (now PARTNER SELECT, `tools/title.py`, `translation/text/title.txt`) is 16x16 gold letters made of
2x2 metatiles: table at $C1:8DE8 (entries 101-108 = this title, TL TR BL BR words), tiles in the block at $C4:B866 (BG1 chr at
VRAM $4000, shared with the CARD BATTLE / WRESTLER SELECT / WHAT'S CARD titles). Tiles $62-$67 were only the K and the U
bottoms, so they carry the new P (bottom half; top is the R's) and N (H's stems + diagonal). Both blocks are repacked in place.
*Seen headless* (owner's right-before savestate).

## Open questions
-
