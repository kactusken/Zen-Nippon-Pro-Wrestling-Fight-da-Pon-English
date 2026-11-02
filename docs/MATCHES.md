# The match system

Source for the [player's guide](guide/index.html), from the original ROM. Frame counts are at 60 fps. Marks: *code* = from the code; *data* = from the ROM's tables; *seen headless* = watched running in Mesen on the original ROM, which is evidence but not an owner check. Nothing here is *verified in game* unless it says so. Run, log and step names refer to the project's private research folder.

## 1. The short version (for the guide's opening)
- **It is not turn-based.** Both sides act in real time. Six cards sit on a row: five moves and FALL. Move the cursor
  left/right and press A. A used card turns face down and recharges by itself. Whoever presses first starts a move; the move
  plays out and the other side can only try to stop it, by playing cards as guards.
- Every wrestler has the same strength. The table of individual stats in the ROM is never read, through a coding slip
  (section 4). Wrestlers differ only in their deck, their one signature card and the cards they may equip.
- Health is 255 for everyone, never heals, and resets for each match.
- Matches end by **pinfall** or by **submission KO** (a hold on a foe at 0 health). No time limit, count-out or ring-out.
- A reversal costs the old attacker only 0-13 health, but it also makes that wrestler's signature card likelier to light up (section 5).

## 2. Match flow
*code* C0:BBB0 ($3A = 5 main, 6 pin/end), C0:C064 ($3C states). *seen headless* run-a/matches3.log, a2 run.

| $3C | Routine | What happens |
|---|---|---|
| 0-2 | C0E6, C24A, C2F1 | Load, fill structures, entrance; decks copied to the slots |
| 4 | C5A5 | Fade in; zeroes the pin bonuses $0198/$019A |
| 5 | C5F3 | **Neutral**: both circle; cards play as attacks (C9E2) |
| 6 | C659 | Attacker starts; waits for wrestlers to be free |
| 7 | C6BB | Move script runs ($C4 bytecode); cards play as guards (C8F7) |
| 3 | C4BA | Script over: damage applied (C0:CE1D), pose decides down/pin; back to 5 |

Rules, in order:
1. **Input.** Neutral, each frame: player first, then COM. If the player's press starts a move the routine returns early
   so COM's press that frame is never read: *ties go to the player* (*code* C9E2, the PLA at CBE4). There is no first
   turn: at $3C=5 whoever presses first attacks.
2. **A press in neutral** with the card ready (not empty, no cooldown): cooldown starts. Your wrestler must be free
   (actor state $023E = 0); if down or getting up, the card is spent for nothing (*code* CB3C, CA63). Then the
   attack value is computed and $3C=6.
3. **During a move, pin or return** any press of a ready card adds its Guard to your defence (*code* C985, C93x).
   Attacker's presses do the same but gain nothing, as reversal wipes the values. Presses in neutral never guard.
4. **Reversal check** at a fixed point of the move (script op $03): if attack < defence the move is reversed. Equal
   means the attack holds. A plain hit has 1 check (Front Neck Lock 2); a hold checks at every tick.
5. **Reversal** (*code* ED18): attacker and defender swap, all values zero, the attacker's card gets a Fail point,
   the script's fail branch plays, damage is what that branch sets (12 for most, Elbow Drop 13, strikes 0).
6. **Lock-ups** (*code* C7B9, *seen headless* $834E=0B-0F, P16=107, C18=0): in neutral, when the circling radius $023A,X = $28
   and random bits 8-9 of $46 are both 0, a move starts by itself with no card. It can't start while someone is rising
   ($01CE not 0). PPU counter bit 2 picks the attacker; nothing happens if that wrestler isn't free. Table C0:B43E/B450 by $46&15:

   | Script | Chance | Damage |
   |---|---|---|
   | 0B | 4/16 | 13 |
   | 0D, 0C | 3/16 each | 7 |
   | 0F, 0E | 3/16 each | 3 |

   Attack = damage + 104, defence starts at 0, so guards need more than 104 to reverse. Timing from the code: the radius
   cycles over 512 frames and passes $28 about twice, so a lock-up can come every few seconds of idling.
7. **Down.** The end pose decides. Victim's poses 22, 23, 36, 38, 3D: the victim goes down (*code* C502). Attacker's pose 26, 31, 34,
   3A, 45, 7F: automatic pin. Other poses: nobody down. Sweeps give each card's result (section 5).
8. **Getting up** (*code* 57AB): counter $0224,X = (255 - HP)/2, set at damage (C0:CE43). It falls by 1 per 2 frames, then a
   20-frame rise. Recovery ≈ 255 - HP frames + 20. **Pressing A does not speed it up.** The code at CBE6 would take 48 off per
   press, but the check at CB3C returns first while the wrestler is down, so it's not reached (no log shows it: 0 of 425 lines).
9. **Attacking a downed foe**: the move starts by hauling the foe up (script $0128), then runs in full. Attack and guards
   work as usual.
10. **FALL** (slot 6): on a foe who isn't down it does nothing and is spent (*seen headless*: 38 frames). On a downed foe, cover
    and pin.
11. **Pin** ($3A=6, CFCF; *seen headless* pin_passive.log, pin_active.log). Three counts at about frames 60, 141 and 223.
    - Attack stays what the move's value was, plus the pin bonus $0198 (you) / $019A (COM).
    - Defence: starts at 104 plus guards. Every 16 frames of the game counter (~19 real frames, about 11 ticks in the pin) both
      defences gain HP/16 (*code* CF8C). Cards still guard.
    - If attack + bonus < defence at any frame before the third count: kick-out, the pin bonus grows by **24** and stays
      for the match, the pinned man's getting-up time is zeroed, and neutral resumes.
    - Otherwise three count, match over.
    - Rule of thumb: no guards, kick-out if 104 + 11 × (HP/16, whole) > attack + bonus.
    - Measured, COM's cards off, Power Slam pin: HP 231 / 196 / 166 kicked out at frame 86 / 130 / 170 (attack 172 / 180 / 188); HP 136 and
      below stayed down (attack 195+). With COM's cards ready it kicked out at every health, 0 included (guards every 16
      frames). Pin when its cards are on cooldown.
