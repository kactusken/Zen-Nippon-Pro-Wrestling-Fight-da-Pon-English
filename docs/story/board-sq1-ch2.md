# Board: sq1-ch2, $012C=7, events $C1:E74A, start pixel (800,784) tile (50,49)

Each line: space number, tile (x,y), what it does, next space(s). * = fork: the player picks with the D-pad.
Tiles are x>>4,y>>4 of the walker position. Counted spaces use one step; STORY STOP and GOAL always stop the walk.

  0 (50,49) START                              -> 1
  1 (46,47) CARD: Microphone (card 20)         -> 2
  2 (42,45) MATCH: random slot 1               -> 3
  3 (46,43) CARD: Headbutt (card 21)           -> 4
  4 (50,41) CARD TROUBLE                       -> 5
  5 (54,39) STORY STOP: script 0C              -> 6
  6 (58,37) MATCH: random slot 1               -> 7
  7 (62,35) CARD: Chest Chop (card 22)         -> 8
  8 (66,33) CARD TROUBLE                       -> 9
  9 (70,31) CARD: random                       -> 10
 10 (74,29) MATCH: random slot 1               -> 11
 11 (78,27) STORY STOP: script 0F              -> 12
 12 (82,25) CARD TROUBLE                       -> 13
 13 (86,23) CARD: Bulldog Headlock (card 23)   -> 14
 14 (86,21) CARD TROUBLE                       -> 15
 15 (82,19) CARD: Spit (card 19)               -> 16
 16 (78,17) MATCH: random slot 1               -> 17
 17 (74,15) CARD TROUBLE                       -> 18
 18 (70,17) CARD: random                       -> 19
 19 (66,19) MATCH: random slot 1               -> 20
 20 (62,21) CARD: Inchworm (card 24)           -> 21
 21 (58,23) CARD TROUBLE                       -> 22
 22 (54,25) STORY STOP: script 12              -> 23
 23 (50,27) CARD: random                       -> 24
 24 (46,29) CARD: random                       -> 25
 25 (42,29) CARD TROUBLE                       -> 26
 26 (38,27) CARD: Mongolian Chop (card 25)     -> 27, 45, 56 *
 27 (34,25) CARD: random                       -> 28
 28 (30,25) STORY STOP: script 17              -> 29
 29 (26,27) CARD TROUBLE                       -> 30
 30 (22,29) CARD: Backdrop (card 2)            -> 31
 31 (18,31) MATCH: random slot 1               -> 32
 32 (14,33) CARD: random                       -> 33
 33 (18,35) CARD TROUBLE                       -> 34
 34 (22,37) CARD: random                       -> 35
 35 (26,39) CARD TROUBLE                       -> 36
 36 (22,41) CARD: random                       -> 37
 37 (18,43) MATCH: random slot 1               -> 38
 38 (18,45) CARD TROUBLE                       -> 39
 39 (22,47) CARD: Microphone (card 20)         -> 40
 40 (26,49) MATCH: random slot 1               -> 41
 41 (30,51) CARD: random                       -> 42
 42 (34,53) CARD TROUBLE                       -> 43
 43 (38,55) CARD: random                       -> 44
 44 (42,53) GOAL: script 1D                    -> end
 45 (42,25) CARD TROUBLE                       -> 46
 46 (42,23) CARD: random                       -> 47
 47 (38,21) CARD TROUBLE                       -> 48
 48 (34,19) CARD: random                       -> 49
 49 (30,17) CARD: random                       -> 50
 50 (26,15) STORY STOP: script 1A              -> 51
 51 (22,17) CARD TROUBLE                       -> 52
 52 (18,19) CARD: DDT (card 8)                 -> 53
 53 (14,21) CARD: random                       -> 54
 54 (18,23) MATCH: random slot 1               -> 55
 55 (22,25) CARD: Powerbomb (card 9)           -> 29
 56 (34,29) CARD TROUBLE                       -> 57
 57 (34,31) CARD: random                       -> 58
 58 (38,33) MATCH: random slot 1               -> 59
 59 (34,35) CARD: random                       -> 60
 60 (30,37) STORY STOP: script 14              -> 35

Space counts: card 27, card trouble 16, match 10, story stops 6, goal 1

Map (one column = 2 tiles, one row = 2 tiles; S start, c card, T card trouble, M match, E story stop, G goal, + fork, . path):
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
