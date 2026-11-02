# Board: sq5-hawaii, $012C=6, events $C1:E9D4, start pixel (1632,656) tile (102,41)

Each line: space number, tile (x,y), what it does, next space(s). * = fork: the player picks with the D-pad.
Tiles are x>>4,y>>4 of the walker position. Counted spaces use one step; STORY STOP and GOAL always stop the walk.

  0 (102,41) START                              -> 1
  1 (98,43) CARD: random                       -> 2
  2 (94,45) CARD: random                       -> 3
  3 (90,47) CARD: DDT (card 8)                 -> 4
  4 (86,49) MATCH: random slot 6               -> 5
  5 (82,51) CARD: random                       -> 6
  6 (78,53) MATCH: random slot 6               -> 7
  7 (74,51) CARD: random                       -> 8
  8 (70,49) CARD TROUBLE                       -> 9
  9 (66,47) CARD: random                       -> 10
 10 (62,49) MATCH: random slot 6               -> 11
 11 (58,47) CARD: random                       -> 12
 12 (54,45) CARD TROUBLE                       -> 13, 34 *
 13 (50,43) CARD: random                       -> 14
 14 (46,41) MATCH: random slot 6               -> 15
 15 (42,41) CARD: random                       -> 16
 16 (38,43) CARD TROUBLE                       -> 17
 17 (34,45) MATCH: random slot 6               -> 18
 18 (30,45) CARD: random                       -> 19
 19 (26,43) CARD TROUBLE                       -> 20
 20 (22,41) CARD: Dropkick (card 10)           -> 21
 21 (18,39) MATCH: random slot 6               -> 22
 22 (14,37) CARD: random                       -> 23
 23 (10,35) CARD TROUBLE                       -> 24
 24 (10,33) MATCH: random slot 6               -> 25
 25 (14,31) CARD: random                       -> 26
 26 (18,29) CARD TROUBLE                       -> 27
 27 (18,27) MATCH: random slot 6               -> 28
 28 (14,25) MATCH: random slot 6               -> 29
 29 (14,23) CARD: random                       -> 30
 30 (18,21) CARD TROUBLE                       -> 31
 31 (22,19) CARD TROUBLE                       -> 32
 32 (26,17) MATCH: random slot 6               -> 33
 33 (22,15) GOAL: script 42                    -> end
 34 (58,43) CARD: Powerbomb (card 9)           -> 35
 35 (62,41) MATCH: random slot 6               -> 36
 36 (66,39) CARD: random                       -> 37
 37 (70,37) CARD TROUBLE                       -> 38
 38 (74,35) MATCH: random slot 6               -> 39
 39 (78,33) CARD: random                       -> 40
 40 (78,31) CARD: random                       -> 41
 41 (74,29) CARD TROUBLE                       -> 42
 42 (70,27) CARD: random                       -> 43
 43 (66,25) MATCH: random slot 6               -> 44
 44 (62,23) CARD: Dropkick (card 10)           -> 45, 59 *
 45 (66,21) MATCH: random slot 6               -> 46
 46 (70,19) CARD TROUBLE                       -> 47
 47 (74,17) CARD: random                       -> 48
 48 (74,15) CARD: random                       -> 49
 49 (70,13) CARD TROUBLE                       -> 50
 50 (66,11) CARD: random                       -> 51
 51 (62, 9) MATCH: random slot 6               -> 52
 52 (58, 9) CARD TROUBLE                       -> 53
 53 (54,11) CARD: random                       -> 54
 54 (50,13) MATCH: random slot 6               -> 55
 55 (46,15) CARD: DDT (card 8)                 -> 56
 56 (42,17) CARD TROUBLE                       -> 57
 57 (38,15) MATCH: random slot 6               -> 58
 58 (34,13) CARD: random                       -> 32
 59 (58,25) CARD TROUBLE                       -> 60
 60 (54,27) MATCH: random slot 6               -> 61
 61 (50,29) CARD: random                       -> 62
 62 (46,29) CARD TROUBLE                       -> 63
 63 (42,27) MATCH: random slot 6               -> 64
 64 (38,25) CARD: Powerbomb (card 9)           -> 65
 65 (34,27) CARD TROUBLE                       -> 66
 66 (30,27) CARD: random                       -> 67
 67 (26,25) MATCH: random slot 6               -> 68
 68 (22,23) CARD: random                       -> 30
off-path, unreachable: (30,31) CARD: random

Space counts: card 30, card trouble 17, match 20, story stops 0, goal 1

Map (one column = 2 tiles, one row = 2 tiles; S start, c card, T card trouble, M match, E story stop, G goal, + fork, . path):
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