12. **Submission KO.** Holds tick: damage, then both defences +2 (op $55), then op $54: if the victim's *displayed* health is 0,
    a 1 in 8 roll (`$46&7==0`) ends the match at once, with no count (*seen headless* tests2.log: ko29, ko31, $3A=6 $3C=3 mid-hold).
13. **Empty deck** ($05BE = 0, no moves): instant loss at the bell (*code* C5F3, *seen headless* tests2.log `empty`).
    Only the player is checked. The FALL slot doesn't count.
14. Pause: Start ($BB52) freezes the match; not relevant to rules.

Not found anywhere: time limit, count-out, ring-out, draw, rounds. A match can't end at 0 health without a pin or a KO roll
(*code*: nothing but CFCF/F5DF/C5F3 leaves $3A=5). A wrestler at 0 health just keeps going with long get-ups.

### Modes
| | Battle 1P vs COM ($059A=$21) | Battle 1P vs 2P ($01C6=$FFFF) | Story ($059A=00-$27) | Demo ($059A=$20) |
|---|---|---|---|---|
| Wrestlers | Baba..Izumida (16) each; opponent can't be the same man (C0:77CE) | same | set by chapter; you pick from your team in team fights | table C0:6C8F |
| Your deck | fixed default deck, no edit | fixed | **Deck Edit** before each fight (5 slots then EXIT) | default |
| COM | cooldown 64 frames shorter | no COM; both normal cooldowns | COM shorter cooldown | COM side AI; other side see note |
| After | win tally $05BA/$05BC, first to 10 resets both, then again (C0:76FD); no best-of | same; result screen always the "win" layout ($018A cleared, D07C) | grunt fights: win = new card, loss = card flip; then the board. Others by table C0:2AD2 | ends after timer $01DA=$0708 frames or Start/A |

Note: in the demo C0:BFA6 feeds the player side random input from table C0:BF96.

