# Story mode

Source for the [player's guide](guide/index.html), from the original ROM. Names follow the English patch. Marks: *code* = from the code; *data* = from the ROM's tables; *seen headless* = watched running in Mesen on the original ROM, which is evidence but not an owner check. Nothing here is *verified in game* unless it says so. Run, log and step names refer to the project's private research folder.

Beside this file: [story/](story/) has the flow graph (`flow-*.md`) and every board space (`board-*.md`) for each square. Match rules are in [MATCHES.md](MATCHES.md).

The owner played squares 0 and 1 to the end on the English build (2026-11-01). The later chapters were reached by pokes, not played.

## 1. The big picture

- Story is data-driven and has **no conditions inside scripts**. All 77 story scripts are straight lines. Every branch is one of four things: a fork on a board, a match result, the Scenario Select choice, or the wrestler picks. *code + data*
- The chain is: script -> after-script action (table $C0:2A37, 2 bytes per script) -> board / match / next script. After a match, table $C0:2AD2 (4 bytes per opponent slot: action, arg for a win, arg for a loss, flag) picks what comes next. *code: C0:DC0B, C0:D25B*
- Script table: $C4:37FD, 77 entries (00-4C) in use; entry 4D is $3244, not a script. Moves in a match use the same interpreter from table $C4:0000. *code*

### Title menu *seen headless, code C0:6D08*
GAME START / PASSWORD, then SCENARIO / BATTLE, then 1P VS 2P / 1P VS COM. B goes back. Left alone it runs attract matches, one wrestler pair per pass (table $C0:6C8F, slot $20).

### Scenario Select *seen headless (m1.png), code C0:4720*
Six squares, 3 by 2 ($066A = 0-5). Left/Right step and wrap, Up/Down jump by 3. A starts a square; a cleared one buzzes.

| Square | Title ($C0:44A3) | Enter | First script | You play | Board |
|---|---|---|---|---|---|
| 0 top left | All Japan Pro Wrestling Roll Call! | $3A=$0E | 00 | Baba | map $C |
| 1 top middle | Rusher Kimura Does His Best | $0F | 09 | Rusher Kimura | map 7 |
| 2 top right | The Case of the Exploding Stretch Plum! | $10 | 37 | Kawada | map 3 |
| 3 bottom left | The Case of the Turncoat Foreign Squad | $11 | 20 | Misawa | map 5 |
| 4 bottom middle | Zebra Mask: Friend or Foe? | $12 | 30 | Tsuruta | map 2 |
| 5 bottom right | The Case of the Kidnapped President Baba (shown as "The Case of ????????", $CDDF, while locked) | $13 | 3F | your choice | map 6, then map 4 as Baba |

- All first five squares are open from the start, in any order. *seen headless (b0-b4.steps, each reached from a new game), code*
- A cleared square is recoloured (palette change at C0:45FE). The sixth is drawn with an X until squares 0-4 are all cleared ($7440-$7444 = 0), then its art appears; picking it locked buzzes. *code C0:45CC, 47CE; X seen headless*
- Square 5 needs nothing else. Cleared flags: scripts 08 (0), 1F (1), 3E (2), 2F (3), 36 (4), and for square 5, on reaching script 45 ($7445). *data, table 2A37*

### Finale
Script 44 (end of the Spider Crab base) -> script 45 is special: action 00 with arg $45 sets $7445 and shows the password first, then runs 45 (the final chapter, title D91E "Showdown! The Case of the Evil Wrestling Society"), which plays as Baba on map 4. *code C0:DD22, 5163, 2BDB*
A password with all six flags set jumps straight to script 45. *seen headless p3.steps: password 15HAAAAAAAAA455C gave $0534=$45, $38=2*

### Otasuke (Partner) Select
Only in square 1 (Rusher Kimura), see section 4. Rusher has to pick one camp on the board (three-way fork) and then one wrestler. The list comes from $C0:49FA (three lists of 4 words, $FF ends). You then fight that wrestler; that wrestler takes the fifth team seat ($7E7490), which is written when you pick. *seen headless partner.png, code C0:4B75*

| List | Script | Camp | Wrestlers |
|---|---|---|---|
| 0 | 1A | Hansen, foreign squad | Hansen, Williams, Gordy, Patriot |
| 1 | 17 | Tsuruta, Holy Demon Army | Tsuruta, Kawada, Taue |
| 2 | 14 | Misawa | Misawa, Kobashi, Kikuchi, Akiyama |

The pick changes who fights in the team match at the end, and nothing else in the story: scripts 16, 19 and 1C differ only in position. *data*

### Square 5 wrestler choice
After script 41: state $3A=$1A (C0:746D). Up/Down steps wrestler id, skipping ids 0, 2, 6, 7, 10 ($C0:747C): **Tsuruta (start), Misawa, Kawada, Taue, Kobashi, Fuchi, Kikuchi, Kimura, Akiyama, Eigen, Izumida**. Any Baba or foreign wrestler is out. The name is used in message E431. *code; seen headless 2026-11-02 on the original and the English build*: the WRESTLER SELECT title and one portrait, no name or other text, so the screen needs no translation.

### Teams *code/data, C0:DCA0-DCC6, 4D53*
| When | Team ($7450, $7460, $7470...) |
|---|---|
| Square 3 after script 23 | Misawa + Kikuchi |
| Square 3 after script 26 | Misawa + Kikuchi + Kobashi |
| Square 4 after script 33 | Tsuruta + Taue |
| Square 1, script 1D on | Kimura, Fuchi, Eigen, Izumida + the fifth pick |

`$0820` holds the tag setup so that random board matches also use the team (read at C0:2CC0, set from the *next* row of 2A37 at C0:DD56).

## 2. Board movement *code C0:1B9C-2600*, checked *seen headless* (walk.lua, gauge.lua, boardsim.py)

- Isometric map, walker one space at a time. Hold A: the 1-6 gauge at the left runs ($061C 0-35, moving 3 every 2 frames, with a random turn at each tick); release to stop. Spaces to walk = gauge/6 + 1, so 1 to 6. *seen headless: released at gauge 6-11, walked 2 spaces and stopped*
- No dice. Timing matters, but the gauge turns randomly. "Flip a card" refers to the card screen, not to movement. In 15000 frames of holding A, with the original RNG, time in each band: 1: 13%, 2: 20%, 3: 21%, 4: 22%, 5: 14%, 6: 10%. *seen headless, gauge.lua* The turn chance is `table $C0:1B94[gauge] / 128`; the table has only 8 meant entries and runs on into code bytes, so the top of the range behaves oddly. Reaches 35. *code + headless*
- Paths are one-way. At a fork the walker stops and you pick with the D-pad ($060A mask, table $C1:E0CC). There is no way back, so nothing repeats, except forks that rejoin.
- Spaces come from $C1:E546 (per map; word byte count, then x, y, action, arg; x,y = pixel >> 4). Tile attributes $C1:E1A8 give the one-way exits. boardsim.py walks this over the map dumped from WRAM ($7FC000): all spaces lie on the walked graph but two (below). This is *code + data*; a space's *look* was only sampled from screenshots: blue = card, yellow = match, red = card trouble, START and GOAL labelled.

| Action | Effect | Stops the walk? | Handler |
|---|---|---|---|
| 1 | Card: arg 0 random, else that card. "WHAT'S CARD?!" screen, A to flip | only when it is your last step | C0:2CA8 -> $059C=2 |
| 2 | Card trouble | last step | C0:2C98 -> $059C=9 |
| 3 (5) | Random match, arg = slot 0-6 | last step | C0:2CC0 -> deck screen, match |
| 4 | Story stop: run script arg | **always**, even mid-walk | C0:2C88 |
| 7 | Goal: run script arg | always | C0:2C88 |
| 6, 8-15 | Unused: empty handler | - | |
| 13 | Unused: would clear $7440[arg] and show the password | | C0:2C5C |

Spaces between events cost nothing. Only listed spaces count as steps.

**Card space** *seen headless t15, code C0:3392, 3317*: the card appears, A flips it. Shows "You got a new card!" ($CD64) or "You already have this card." ($CD76). Random pick when arg is 0 or after a match:
- Any flag $7440-5 still unset: uniform 0-41. If you own 16 or fewer cards it rerolls cards you own. Card 31 (Stretch Plum) rerolls in square 2 only.
- All six set: uniform over cards 0-15.

**Card trouble** *seen headless l_c, code C0:305F-3186, 42DD*: "Card trouble!!" ($CD31), a cursor bounces over the 42 card slots, slowing, and stops. Nothing you press matters. Length: 21-62 steps from a random start. If it lands on a card you own, you lose it, and it comes out of every deck ("You lost 1 move card!" $CD3E); otherwise "Your move card is safe!" ($CD53). So the chance is roughly cards owned / 42.

**Start** *seen headless, code C0:8B36, 3C71*: a new game owns cards 0-7 (Brainbuster, Piledriver, Backdrop, Lariat, Elbow, Power Slam, Cobra Twist, German Suplex). Deck edit before a match: 5 slots + EXIT, up to 42 cards. An empty deck loses at once with "GIVE UP!" and YOU LOSE. *seen headless slot19.png*

**Random match results** *code C0:D26E; headless with a forced winner, t4*: slots 0-6 end as a win -> random card; loss -> card trouble; back to the board at the same space. $018A = 0 for a win, anything else (including the time-up value $FFFF, C0:C5F3) is a loss.

| Slot | Used on | Opponent ($C0:733A, chosen by RNG) |
|---|---|---|
| 0 | square 0 | Grunt 1 |
| 1 | square 1 | Grunt 1 or 2 |
| 2 | square 3 | Grunt 2 or 3 |
| 3 | squares 4, 2 | Grunt 3 or 4 |
| 5 | one space on the finale board | Grunt 5 |
| 6 | square 5, finale | Grunt 5 |

Slot 4 is not used by any space. *data*

## 3. Story matches: lose and retry *code/data*

Every story opponent has a lose script. It always opens "Oh well... Time to flip a card!" ($CD20), gives a **free random card** (op 5A, the same card screen), and offers a rematch. So a story loss costs nothing and gains a card. Only random board matches cost cards. This is even remarked on by the villain in script 48 ("You lot can lose and fight again as often as you like"). 

Full slot table: `story/slots.tsv`. Row meaning, $C0:2AD2: action 00: win script, lose script. 12: Rusher's team match, 13: three-match gauntlet, 03: random. 

## 4. Chapters: events in order

Script numbers are hex; "lose X" means the retry script. Everything is *data* (tables) plus *code*. Message addresses: `story/scripts.txt`, graph: `story/flow-*.md`.

### Square 0: All Japan Pro Wrestling Roll Call! (Baba, map $C)
| # | Where | Script | Who, what | Then |
|---|---|---|---|---|
| 1 | start | 00 | Opening, Rusher late, nobody at the arena | board |
| 2 | space (54,39) | 03 | Fuchi, Izumida, Eigen and the VCR | board |
| 3 | (30,37) | 01 | Kobashi, Kikuchi, Misawa, Akiyama at camp | board |
| 4 | (30,25) | 02 | Tsuruta, Taue, Kawada | board |
| 5 | goal (30,17) | 04, 05, 06 | Foreign squad; arena; fake Baba, Hyperspace Mask | match slot 0D |
| 6 | | win 08 / lose 07 | Hyperspace Mask flees; All Japan begins | square 0 cleared, password |

Linear board, 28 spaces. No forks.

### Square 1: Rusher Kimura Does His Best (Rusher Kimura, map 7)
| # | Where | Script | Who, what | Then |
|---|---|---|---|---|
| 1 | start | 09, 0A, 0B | Red Bears' challenge; Baba makes Rusher captain | board |
| 2 | (54,39) | 0C | Fuchi | match slot 07: win 0E, lose 0D |
| 3 | (78,27) | 0F | Eigen | match slot 08: win 11, lose 10 |
| 4 | (54,25) | 12 | Izumida joins, no match in the end ("Just join already!!") | board |
| 5 | fork at (38,27) picks one camp | 17 (30,25) or 1A (26,15) or 14 (30,37) | Tsuruta, Hansen or Misawa; Otasuke Select | match with the pick: slots 0A, 09, 0B |
| 6 | | win 19 / 1C / 16; lose 18 / 1B / 15 | Lose: back to Otasuke Select | board |
| 7 | goal (42,53) | 1D | Red Bears | team match, below |
| 8 | | win 1F, 5th loss 1E | | square 1 cleared, password |

Team match: Wrestler Select screen with NEXT ENEMY *seen headless gauntlet.png*. Red Bears 1-5 in order (slots 0E-12). Each loss removes that wrestler of yours and the same bear comes back; five losses run script 1E and the whole match restarts. Win all five for script 1F. *code C0:D322, 4BF9*

### Square 2: The Case of the Exploding Stretch Plum! (Kawada, map 3)
Card 31 Stretch Plum is taken away on entry ($7E741F=$FF, C0:BD14) and does not appear as a random card here.
| # | Where | Script | Who, what | Then |
|---|---|---|---|---|
| 1 | start | 37, 38, 39, 3A, 3B | Kawada, Izumida, the truck, Hansen waits, off to the Hermit | board |
| 2 | goal (48,10) | 3C | Signboard, Hansen's Lariat brings the Plum back. Op 5C returns the card ($7E741F=0) before the match | match slot 1B (Hansen): win 3E, lose 3D |
| 3 | | 3E | Staredown | square 2 cleared, password |

No story stops on the way; two forks.

### Square 3: The Case of the Turncoat Foreign Squad (Misawa, map 5)
| # | Where | Script | Who | Then |
|---|---|---|---|---|
| 1 | start | 20 | Belt stolen | board |
| 2 | (86,9) | 21 | Patriot has Kikuchi | slot 14: win 23, lose 22 |
| 3 | (42,11) | 24 | Williams has Kobashi | slot 15 tag: win 26, lose 25 |
| 4 | (10,19) | 27 | Gordy at the hospital | slot 16 tag: win 29, lose 28 |
| 5 | goal (50,39) | 2A | Hansen at the school | slot 17: win 2C -> 2D, lose 2B |
| 6 | | 2D | USA Mask | slot 18: win 2F, lose 2E |
| 7 | | 2F | "Goes on and on" | square 3 cleared, password |

One fork at (70,13), rejoins before script 24. Kikuchi joins after 23, Kobashi after 26.

### Square 4: Zebra Mask: Friend or Foe? (Tsuruta, map 2)
| # | Where | Script | Who | Then |
|---|---|---|---|---|
| 1 | start | 30 | Mountain training, Zebra Mask, Taue and Kawada run | board |
| 2 | (42,45) | 31 | Grunt holds Taue (slot 19, Grunt 3) | win 33, lose 32 |
| 3 | goal (12,58) | 34 | Tutan Mask has Kawada | slot 1A tag with Taue: win 36, lose 35 |
| 4 | | 36 | Pharaoh's curse, Baba revealed as Zebra | square 4 cleared, password |

Fork at (54,37); both routes rejoin before script 31, so that stop is mandatory (checked by removing it from the graph).

### Square 5: The Case of the Kidnapped President Baba (your pick, map 6)
| # | Where | Script | Who | Then |
|---|---|---|---|---|
| 1 | start | 3F, 40, 41 | Hawaii, Black Wrestling Gang letter | wrestler choice, board |
| 2 | goal (22,15) | 42 | Grand Director Spider Crab | 3 matches in a row: slots 22 Hyperspace, 23 USA, 24 Tutan |
| 3 | | any loss 43 | Flip a card | restart at slot 22 |
| 4 | | win 44 | Baba woke up; underling names the hideout | flag $7445, password, finale |

### Finale: Showdown! The Case of the Evil Wrestling Society (Baba, map 4)
| # | Where | Script | Who | Then |
|---|---|---|---|---|
| 1 | start | 45 | Baba goes alone | board |
| 2 | goal (52,18) | 49 | Red Bear, Hyperspace, Tutan | 3 matches: slots 25 Hyperspace, 26 Red Bear 5, 27 Tutan |
| 3 | | any loss 4A | | restart at slot 25 |
| 4 | | win 4B, 46 | Spider Crab, the mirror | slot 1E Mecha Baba: lose 47 |
| 5 | | win 48, 4C | The ending | staff credits |

## 5. Ending *data, headless t12*
Script 48 (Spider Crab complains about the game's system; Baba's speech; the underling's tickets), script 4C (wordless, $C4:3897, music $17 then $19), then action $15: state $3A=$17 credits (text at $C6:F627). After 5147 frames from start they reach the copyright page, $3C=2, and the code just idles there: no exit, no return to title. Seen for 600 more frames. There is one ending and no branch. The wrestler you chose in square 5 only affects square 5.

## 6. Password *code C0:5443-5570, confirmed headless both ways*

16 characters, A-Z and 0-5 = values 0-31 (A=0, Z=25, 0=26, 5=31); grid also shows 6-9 which are values 32-35 and act as A-D because only 5 bits count. Blank cells are $FF, value 31. Screen: 4 groups of 4 (*seen headless pw_in1*), keys ← → BS END.

Layout: char 0 = check, chars 1-15 hold 75 bits, 5 per character, low bit first, for bytes $7E7400+n (n = bit number). Bit set = byte has bit 7 clear.
| Bytes | Meaning |
|---|---|
| $7400-$7429 | owned cards 0-41 (0 = owned, 1 = also in a deck, $FF = not owned) |
| $742A-$742F | unused, stay $FF |
| $7430-$743F | check: each = NOT(7400+i XOR 7410+i XOR 7420+i) |
| $7440-$7445 | squares cleared, 0 = yes |
| $7446 | never set |
| $7447 | check: NOT of the XOR of $7400-$7446 |

Checks on entry: XOR of all 16 values, low 5 bits, must be $1F; $7447 must differ from the XOR; each word of $7430-3F must differ from the word XOR (so this one is weak). Any wrong: "Wrong password!". All pass: cards and squares restored, Scenario Select, or script 45 if all six squares are set. password.py does encode and decode: `python3 password.py cards=0,1 clear=0,3`.

With the 8 starting cards ($7400-7) (*all computed; the game's own display matched one, and it accepted two*):
| Cleared | Password |
|---|---|
| none | U5HA AAAA AAAA 4PAC |
| square 0 | G5HA AAAA AAAA 45AA |
| square 1 | X5HA AAAA AAAA 4PBA |
| square 2 | U5HA AAAA AAAA 4PCA |
| square 3 | S5HA AAAA AAAA 4PEA |
| square 4 | 45HA AAAA AAAA 4PIA |
| 0-4, sixth open | J5HA AAAA AAAA 45PA |
| all six, finale | 15HA AAAA AAAA 455C |
| 0-4, all 42 cards | U555 5555 5DAA Y5PA |
| all six, all 42 cards | G555 5555 5DAA Y55C |
Display check: cards 0-7, 16, 41 and square 1 gave 15HACAAAACIA0PBA from the game (p1.steps), the same as the encoder. Entry check: that password restored the cards (p2.steps).

## 7. Modes, states, flags

Top state $38 (table C0:8A89): 0 boot, 1 BBB0, 2 D8FF scripts, 3 C0:6582 load music ($72) then back to $78, 4 C0:1B9C board, 5 C0:2B7C screens via $059C.

$059C (table C0:2B8C): 0 run board event, 1 advance, 2 card screen, 3,4 Scenario Select, 5 deck edit then match, 6,7 wrestler select / team, 8 Otasuke Select, 9 card trouble, A password (shown if $0720=0, entry if 1), B card screen inside a script.
$3A with $38=1 (table C0:BBBF): 0 debug menu, 5 match, $15 sound test, $16 title, $17 credits, $18 preset match, $19 Battle wrestler select, $1A square 5 wrestler choice, $1B logo before the title, $0E-$14 start squares 0-5 and finale.

- **Battle** *seen headless, code C0:7578*: 1P VS COM ($01C6=0) or 1P VS 2P ($01C6=$FFFF). Pick from ids 0-15 only (no masks or grunts), slot $21, back to the select screen after each match. Wins are counted in $05BA/$05BC up to 10.
- **Deck edit** (no menu entry): before each story match and Battle. Move with the D-pad, EXIT is slot 5. *code C0:3622-3791*
- **WHAT'S CARD?!** is the title of the card screen. Not a mode. *seen headless*
- **Wrestler default decks** $C0:6230, used in Battle: `story/decks.tsv`.

Progress variables:
| Address | Meaning |
|---|---|
| $7E7400-29 | cards |
| $7E7440-45 | square cleared flags (0 = cleared) |
| $7E7450+$10n | team seats: word wrestler id<<8, 5 deck cards from +2, +$0C state |
| $7E7490 | fifth seat, Otasuke pick |
| $7E74A0 | opponent id<<8 |
| $012C, $069E | board number and the one to return to |
| $0534 | current script |
| $059A | match slot |
| $066A | Scenario Select cursor |
| $0820 | tag setup for board matches, $16-$1A |
| $06F0 | match set: 5 team, 3 gauntlet, 1 tag |
| $06F2, $06F4, $06F6, $06F8, $06FA, $06FC, $06FE, $0702 | wins, losses, wins needed, losses allowed, running flag, list, step, matches left |
| $0612 | Otasuke list |
| $0824 | set by the all-cards code: R skips scripts |
| $0720 | password screen mode |

No SRAM: passwords are the only save. *docs/TECHNICAL.md*

## 8. Hidden and unused

**Button codes at the title** (GAME START / PASSWORD or SCENARIO / BATTLE; any wrong press restarts the code):
- **All cards**: Up Up Up Down Down Left Right Right Up Down Right Left Left. Sets all $7400-$743F to 0 (all cards) and $0824, then **R skips any story script** ($C0:DA77). Sound $1B. Table $C0:71D4. *seen headless t9 for the cards; the R skip is from the code*
- **Sound test**: Up L R Down L R Left L R Right R L. Table $C0:7184. "The Fight Da Pon! Music Driver Ver1.01B". Up/Down music $00-$19, A play, B fade, Start leaves. Song names $C6:F3B7. *seen headless t8*
Note the all-cards code also sets $7430-$743F to 0, which is harmless.

**Debug menu**: hold X + press Select was the entry; the shipped game disabled it with one byte at $C0:8A22. Rows, handlers and the patch: [HIDDEN_CONTENT.md](HIDDEN_CONTENT.md#debug-menu). **Soft reset**: hold Start, press Select.

**Unused data** *data*:
- Script 13: same pointer as 12; never run. Board uses 12.
- 32 messages have no pointer at all, listed with neighbours in `story/unused-messages.txt`; all 862 are in `messages.tsv`: 812 used by scripts, 9 by tables, 9 both, 32 unused. Most are small cuts inside scenes: chapter stage names (CF83 "Misawa's camp...", D18B, D3E9, FB66 "Fuchi's place..."), a trimmed Mecha Baba exchange (DDE1-DE0F "Mecha Baba... / What kind of a name is that... / Silence! / And once it copies your moves too, / it will be perfect!" and "Boh." DE25), a line after the first Red Bear scene (FFA7), and interface lines: CD87 "Choose a wrestler to use." and FEB5 "Choose your opponent." Banks C0-C5 were searched whole for the 16-bit address of each: no real pointer.
- Slots: 04 (Grunt 4/5), 0C (Red Bear 1), 13, 1C, 1D (Hyperspace Mask, rows 4B/4A), 1F, 28 and up are not reached.
- Bars and ids: Zebra Mask is wrestler index 30 and is never fought ([HIDDEN_CONTENT.md](HIDDEN_CONTENT.md#zebra-mask)).
- Maps 0, 1, 8-11 and 13-15 have no board use (their event pointers repeat others).
- Off-path spaces: map 6 (30,31) card, map 4 (70,16) match. The walker can't reach them.
- Board actions 6, 8-15 and action 13 are in no space.
- Action F/10 in 2A37; rows $4E-$5B of 2A37 run on (they look like another table; no script $4E exists).
- Map 12 reuses map 1's events ($E83C) and map 7's layout page table start.
- Op 49 explosions, ops 54, 55, 57 etc. are battle or rare.

**$C4 byte accounting** ($C4:068F-$CD20): $3897-$948E story scripts, every byte walked. $37FD-$3896 script table. $0000-$018C move script table (198 words; 158 valid, 40 point at data). Scripts for moves and animation data fill the rest; after walking both, unaccounted are only small runs inside animation data: 14CE+10, 14EA+6, 168C+16, 2CDD+76, A0D7+15, A2F7+24, A60B+15, A8C7+33, AB08+6, AB4F+58. $ACA6-$CD1F is a compressed block loaded at boot (C0:D4D6 to $7E2000). No cut scene hides there: the scan for ops $2C/$42 finds nothing in those runs.

## 9. Not established
- Which name appears when a Grunt's bar shows ZAKO; bars vs id mapping (table $C0:73D0).
- Exact look of story-stop spaces (a4): not compared with screenshots. Space colours rest on a few spaces.
- Gauge probabilities above are from one run; the RNG is shared, so they are a guide only.
- No chapter was played through normally in the research runs: matches, the final ones and credits were reached by pokes (see run-b/*.steps). Win paths from slots other than 0 are read from tables, not run. Only a forced win on slot 0 was run. Separately, the owner played every story mode and screen through in the English build on 2026-11-02 and saw no problems (*verified in game*); that test did not record which win paths were taken.

## 10. Boards

Every space: `story/board-*.md`.

### Square 0, map $C
Space counts: card 11, card trouble 7, match 6, story stops 3, goal 1. Forks: none


```
        G.
          c.
           .T
         .M
       .E
     .T          .c.
   .c          .T   M.
 .M          .c       c.
c.         .M           T.
  T.     .c            .c
    c. .E            .M
      T            .E
                 .T
               .c
              M.
                c.
                  S

```

### Square 1, map 7
Space counts: card 27, card trouble 16, match 10, story stops 6, goal 1. Forks: 26 (38,27) CARD: Mongolian Chop (card 25)     -> 27, 45, 56 *


```
     .E.                     .T.
   .T   c.                 .c   M.
 .c       c.             .M       c.
c.          T.         .c           T.
  M.     .    c.     .T            .c
    c. .E c. .T    .E            .T
     .T    .c.   .c            .E
   .c    .T   T.c            .M
 .M       c.               .c
c.         .M            .T
  T.     .c            .c
    c. .E            .M
     .T            .E
   .c            .T
 .M            .c
  T.          M.
    c.          c.
      M.          S
        c.
          T. .G
            c

```

### Square 2, map 3
Space counts: card 37, card trouble 24, match 11, story stops 0, goal 1. Forks: 27 (34,45) CARD: random                       -> 28, 65 *; 37 (46,31) CARD: random                       -> 38, 56 *


```
                 G.

                  .T
      T  T. .M. .T.
       .c  c   c   M
     c            T
    c
  M.               c. .M
   .c                T  c
     .T   M   T   c   T.
       .c. .c. .c. .c.   T.
                         T
      .c.     .c        c
     c   M. .T        T.        c
    T      c        c.        T. .c
     .c           M.        M.
       .c   c   c.           .T    .S
  .c.    .c. .c.            c.
 T   c.               T   c.
T      T. .T        T. .M.
 .c   c  M        c.
   .M. .T   c   c.
         .c. .T.

```

### Square 3, map 5
Space counts: card 24, card trouble 13, match 14, story stops 3, goal 1. Forks: 16 (70,13) MATCH: random slot 2               -> 17, 48 *


```
                         .M.     .c. .E.
               .E.     .c   c. .T   M  .c
     .T.     .T   c. .T      .M      .c
   .c   c. .c       M.     .c      .T
 .M       M          .c  .T       M.
E.                 .T  .c           c.
  c.              c. .T              .M
    M.              M              .c
     .c                          .T
   .T                          .c
 .c                           M.
M.                              c.
  c.     .T.                      S
    T. .M   c.
      c       T. .M.
                c   G

```

### Square 4, map 2
Space counts: card 28, card trouble 18, match 17, story stops 1, goal 1. Forks: 33 (54,37) MATCH: random slot 3               -> 34, 63 *


```
                          .S
                      .M.
              c      T.  c
               .T      c.
            .M   .M      M.
           c.   c.         c.
            .T   .M          T.
          .c       .c          c
         M.          .T   M   M
           T. .M.      .c. .c  .c
             c   c.          .T.
                   T.
                     c. .c.
        .c.            M.  T.
      .M   M.           .T   c.
    .T      .c         T      .M
   c       T.         .      c.
  M          c. .E. .c         T
c.             M   T.         .
 .T                  c.     .c
   .c                  T. .M
     .M                  c
    T.
  G.

```

### Square 5, map 6
Space counts: card 30, card trouble 17, match 20, story stops 0, goal 1. Forks: 12 (54,45) CARD TROUBLE                       -> 13, 34 *; 44 (62,23) CARD: Dropkick (card 10)           -> 45, 59 *
off-path, unreachable: (30,31) CARD: random

```
                         T.M
                       c.   .c
             c       M.       .T
       G   .. .M   c.           .c
        .M.     .T.              c.
       T.                      T.
     T.                      M.
   c. .c                   c.
  .M    .M     c         T. .M
    .M    .c T. .M     M.     .c
     T.     .     .T c.         .T
   c.               .             .c
 M.                                c.
.T                               M.
  .c                           T.
    .M                       c.
      .c         c.M       M.                  S
        .T     T.   .c   c.                  c.
          .c M.       .T.                  c.
            .           .c   c           c.
                          .M. .T       M.
                                .c   c.
                                  .M.

```

### Finale, map 4
Space counts: card 52, card trouble 30, match 29, story stops 0, goal 1. Forks: 1 (64,86) CARD: Kawazu Drop (card 15)        -> 2, 112 *; 2 (62,83) MATCH: random slot 6               -> 3, 111 *; 18 (12,70) CARD TROUBLE                       -> 19, 82 *; 22 (18,61) MATCH: random slot 6               -> 23, 78 *; 35 (56,52) MATCH: random slot 6               -> 36, 60 *; 66 (64,36) CARD TROUBLE                       -> 67, 73 *
off-path, unreachable: (70,16) MATCH: random slot 6

```
                      G.

                      c
                       T
                             .c
              M. .T.   .M. .T  M
             c  c   c.T   c
                       c       .c
            T        M.      .c
           c               .T.
         M.           c. .c   c
                        T      M
         .c                  c.
        T.     .c.
          c. .M   T.         .M
            c      .c      .T
                  M. .c. .c
                    T   M
     .T.               c
    c   M.           M.    .T.
   T      T.             .c   c  T   c
    .M      c. .T. .T. .c      M. .M.
   c. .c      M   c   M               T.
        .M   T                         .c
 .M       .c.                        .M
c.                         .c. .c. .c
 .T.                     .T   M   T
M.  c. .T.         .c. .c
  c   c   M. .M. .T   M
 T          c   c
  .c
    .c   c   M           T
      .T. .T. .c       c. .M
                .T   M. .c.
                  .c.      .c.
                          M   S

```

S start, c card, T card trouble, M match, E story stop, G goal, + fork, . path. *Generated from the data and simulated code; the maps were checked against one screen each (sheet1.png), not in full.*
