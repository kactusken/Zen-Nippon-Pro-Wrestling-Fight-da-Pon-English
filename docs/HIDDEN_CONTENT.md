# Hidden content

Unlockables, debug features, button codes, cut and unused content. Every find says how sure it
is:

- *verified in game* - seen in an emulator (with the date, and the build or code used to get there)
- *from the code* - read in the disassembly, not seen running
- *from the data* - in the game's files or tables, whether or not the code uses it
- *from a guide* / *from fans* - a published source, not yet matched with the code

Addresses: `$bank:addr` CPU addresses on the original ROM.
Optional patches that switch some of this on are in [PATCHES.md](PATCHES.md).

**Prior art (2026-11-02).** Nothing confirmed. *From fans, unverified:* search listings show The
Cutting Room Floor's page for this game as a stub, categorised under debugging functions, a hidden
sound test and a hidden level select, with no details seen. The article itself could not be read,
so no input codes are known. Natsume Championship Wrestling's TCRF page says a hidden credit is
found in most of the SNES Zen Nihon Pro Wrestling games; this game has one ([below](#hidden-credit)).
English and Japanese searches found no code lists, guides or cheat pages for this game.

## Contents
- [All cards code](#all-cards-code) · [Sound test code](#sound-test-code) · [Soft reset](#soft-reset) · [Debug menu](#debug-menu) · [Zebra Mask](#zebra-mask) · [Hidden credit](#hidden-credit) · [Dead developer code](#dead-developer-code) · [Unused content](#unused-content) · [Searched and not found](#searched-and-not-found) · [How to see it yourself](#how-to-see-it-yourself)

Pad input for both codes is read at the title menu; a wrong press restarts the code. The button order
is decoded from the ROM tables.

## All cards code
*seen headless* (2026-11-01, original ROM) for the cards; the R skip is *from the code*

At the title menu: **Up Up Up Down Down Left Right Right Up Down Right Left Left** (table $C0:71D4).
Gives all 42 cards ($7E:7400-743F = 0), plays sound $1B and sets $0824, after which **R skips any story
script** ($C0:DA77).

## Sound test code
*seen headless* (2026-11-01, original ROM)

At the title menu: **Up L R Down L R Left L R Right R L** (table $C0:7184). Opens "The Fight Da Pon!
Music Driver Ver1.01B": Up/Down picks music $00-$19, A plays, B fades, Start leaves. Song names are at $C6:F3B7.

## Soft reset
*seen headless* (2026-11-02, original ROM)

Anywhere, **hold Start and press Select**: the interrupt handler jumps to the reset code ($C0:8A6E, JMP $8000)
and the game restarts at the logo. There's no saving, so unnoted progress is lost.

## Debug menu
*seen headless* (2026-11-02, original ROM plus one byte); *from the code*

The developers' menu is still in the game, and so is the button combination that opened it: **hold X and press
Select**, tested every frame at $C0:8A14. The shipped game turned it off by changing one instruction: the
`BEQ` after the Select test at $C0:8A22 became `BRA`, so the three lines that open the menu ($38=1, $3A=0, $3C=0) are
always jumped over. It's the only test in bank $C0 bypassed this way. Changing that byte back gives the combination
its original effect, on any screen: the `(English) (Debug Menu)` patch ([PATCHES.md](PATCHES.md#dev-menu)).

Up/Down moves, A runs the row, and the cursor is remembered. Row N sets $3A to N+1 (table $C0:BBBF; labels $C0:B462). The menu is
drawn over whatever screen was showing, and nothing leaves a row except its own ending or the soft reset.

| Row | Label | Handler | What it does |
|---|---|---|---|
| 0 | -------- | C0:BDB9 | Two hex counters at the top left: pad 1 Up/Down, pad 2 Up/Down |
| 1-3, 6 | -------- | RTS | Nothing |
| 4 | CardTest | C0:C04B | The match loop, with nothing set up: wrestlers from RAM, GIVE UP! at once when tried |
| 5 | COUNT!! | C0:CFCF | The pinfall count, nothing visible without a match |
| 7 | EVENT--- | C0:D8FF | Script tester: Up/Down picks a script in hex, A runs it |
| 8 | -------- | C0:E762 | Scene viewer, see below |
| 9 | -------- | C0:2827 | Board 1 loader with fixed values ($0668=$10), ends on a blank screen |
| 10 | CARD-SEL | C0:BC2E | Deck edit |
| 11 | PLY--SEL | C0:BC1F | Wrestler select |
| 12 | STAGESEL | C0:BC10 | Scenario Select, with its graphics corrupted from this menu |
| 13-19 | EVENT_01-07 | C0:BC63-BD60 | Starts squares 0-5 and the finale at their title |
| 20 | SoundTes | C0:7247 | Sound test |
| 21 | TITLE--- | C0:6A7D | Title screen |
| 22 | STAFF--- | C0:6374 | Staff credits |
| 23 | PRSET--- | C0:BBF9 | Preset match |
| 24 | 1P vs 2P | C0:7578 | Battle wrestler select |

Rows 13-19 and 12 are the nearest thing to the "level select" listings mention. *Seen headless:* rows 0, 4, 5, 7-13, 18,
19, 23, 24 on the original plus the byte; 13 also on the English build; 21 and 22 opened from a board.

**Scene viewer (row 8).** Shows `SIIN_NO=` (romaji "scene no") and three hex digits: Up/Down the board number $012C, L/R the scene
$0668, A loads that board's tile sets (tables $C0:E72C, $C0:E6E0). It loads tiles only, so opened from a board the old
tilemap turns to noise, and from the title the whole screen does.

**Unused labels.** After the 25 rows the label table goes on to $C0:B6F1 with 16 more names and nothing reads them:
`1P :00`, `2P :00`, `WAZA:00` (move), `OK??:00`, `PAL1`, `PAL2`, `STE1-3`, `DAME:00` (damage), `SW1`, `SW2`, `-X-`, `SW4`.
They look like the labels of a match inspector whose code has been removed.

## Zebra Mask
*seen headless* (2026-11-02, original ROM with a RAM write); *from the data*

Zebra Mask is a nearly complete wrestler, though the game never lets you fight him. At wrestler index 30 the sprite group ($17, table $C0:73D0), portrait
($12E0, table $C0:13ED), name bar (シマウマ, table $C0:142F by group) and a card row (table $C0:5D80) are all in place, and group
$17 holds a full set of 126 ring frames. Story scenes show only a few of them. Missing are his name (a placeholder at
$C0:3D75), his deck ($C0:6230 runs into other data at that index) and anything that sets index 30.

Forcing the opponent to 30 at C0:73F3 ran a full match against Baba for about 4600 frames with no crash: moves, knockdowns and pins
all work. One computer card slot drew garbled, probably the missing deck.

## Hidden credit
*from the data*

$C1:DCBA, in ASCII between two data tables, with no pointer to it: `  Osaka Natsume Software T.NOH  `. It's never displayed.

## Dead developer code
*from the code*: nothing calls these.

- **Raster bars**, $C0:8A30 and $C0:8A4C, right after the debug test: blank the screen for a moment, the first while Y alone is held,
  the second after waiting on the scanline counter. The usual way to see how much of a frame the code takes.
- **Control toggle**, $C0:C031, right before the match loop: hold X, press Y to flip $01C6, which says whether player 2 is the
  computer. Only a poke of $01C6 reaches the effect now.
- **Card helpers**, $C0:E203: set, clear and read a card's flag.
- **Disabled deck-edit hooks**, $C0:3754 and $C0:388D: five NOPs after the pad read, probably a removed call.

Also unused: the pad reader handles a multitap ($0860-$0866), but nothing reads players 3-5.

## Unused content
*from the data*; full list in [STORY.md](STORY.md#8-hidden-and-unused)

- 32 messages have no pointer: chapter stage names, a trimmed Mecha Baba exchange, a line after the first
  Red Bear scene, and two prompts ("Choose a wrestler to use.", "Choose your opponent.").
- Script 13; match slots 04, 0C, 13, 1C, 1D, 1F, 28 and up; maps 0, 1, 8-11, 13-15.
- Two spaces the walker can't reach: map 6 (30,31) card, map 4 (70,16) match.
- Each wrestler's stat table at $C0:05CD: a coding slip means row 0 is always read, so all wrestlers share
  Baba's numbers ([MATCHES.md](MATCHES.md#4-wrestler-stats-the-data-is-dead)).
- **Orphan tile set**, $C8:0000: an LZ block ($3D60 bytes, 491 tiles) with sand, sea and paths, missing from the 15-entry
  picture table $C0:E6E0 and from every literal loader. The 256 palette bytes at $C1:D650, the one slot table $C1:D230 skips,
  color it naturally, which suggests they belong together. No map fits it, so it's art for a board that was never built, or
  was removed. The loader at $C0:E90C copies from the middle of this block; that address looks stale.
- **Spare frames**: Eigen, Misawa and Kikuchi each have 13-17 ordinary poses in their sprite sets that no animation shows; Mecha
  Baba has one seated pose. About $2C80 bytes of tile scraps in banks $C9-$CF are reached by nothing, none of it a whole picture.
- **Duplicates**: $C5:D404 unpacks to the same bytes as music table entry 3; picture id $0C repeats $0B.

## Searched and not found
- No other pad code: the title's two checks ($C0:719E, 71F0, called at C0:6D0C-0F) are the only sequence checks. All 84 reads
  of the pad variables were listed by mask and the unusual ones read; none is another code.
- No password is special: entry only runs the checksums, with no comparison to a fixed string.
- No unused music: the 26 songs are all played (01-07 are match themes picked at C0:D6EA). Ids $1A-$1F reuse other songs' data.
- No read-but-never-written variable turned out to be a switch: the ones checked are hardware shadows and high bytes.
- Sound effects weren't compared with their uses.
- Bank $C4 from $068F to $CD20 was walked byte by byte: the only unreached runs are small and hold no
  message opcodes, so there's no cut scene there.
- Time limit, count-out, ring-out, draw: no code for any of them.

## How to see it yourself
| Find | How |
|---|---|
| All cards, R skip | The code above at the title |
| Sound test | The code above at the title |
| Soft reset | Hold Start, press Select |
| Debug menu | Apply the `(Debug Menu)` patch, then hold X and press Select on any screen |
| Hidden credit | A hex editor, file offset 0x1DCBA |
| Zebra Mask match | Write 30 to $7E:01D5 each time the CPU reaches $C0:73F3, with a match starting |
| Orphan tile set | `lz.py` on file offset 0x80000 |