Team fights in story (*code* 4BF9-4D53, details are the story document's): `$06F0`=5: five of yours against five Red Bears in order. A win moves on to the next Bear and your winner stays available; a loss marks that wrestler out (C0:4C87, +$0C = $8000) and the same Bear comes back. Five wins clear it; a fifth loss runs script 1E and restarts it (team: Kimura, Fuchi, Eigen, Izumida plus the partner, record $7E:7490). `$06F0`=3: three matches in a row; any loss runs the lose script and starts the set again (C0:D35E, D302).

**Partner (Otasuke).** Partner Select picks a wrestler for your team (*code* 4B78: stored as team record 5); that wrestler then fights their own bouts. *There is no in-match assist*: no match
routine reads the partner, and no move script $0B-$39/$6F uses the actor-swap ops ($5D, $57, $56, *data* battle_scripts.txt).

## 3. Health
- 255 for each wrestler, in every mode, from every source (*code* C0:078F writes $FF; *seen headless* in all logs incl. story).
- Structures: player $7E:7000, COM $7E:71C0; health at +$10: $7E:7010, $7E:71D0.
- Only damage changes it: *code*, the only writers are CE36/CE3F/CE66/CE6F. No regeneration, no refill between pin attempts.
  Floor 0.
- Fresh each match: the block $7000-$73FF is cleared in C0E6. Team fights too.
- Bar: 16 cells of 8 steps = 128 steps of health/2, so a cell is 16 health (*code* CD4C-CDCC). $7E:8370/8372 start at 256 and chase
  health at 3 per frame (6 per even frame). The damage shows late (*seen headless*).
- Portrait face: by health band, table C0:CEC7: 192+ / 128-191 / 64-127 / below 64 (*code*; cosmetic).

## 4. Wrestler stats: the data is dead
*code* C398: stats load with `LDA $01D2 ... AND #$00FF`, the LOW byte of the wrestler word, but wrestler numbers live in the HIGH byte
($01D2 = n<<8; all writers: 7788, 6CD4, 1DA5, C0FD, tables 733A/736A). So row 0 is always used.
**Every wrestler in every mode: Attack 109, Guard 104.** (+$04=$6D, +$06=$1C, +$08=$68). *seen headless*: peeks at $7E:7000/$71C0 with player Baba and
another poked wrestler; COM Tsuruta, Hansen, Akiyama, Eigen, Hyperspace Mask, Grunt, Baba; story chapter 1 (Grunt 1). Attack values of all 16 playable wrestlers fit base 109: 31 of 31, run-a/sweep_var.log. +$06 has no reader either.

For the record, the ignored table at C0:05CD (8 bytes, n*8; bytes 1-5 stored at +$04, +$06, +$08, +$0A, +$0C; byte 0, 6, 7 are 0). Row 0 is
Baba's: 109/28/104. Column names are inferred (first compared as attack, third as guard):

| # | Wrestler | Attack | ? | Guard | ? | ? |
|--:|---|--:|--:|--:|--:|--:|
| 0 | Baba | 109 | 28 | 104 | 0 | 0 |
| 1 | Tsuruta | 116 | 34 | 120 | 6 | 2 |
| 2 | Hansen | 113 | 34 | 128 | 3 | 0 |
| 3 | Misawa | 110 | 30 | 128 | 4 | 0 |
| 4 | Kawada | 110 | 28 | 128 | 9 | 0 |
| 5 | Taue | 108 | 30 | 120 | 3 | 6 |
| 6 | Williams | 104 | 30 | 122 | 5 | 0 |
| 7 | Gordy | 104 | 30 | 120 | 9 | 3 |
| 8 | Kobashi | 108 | 28 | 118 | 10 | 0 |
| 9 | Fuchi | 112 | 25 | 112 | 2 | 0 |
| 10 | Patriot | 112 | 25 | 104 | 0 | 0 |
| 11 | Kikuchi | 108 | 26 | 112 | 7 | 0 |
| 12 | Kimura | 112 | 25 | 80 | 0 | 0 |
| 13 | Akiyama | 108 | 28 | 64 | 7 | 0 |
| 14 | Eigen | 108 | 25 | 64 | 0 | 0 |
| 15 | Izumida | 112 | 26 | 64 | 0 | 0 |
| 16 | Grunt 1 | 80 | 28 | 48 | 0 | 0 |
| 17 | Grunt 2 | 88 | 29 | 56 | 0 | 0 |
| 18 | Grunt 3 | 88 | 31 | 64 | 0 | 0 |
| 19 | Grunt 4 | 96 | 33 | 64 | 0 | 0 |
| 20 | Grunt 5 | 96 | 35 | 80 | 0 | 0 |
| 21 | Hyperspace Mask | 96 | 42 | 96 | 0 | 0 |
| 22 | USA Mask | 96 | 50 | 80 | 0 | 0 |
| 23 | Tutan Mask | 80 | 46 | 128 | 0 | 0 |
| 24 | Red Bear 1 | 112 | 50 | 112 | 0 | 0 |
| 25 | Red Bear 2 | 104 | 48 | 104 | 0 | 0 |
| 26 | Red Bear 3 | 96 | 46 | 96 | 0 | 0 |
| 27 | Red Bear 4 | 88 | 44 | 88 | 0 | 0 |
| 28 | Red Bear 5 | 80 | 42 | 80 | 0 | 0 |
| 29 | Mecha Baba | 128 | 68 | 128 | 0 | 0 |

## 5. Cards
Table C0:0454, 8 bytes, 43 entries (*data* battle_cards.csv). Unpacked at C0:06E9 to a $40-byte slot: player $7E:7040+$40*n, COM $7E:7200+$40*n, n=0-5.

| Byte | Slot field | Meaning |
|---|---|---|
| 0 | +$02 = low 3 bits | always 3; stored, unused |
| 0 | +$04 = bits 3-7 | cooldown in ticks of 4 frames (COM in 1P: minus 16) |
| 1 | +$06 = high nybble × 4 | Power |
| 1 | +$08 = low nybble | Random range n: adds 0..n-1 |
| 2 | +$0A = high nybble × 4 | Guard |
| 2 | +$0C = low nybble | stored, never read |
| 3 | +$0E | always $25, never read |
| 4 | | always $FF, not stored |
| 5 | +$28 | Damage ÷ 4 |
| 6 | +$2A | move script ($10 + id; FALL $6F) |
| 7 | | 0, not read |

Other slot fields: +$00 id (FF = empty), +$12 cooldown (low) plus a 3-tick card flip (high), +$14 flash, +$20 lit flag ($1C00), +$22 Fails, +$24 byte from C0:5D80.

### Formula
*code* CA85-CAD5 (COM), CB5E-CBAE (player). *seen headless* 69/69 attacks, 21 cards, both sides: check_formula.py on matches3.log; every value in range and every
damage exact.

```
Attack  = 109 + Power + rand(Random) + (Lit ? 80 : 0) + (255 - victim's health) / 4     (integer divide)
Defence = 104 + sum of Guard of the cards the defender plays during this move
          + 2 per earlier hold tick
Reversed if Attack < Defence.
Damage  = card Damage (field × 4), applied when the script ends, or at each tick of a hold.
Reversal damage = the fail branch's fixed value, to the old attacker.
```
- rand(n) = (byte × n) >> 8 with a byte from the 8-byte ring $46-$4D, stepped by $4E: even, 0..n-1 (*code* CD2B, 5894). The main loop spins $46-$4D between
  frames, so results depend on free CPU time; not plannable.
- Attack is fixed when the card is pressed; the health bonus uses health at that moment. The victim weakens: at 0 health +63.
- The other way: `Defence` is reset to 104 every neutral frame; guards never carry between moves.
- Random elements in a match: Random of the card, AI, lock-ups (start, attacker, kind), lit rolls, KO roll. Damage has no random part. op $14 ("defence + rand(stat)") is in no move
  script (*data*).

Consequences for the guide: Power 60 attack at full health is 169+. With no guards every attack lands (minimum 109+28=137 > 104). To stop a Power 56, Random 14 card at full health you need Guard > 61-74, i.e.
2 or 3 cards in the 1-2 seconds before the check. Guards are spent cards, so a guard is a move you can't use. Every card has a Guard, and they run opposite to Power: high-Guard cards (Tiger Suplex 52) are strong defensively.

### All cards
Cooldown you = ticks × 4 (*seen headless* tests1.log: Dropkick 189, Brainbuster 317, Microphone 765, FALL 509 frames: 3 less than the table, as the first tick comes early). It runs during moves and pins too. "Reversed" *data*
fail branch. "Kind" and frames *seen headless* sweep_normal.log (Baba's animation; other wrestlers vary).

| id | Label | Move | Attack (Power) | Random | Guard | Damage | Cooldown you / COM (frames) | Reversed: damage to the user | Kind | Frames (Baba) |
|--:|---|---|--:|--:|--:|--:|--:|--:|---|--:|
| 0 | BBUSTER | Brainbuster | 60 | 0-12 | 8 | 16 | 320 / 256 | 12 | hit | 172 |
| 1 | PDRIVER | Piledriver | 52 | 0-11 | 8 | 20 | 320 / 256 | 12 | hit | 222 |
| 2 | BDROP | Backdrop | 56 | 0-9 | 12 | 24 | 320 / 256 | 12 | hit | 184 |
| 3 | LARIAT | Lariat | 44 | 0-9 | 24 | 36 | 384 / 320 | 0 | hit | 218 |
| 4 | ELBOW | Elbow | 48 | 0-11 | 24 | 24 | 288 / 224 | 0 | hit | 102 |
| 5 | PSLAM | Power Slam | 56 | 0-12 | 16 | 24 | 352 / 288 | 0 | hit, then pin | 226 |
| 6 | COBRA T | Cobra Twist | 44 | 0-7 | 16 | 16 per tick | 416 / 352 | 12 | hold, repeats | to HP 0 |
| 7 | GERMAN | German Suplex | 48 | 0-7 | 16 | 32 | 448 / 384 | 12 | hit, then pin | 200 |
| 8 | DDT | DDT | 48 | 0-4 | 28 | 36 | 416 / 352 | 12 | hit | 144 |
| 9 | PBOMB | Powerbomb | 40 | 0-3 | 32 | 36 | 480 / 416 | 12 | hit, then pin | 178 |
| 10 | DROPKICK | Dropkick | 56 | 0-13 | 8 | 16 | 192 / 128 | 0 | hit | 108 |
| 11 | 16 MON | Sixteen-Mon Kick | 52 | 0-9 | 32 | 48 | 384 / 320 | 0 | hit | 210 |
| 12 | NECK BD | Neckbreaker Drop | 44 | 0-6 | 36 | 44 | 416 / 352 | 12 | hit | 160 |
| 13 | COCONUT | Coconut Crush | 36 | 0-7 | 32 | 40 | 416 / 352 | 12 | hit | 152 |
| 14 | BCHOP | Brain Chop | 44 | 0-7 | 24 | 36 | 288 / 224 | 0 | hit | 110 |
| 15 | KAWAZU | Kawazu Drop | 48 | 0-5 | 40 | 52 | 640 / 576 | 12 | hit | 136 |
| 16 | KSINK | Kitchen Sink | 52 | 0-6 | 32 | 48 | 576 / 512 | 0 | hit | 196 |
| 17 | JKNEE | Jumping Knee | 48 | 0-9 | 32 | 52 | 512 / 448 | 0 | hit | 220 |
| 18 | THROAT | Throat Thrust | 40 | 0-11 | 32 | 48 | 608 / 544 | 12 | hit | 160 |
| 19 | SPIT | Spit | 52 | 0-11 | 28 | 24 | 512 / 448 | 0 | hit | 252 |
| 20 | MIC | Microphone | 56 | 0-7 | 32 | 24 | 768 / 704 | 12 | hit | 216 |
| 21 | HBUTT | Headbutt | 60 | 0-13 | 16 | 24 | 448 / 384 | 0 | hit | 126 |
| 22 | CCHOP | Chest Chop | 56 | 0-7 | 24 | 28 | 416 / 352 | 0 | hit | 122 |
| 23 | BULLDOG | Bulldog Headlock | 40 | 0-7 | 16 | 32 | 640 / 576 | 12 | hit | 170 |
| 24 | IWORM | Inchworm | 52 | 0-7 | 12 | 16 | 384 / 320 | 0 | hit | 286 |
| 25 | MCHOP | Mongolian Chop | 48 | 0-7 | 12 | 28 | 416 / 352 | 0 | hit | 118 |
| 26 | TDRIVER | Tiger Driver | 56 | 0-9 | 40 | 48 | 640 / 576 | 12 | hit, then pin | 174 |
| 27 | TSUPLEX | Tiger Suplex | 52 | 0-8 | 52 | 52 | 896 / 832 | 12 | hit, then pin | 200 |
| 28 | FLARIAT | Flying Lariat | 56 | 0-10 | 32 | 44 | 384 / 320 | 0 | hit | 248 |
| 29 | FLOCK | Front Neck Lock | 28 | 0-7 | 40 | 24 per tick | 384 / 320 | 12 | hold, repeats | to HP 0 |
| 30 | SOCCER | Soccer Kick | 36 | 0-12 | 16 | 24 | 320 / 256 | 12 | hit | 300 |
| 31 | SPLUM | Stretch Plum | 36 | 0-9 | 20 | 24 per tick | 416 / 352 | 12 | hold, repeats | to HP 0 |
| 32 | SPIN K | Spin Kick | 48 | 0-11 | 40 | 44 | 448 / 384 | 0 | hit | 192 |
| 33 | ZEROSEN | Zero Fighter | 44 | 0-10 | 32 | 36 | 448 / 384 | 0 | hit | 138 |
| 34 | DHEAD | Diving Headbutt | 48 | 0-7 | 24 | 48 | 480 / 416 | 0 | hit | 364 |
| 35 | JSHLDR | Jumping Shoulder | 44 | 0-13 | 28 | 28 | 160 / 96 | 0 | hit | 218 |
| 36 | MSAULT | Moonsault | 52 | 0-11 | 24 | 60 | 768 / 704 | 0 | hit, then pin | 434 |
| 37 | ROLLING | Rolling Move | 32 | 0-7 | 16 | 32 | 704 / 640 | 12 | hit | 320 |
| 38 | EDROP | Elbow Drop | 48 | 0-8 | 40 | 52 | 544 / 480 | 13 | hit | 238 |
| 39 | OKROLL | Oklahoma Roll | 52 | 0-7 | 32 | 48 | 768 / 704 | 12 | hit, then pin | 300 |
| 40 | NELSON | Full Nelson | 44 | 0-7 | 32 | 40 | 512 / 448 | 12 | hit | 142 |
| 41 | MISSILE | Missile Kick | 52 | 0-10 | 32 | 60 | 608 / 544 | 0 | hit | 372 |
| 42 | FALL | Fall (pin) | 48 | 0-7 | 24 | 0 | 512 / 448 | - | pin (needs a downed foe) | 38 |

- Hit damage measured for every card, *seen headless* sweep_normal.log: all match field × 4.
- Moves of holds: Cobra Twist, Front Neck Lock, Stretch Plum. Each tick about 100 frames. Attack is fixed; both defences +2 per tick; guards add up. Check every tick; escaped = 12 damage to the holder. Rolling Move is a hold only for Red Bear (sprite 18, script at C4:015D, has a KO roll).
- Spit and Microphone are ordinary cards: same fields, no effect of their own. No code tests a card id except FALL's script. Status effects don't exist.

### Wrestler-specific moves
Script op $45 branches by sprite (*data*; *seen headless* sweep_var.log):
| Card | Wrestler | Difference |
|---|---|---|
| Elbow | Misawa | Two strikes: 24 then 12 (36 total) |
| Powerbomb | Hansen | No pin: 36 damage, foe down |
| Powerbomb | Kawada, Gordy | Own animation; with pin; lit +31 |
| Lariat | Misawa, Kikuchi | own animation, 36 |
| Lariat | Hansen | own; lit +31 |
| Lariat | Gordy | own, shorter |
| German Suplex | Akiyama | own; lit +31 |
| Backdrop | Fuchi | own; lit +31 |
| Rolling Move | Red Bear | hold |

### Lit (glowing) cards: signature moves
*code* C73A, *seen headless* tests1.log lit5/lit0/nosig.
- Each playable wrestler has exactly one signature card (+$24 bit 1, table C0:5D80; Mecha Baba also has Neckbreaker Drop).
- When a signature card's cooldown ends the game rolls: chance by its Fails (reversals since last lit), table C0:C703:
  | Fails | 0 | 1 | 2 | 3 | 4 | 5+ |
  |---|---|---|---|---|---|---|
  | Chance | 1/256 | 1/16 | 1/8 | 1/4 | 1/2 | always |
- Lit: card flashes ($1C00), Fails reset to 0, stays until used.
- Lit attack: +80 Attack, and the move's lit version does an extra **31** damage (a second hit) (*seen headless*: every signature in sweep_var.log: all 16 wrestlers).
- Only reversals add Fails (ED79; op $4D is in no move script). So a reversed signature card gets more dangerous: 5 reversals guarantee it. Fails are per card slot, per match.

## 6. Wrestlers and cards
Name index = $01D3 (player), $01D5 (COM). Sprite = C0:73D0[index] (bit 7 is just part of the id; row = low 7 bits).
Deck C0:6230 (5 bytes per index; FF empty). The player uses it in Battle; COM always. FALL is always slot 6. Hand size: always these 6 cards, no draw, no shuffling, no running out: cards cycle by cooldown.

| # | Wrestler | Sprite | Battle / COM deck (slots 1-5) | Signature card | Cards allowed of 42 |
|--:|---|--|---|---|--:|
| 0 | Baba | 0F | Brain Chop, Cobra Twist, DDT, Sixteen-Mon Kick, Neckbreaker Drop | Neckbreaker Drop | 16 |
| 1 | Tsuruta | 86 | Dropkick, Cobra Twist, Backdrop, Kitchen Sink, Jumping Knee | Jumping Knee | 13 |
| 2 | Hansen | 87 | Elbow, DDT, Powerbomb, Elbow Drop, Lariat | Lariat | 13 |
| 3 | Misawa | 85 | Dropkick, Elbow, Front Neck Lock, Tiger Suplex, Tiger Driver | Tiger Driver | 16 |
| 4 | Kawada | 00 | Elbow, Spin Kick, Lariat, Stretch Plum, Powerbomb | Powerbomb | 15 |
| 5 | Taue | 08 | Brainbuster, Dropkick, Cobra Twist, Lariat, Throat Thrust | Throat Thrust | 12 |
| 6 | Williams | 0A | Brainbuster, Dropkick, DDT, Power Slam, Oklahoma Roll | Oklahoma Roll | 12 |
| 7 | Gordy | 09 | Piledriver, DDT, Power Slam, Lariat, Powerbomb | Powerbomb | 11 |
| 8 | Kobashi | 04 | Dropkick, Brainbuster, DDT, Rolling Move, Moonsault | Moonsault | 14 |
| 9 | Fuchi | 0C | Brainbuster, Dropkick, Cobra Twist, German Suplex, Backdrop | Backdrop | 11 |
| 10 | Patriot | 0D | Dropkick, Piledriver, Power Slam, Full Nelson, Missile Kick | Missile Kick | 13 |
| 11 | Kikuchi | 8E | Dropkick, Elbow, Zero Fighter, German Suplex, Diving Headbutt | Zero Fighter | 13 |
| 12 | Kimura | 0B | Elbow, Piledriver, Microphone, Chest Chop, Bulldog Headlock | Bulldog Headlock | 15 |
| 13 | Akiyama | 01 | Dropkick, Brainbuster, Backdrop, German Suplex, Tiger Suplex | German Suplex | 12 |
| 14 | Eigen | 82 | Elbow, Piledriver, Spit, Backdrop, Lariat | Spit | 12 |
| 15 | Izumida | 03 | Inchworm, Dropkick, Mongolian Chop, Piledriver, Backdrop | Mongolian Chop | 13 |
| 16 | Grunt 1 | 16 | Dropkick, Brainbuster, Piledriver, (empty), (empty) | - | 11 |
| 17 | Grunt 2 | 16 | Dropkick, Brainbuster, Piledriver, Backdrop, (empty) | - | 11 |
| 18 | Grunt 3 | 16 | Dropkick, Brainbuster, Piledriver, Backdrop, Lariat | - | 11 |
| 19 | Grunt 4 | 16 | Elbow, Piledriver, Backdrop, Cobra Twist, DDT | - | 11 |
| 20 | Grunt 5 | 16 | Elbow, Dropkick, Piledriver, Cobra Twist, Powerbomb | - | 11 |
| 21 | Hyperspace Mask | 14 | Dropkick, Elbow, Piledriver, DDT, German Suplex | - | 11 |
| 22 | USA Mask | 11 | Elbow, Piledriver, Cobra Twist, Lariat, Powerbomb | - | 11 |
| 23 | Tutan Mask | 15 | Dropkick, Backdrop, Elbow, Cobra Twist, Lariat | - | 11 |
| 24 | Red Bear 1 | 18 | Dropkick, Brainbuster, Backdrop, (empty), (empty) | - | 11 |
| 25 | Red Bear 2 | 18 | Dropkick, Brainbuster, Backdrop, Power Slam, (empty) | - | 11 |
| 26 | Red Bear 3 | 18 | Elbow, Piledriver, Backdrop, Power Slam, Lariat | - | 11 |
| 27 | Red Bear 4 | 18 | Elbow, Piledriver, Cobra Twist, German Suplex, DDT | - | 11 |
| 28 | Red Bear 5 | 18 | Elbow, Piledriver, Cobra Twist, German Suplex, Rolling Move | - | 11 |
| 29 | Mecha Baba | 10 | Brain Chop, Neckbreaker Drop, Sixteen-Mon Kick, Coconut Crush, Kawazu Drop | Neckbreaker Drop | 16 |

Battle selectable: 0-15. 16-29 story only. Index 30 is Zebra Mask, complete but for a name and a deck ([HIDDEN_CONTENT.md](HIDDEN_CONTENT.md#zebra-mask)); 31 has no name; 32 (sprite $13) unused.

Bosses and grunts: sprite row $16 for all Grunts, $18 Red Bears. Red Bear 5's deck has Rolling Move, which row $18 forbids; decks aren't checked (*data*). Colours of grunts 1-4 come from C0:16BF.

### Who can use what
Table C0:5D80, 48 bytes per sprite row (*data* battle_wrestler_cards.csv). 0 = can use, bit 7 ($80) = can't equip, bit 1 = signature. Bit 0 (values 1, 3): read by nothing.
Matrix below by card id: `.` usable, `o` usable with the unused bit 0, `S` signature, `-` forbidden, `D` in default deck.

```
card                 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41
Baba                 .  .  .  .  .  . oD  . .D  .  - .D SD  . .D  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  .  -  -  -  -
Tsuruta              .  . oD  .  .  . oD  .  .  . .D  -  -  -  -  - .D SD  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Hansen               .  .  . SD .D  .  .  . .D oD  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  .  -  -  -  -  -  -  - .D  -  -  -
Misawa               .  .  .  . oD  .  .  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - SD .D  . .D  -  -  .  -  -  -  -  -  -  -  -  -
Kawada               .  .  . .D .D  .  .  .  . SD  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  .  . .D .D  -  -  -  -  -  -  -  -  -
Taue                .D  .  . oD  .  . .D  .  .  . .D  -  -  -  -  -  -  - SD  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Williams            .D  .  .  .  . oD  .  . .D  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - SD  -  -
Gordy                . .D  . oD  . .D  .  . .D SD  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Kobashi             .D  .  .  .  .  .  .  . .D  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  . SD .D  -  -  -  -
Fuchi               .D  . SD  .  .  . .D .D  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Patriot              . .D  .  .  . .D  .  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - .D SD
Kikuchi              .  .  .  . .D  .  . oD  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - SD .D  -  -  -  -  -  -  -
Kimura               . .D  .  . .D  .  .  .  .  .  .  -  -  -  -  -  -  -  -  - .D  . .D SD  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Akiyama             .D  . .D  .  .  .  . SD  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Eigen                . .D .D .D .D  .  .  .  .  .  .  -  -  -  -  -  -  -  - SD  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Izumida              . .D .D  .  .  .  .  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  - .D SD  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Grunt 1             .D .D  .  .  .  .  .  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Grunt 2             .D .D .D  .  .  .  .  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Grunt 3             .D .D .D .D  .  .  .  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Grunt 4              . .D .D  . .D  . .D  . .D  .  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Grunt 5              . .D  .  . .D  . .D  .  . .D .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Hyperspace Mask      . .D  .  . .D  .  . .D .D  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
USA Mask             . .D  . .D .D  . .D  .  . .D  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Tutan Mask           .  . .D .D .D  . .D  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Red Bear 1          .D  . .D  .  .  .  .  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Red Bear 2          .D  . .D  .  . .D  .  .  .  . .D  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Red Bear 3           . .D .D .D .D .D  .  .  .  .  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Red Bear 4           . .D  .  . .D  . .D .D .D  .  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
Red Bear 5           . .D  .  . .D  . .D .D  .  .  .  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  - -D  -  -  -  -
Mecha Baba           .  .  .  .  .  .  .  .  .  .  . oD SD oD oD oD  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -
```

| Wrestler | Can use beyond the common 0-9 | Common cards refused |
|---|---|---|
| Baba | Sixteen-Mon Kick, Neckbreaker Drop, Coconut Crush, Brain Chop, Kawazu Drop, Rolling Move | - |
| Tsuruta | Dropkick, Kitchen Sink, Jumping Knee | - |
| Hansen | Dropkick, Soccer Kick, Elbow Drop | - |
| Misawa | Dropkick, Tiger Driver, Tiger Suplex, Flying Lariat, Front Neck Lock, Spin Kick | - |
| Kawada | Dropkick, Front Neck Lock, Soccer Kick, Stretch Plum, Spin Kick | - |
| Taue | Dropkick, Throat Thrust | - |
| Williams | Dropkick, Oklahoma Roll | - |
| Gordy | Dropkick | - |
| Kobashi | Dropkick, Jumping Shoulder, Moonsault, Rolling Move | - |
| Fuchi | Dropkick | - |
| Patriot | Dropkick, Full Nelson, Missile Kick | - |
| Kikuchi | Dropkick, Zero Fighter, Diving Headbutt | - |
| Kimura | Dropkick, Microphone, Headbutt, Chest Chop, Bulldog Headlock | - |
| Akiyama | Dropkick, Tiger Suplex | - |
| Eigen | Dropkick, Spit | - |
| Izumida | Dropkick, Inchworm, Mongolian Chop | - |

### Deck Edit (story)
*code* 35xx-3C47; *seen headless* st1 run, st1.png.
- Before each fight: 5 slots at top, EXIT, then a 6×7 grid of all 42 cards. A picks a slot, A a card, B empties a slot, EXIT starts (C0:377E).
- $7E:7400 + card id: $FF not owned, 0 owned, 1 in a deck. A card can be in one deck only (38E3 refuses non-zero). Forbidden cards refused with a buzzer (38DE).
- Each team member has a 16-byte record at $7E:7450+$10n: wrestler word, 5 card words, +$0C "out" flag. 5 members. Cards return to the pool when a member drops out (3C1A).
- New game: cards 0-7 owned and **no card equipped** (*seen headless* 2026-11-02 on the English build, at the chapter 1 board: 7400 = `00 00 00 00 00 00 00 00 FF...`, seat 7450 = `00 00 FF FF...`; the Deck Edit screen shows five empty slots). An earlier note here said Brainbuster starts equipped: that was the research script's own A press in Deck Edit. An empty deck loses at once.
- Stretch Plum (31) is taken away at the third scenario's start (C0:BD18), given back by script op $5C.

### Gaining and losing cards
*code* 2DDA, 305F, 338F, 42FA. Messages at C4:CD3E-CD76.
- Story, chapter fights ($059A<7): **win** a card: reward $05A0 if a script set one; else a random card. With 16 or fewer owned the roll repeats until it's new; with 17+ any of 42, so "You already have this card" is possible. Stretch Plum is skipped in the third scenario ($066A=2). When the flags $7E:7440-45 are all 0 (all six squares cleared, see STORY.md): rand(16), ids 0-15.
- **Lose**: "Time to flip a card!": a pointer spins over the grid for rand(42)+21 steps. If it stops on a card you own you lose it (removed from every deck), else "Your move card is safe!". Then back to the board.
- Battle mode: no cards change.

## 7. COM AI
*code* C0:177F-186D. Same code for every opponent and chapter. 1P only ($01C6=0). Input goes through the same routine as the player, so its rules are the same.

**Attack, neutral.** Every 8 frames:
1. Level = 3 if your wrestler's actor state is 4 (down); else `($701C >> 4) & 3`. $701C adds up the Power of every attack **you** make this match, so the level wanders with what you play: (e.g. one Power 56 card = 3).
2. Target list C0:171F + level*16; if the cursor isn't on the target, move one step.
3. If on target: pick a new target from the list (index $49&15) and press A with chance w/128 (*`$46&127 < w`*).
   w table C0:175F, words, index = level + 2×((HP>>3)&3) where HP = your health:
   | (HP>>3)&3 | L0 | L1 | L2 | L3 |
   |---|---|---|---|---|
   | 0 | 80 | 96 | 112 | 128 |
   | 1 | 112 | 128 | 32 | 64 |
   | 2 | 32 | 64 | 96 | 128 |
   | 3 | 96 | 128 | 16 | 32 |

   (HP>>3)&3 cycles every 32 health, surely not what was meant, likely `(HP>>6)`. So the rate jumps as health falls. COM presses as much as 1 in 1 at each 8 frames when the card is ready.
4. FALL (slot 6) is only pressed at level 3.

Lists (slots 0-5; bottom = 6th):
| Level | 16 picks |
|---|---|
| 0 | 1 2 2 1 2 1 1 2 1 3 2 1 3 2 3 2 |
| 1 | 3 5 2 1 5 3 4 4 5 4 5 4 3 5 4 5 |
| 2 | 5 4 3 5 5 3 4 2 5 5 3 4 5 1 4 5 |
| 3 | 6 5 6 6 3 6 6 6 4 5 3 6 6 6 5 4 |

(shown as slots 1-6.) Level 3: 9/16 FALL: COM really does go for the pin when you're down.

**Defence.** While you attack or pin ($019C=0, not neutral): a fixed 16-frame pattern: cursor right, 2 frames later A (table C0:16DF). So one card per 16 frames in order round the row; not-ready ones do nothing. No look at the move, no choice. A on the FALL slot is dropped unless the last level was 3.
When COM attacks, it presses nothing.

**Difficulty:** nothing by chapter or opponent, other than (a) the deck, and (b) the 16-tick (64-frame) cooldown cut in all 1P play. No stat advantage, as stats are ignored. Mecha Baba is hard for the deck only (hand: Brain Chop, Neckbreaker Drop, Sixteen-Mon, Coconut Crush, Kawazu Drop).

**Exploit notes** (*code* reasoning, not played): COM's guards come from a cooldown pool. Holds drain it. Attack right after COM spends cards; low COM level by keeping $701C low: `Power` sum modulo 64 below 16 gives level 0, weak cards only; sums 48-63 turn on FALL.

## 8. Other hidden facts
- Attack bonus (255 - health)/4 and get-up time make low health snowball. There is no comeback mechanic, no rage, no crowd, no finisher meter.
- `$0150` (attack - defence) is computed and unused by the match.
- op $14 (random defence) and op $4D (add a Fail) exist, unused by moves.
- CBE6 (mash to rise) is effectively dead; the sound of a wasted press is still played.
- Card id 42 is FALL; table entry 43 ($05AC) is not a card (it runs into the stats table).

## 9. RAM map for the match
| Address | Meaning |
|---|---|
| $38/$3A/$3C | mode / match phase (5 main, 6 pin) / state |
| $34 | frame counter |
| $46-$4D, $4E | random bytes, ring index |
| $0180, $0184 | cursors, player/COM |
| $018A/$018C | attacker/defender actor ($0000 player, $0040 COM: offsets into $0200) |
| $0190/$0192 | player/COM actor |
| $019C | 0 player attacks, $FFFF COM |
| $0198/$019A | pin bonus player/COM |
| $01C6 | $FFFF = 2P |
| $01D2/$01D4 | player/COM wrestler (word, index in high byte) |
| $01D6/$01D8 | sprite words |
| $01DE | selected wrestler, copied to $01D2 at match start |
| $05B8 | last card lit |
| $05BA/$05BC | Battle win tally |
| $05BE | player's card count |
| $05F0/$05F2 | last used slot offset player/COM |
| $059A | match id (story table C0:2AD2, opponents C0:736A, C0:733A) |
| $023E,X | actor state: 0 free, 4 down, 5 pinning/waiting |
| $0224,X | get-up counter |
| $701C | player's Power sum, AI level |
| $7000/$71C0 | wrestler: +$00 id, +$04 attack base, +$08 guard base, +$10 health, +$16 attack, +$18 defence, +$20 damage to deal |
| $7040/$7200 | card slots |
| $7400 | card ownership |
| $7450 | team records |
| $7E:834E | move script |
| $7E:8370/8372 | displayed health |
| $7E:8392/8394 | AI level, health index |

Opponents by match id, C0:736A (*data*), index to name: 07 Fuchi, 08 Eigen, 0C Red Bear 1, 0D Hyperspace Mask, 0E Red Bear 1, 0F-12 Red Bears 2-5, 14 Patriot, 15 Williams, 16 Gordy, 17 Hansen, 18 USA Mask, 19 Grunt 3, 1A Tutan Mask, 1B Hansen,
1D Hyperspace Mask, 1E Mecha Baba, 22-27 Hyperspace, USA, Tutan, Hyperspace, Red Bear 5, Tutan. 00-06 C0:733A: two random grunts per id (G1/G1, G1/G2, G2/G3, G3/G4, G4/G5, G5/G5, G5/G5). Others FFFF: set by the caller (team list C0:4BEB).

## 11. Unknown or not checked
- What moves lock-up scripts 0B-0F are by name (not watched).
- AI press rate in real play was not measured against the table; the table is read from code, and COM behaviour fits (*seen headless* logs show cursors and FALL when down).
- Lock-up frequency: from the code only.
- 2P mode wasn't run with two inputs; only the AI-off path (poked $01C6).
