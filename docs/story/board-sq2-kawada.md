# Board: sq2-kawada, $012C=3, events $C1:E8AE, start pixel (1376,688) tile (86,43)

Each line: space number, tile (x,y), what it does, next space(s). * = fork: the player picks with the D-pad.
Tiles are x>>4,y>>4 of the walker position. Counted spaces use one step; STORY STOP and GOAL always stop the walk.

  0 (86,43) START                              -> 1
  1 (82,39) CARD: Powerbomb (card 9)           -> 2
  2 (78,37) CARD: random                       -> 3
  3 (74,39) CARD TROUBLE                       -> 4
  4 (70,41) MATCH: random slot 3               -> 5
  5 (74,43) CARD TROUBLE                       -> 6
  6 (70,45) CARD: Front Neck Lock (card 29)    -> 7
  7 (66,47) CARD: random                       -> 8
  8 (62,49) MATCH: random slot 3               -> 9
  9 (58,47) CARD TROUBLE                       -> 10
 10 (54,49) CARD TROUBLE                       -> 11
 11 (50,51) CARD: Soccer Kick (card 30)        -> 12
 12 (46,53) CARD: random                       -> 13
 13 (42,55) CARD TROUBLE                       -> 14
 14 (38,53) CARD: random                       -> 15
 15 (34,55) CARD: random                       -> 16
 16 (30,53) CARD TROUBLE                       -> 17
 17 (26,51) CARD: Spin Kick (card 32)          -> 18
 18 (22,53) MATCH: random slot 3               -> 19
 19 (18,51) CARD: Powerbomb (card 9)           -> 20
 20 (14,49) CARD TROUBLE                       -> 21
 21 (16,46) CARD TROUBLE                       -> 22
 22 (20,44) CARD: random                       -> 23
 23 (24,46) CARD: Spin Kick (card 32)          -> 24
 24 (28,48) CARD TROUBLE                       -> 25
 25 (32,50) MATCH: random slot 3               -> 26
 26 (36,48) CARD TROUBLE                       -> 27
 27 (34,45) CARD: random                       -> 28, 65 *
 28 (30,43) CARD: Spin Kick (card 32)          -> 29
 29 (26,41) CARD: random                       -> 30
 30 (22,39) CARD TROUBLE                       -> 31
 31 (24,36) CARD: random                       -> 32
 32 (28,34) CARD: random                       -> 33
 33 (32,36) MATCH: random slot 3               -> 34
 34 (36,38) CARD: random                       -> 35
 35 (40,36) CARD TROUBLE                       -> 36
 36 (44,34) CARD: Spin Kick (card 32)          -> 37
 37 (46,31) CARD: random                       -> 38, 56 *
 38 (42,29) CARD TROUBLE                       -> 39
 39 (38,31) CARD: random                       -> 40
 40 (34,29) MATCH: random slot 3               -> 41
 41 (30,31) CARD: random                       -> 42
 42 (26,29) CARD TROUBLE                       -> 43
 43 (22,27) CARD: random                       -> 44
 44 (18,25) MATCH: random slot 3               -> 45
 45 (22,23) CARD: Soccer Kick (card 30)        -> 46
 46 (24,20) CARD: random                       -> 47
 47 (26,17) CARD TROUBLE                       -> 48
 48 (30,19) CARD: random                       -> 49
 49 (32,16) CARD TROUBLE                       -> 50
 50 (36,18) CARD: random                       -> 51
 51 (40,16) MATCH: random slot 3               -> 52
 52 (44,18) CARD: Powerbomb (card 9)           -> 53
 53 (48,16) CARD TROUBLE                       -> 54
 54 (52,14) CARD TROUBLE                       -> 55
 55 (48,10) GOAL: script 3C                    -> end
 56 (50,29) CARD: Spin Kick (card 32)          -> 57
 57 (54,31) CARD: random                       -> 58
 58 (58,29) CARD TROUBLE                       -> 59
 59 (62,27) CARD: random                       -> 60
 60 (60,24) MATCH: random slot 3               -> 61
 61 (56,26) CARD TROUBLE                       -> 62
 62 (52,24) CARD: Powerbomb (card 9)           -> 63
 63 (50,21) CARD TROUBLE                       -> 64
 64 (52,18) MATCH: random slot 3               -> 53
 65 (38,43) CARD: Front Neck Lock (card 29)    -> 66
 66 (42,45) CARD: random                       -> 67
 67 (46,43) CARD: random                       -> 68
 68 (50,41) MATCH: random slot 3               -> 69
 69 (54,39) CARD: random                       -> 70
 70 (58,37) CARD TROUBLE                       -> 71
 71 (62,35) CARD: Soccer Kick (card 30)        -> 72
 72 (64,32) CARD TROUBLE                       -> 73
 73 (64,30) CARD TROUBLE                       -> 59

Space counts: card 37, card trouble 24, match 11, story stops 0, goal 1

Map (one column = 2 tiles, one row = 2 tiles; S start, c card, T card trouble, M match, E story stop, G goal, + fork, . path):
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
