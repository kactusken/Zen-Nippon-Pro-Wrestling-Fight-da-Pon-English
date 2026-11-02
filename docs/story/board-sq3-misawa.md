# Board: sq3-misawa, $012C=5, events $C1:E66C, start pixel (1248,528) tile (78,33)

Each line: space number, tile (x,y), what it does, next space(s). * = fork: the player picks with the D-pad.
Tiles are x>>4,y>>4 of the walker position. Counted spaces use one step; STORY STOP and GOAL always stop the walk.

  0 (78,33) START                              -> 1
  1 (74,31) CARD: Flying Lariat (card 28)      -> 2
  2 (70,29) MATCH: random slot 2               -> 3
  3 (74,27) CARD: random                       -> 4
  4 (78,25) CARD TROUBLE                       -> 5
  5 (82,23) CARD: random                       -> 6
  6 (86,21) MATCH: random slot 2               -> 7
  7 (82,19) CARD: Front Neck Lock (card 29)    -> 8
  8 (78,17) MATCH: random slot 2               -> 9
  9 (82,15) CARD TROUBLE                       -> 10
 10 (86,13) CARD: random                       -> 11
 11 (90,11) CARD: random                       -> 12
 12 (86, 9) STORY STOP: script 21              -> 13
 13 (82,11) MATCH: random slot 2               -> 14
 14 (78, 9) CARD: random                       -> 15
 15 (74,11) CARD TROUBLE                       -> 16
 16 (70,13) MATCH: random slot 2               -> 17, 48 *
 17 (66,11) CARD: Zero Fighter (card 33)       -> 18
 18 (62, 9) MATCH: random slot 2               -> 19
 19 (58,11) CARD: random                       -> 20
 20 (54,13) CARD TROUBLE                       -> 21
 21 (50,15) MATCH: random slot 2               -> 22
 22 (46,13) CARD: Diving Headbutt (card 34)    -> 23
 23 (42,11) STORY STOP: script 24              -> 24
 24 (38,13) CARD TROUBLE                       -> 25
 25 (34,15) CARD: Tiger Driver (card 26)       -> 26
 26 (30,17) MATCH: random slot 2               -> 27
 27 (26,15) CARD: random                       -> 28
 28 (22,13) CARD TROUBLE                       -> 29
 29 (18,15) CARD: Rolling Move (card 37)       -> 30
 30 (14,17) MATCH: random slot 2               -> 31
 31 (10,19) STORY STOP: script 27              -> 32
 32 (14,21) CARD: random                       -> 33
 33 (18,23) MATCH: random slot 2               -> 34
 34 (22,25) CARD: Moonsault (card 36)          -> 35
 35 (18,27) CARD TROUBLE                       -> 36
 36 (14,29) CARD: random                       -> 37
 37 (10,31) MATCH: random slot 2               -> 38
 38 (14,33) CARD: Jumping Shoulder (card 35)   -> 39
 39 (18,35) CARD TROUBLE                       -> 40
 40 (22,37) CARD: random                       -> 41
 41 (26,35) MATCH: random slot 2               -> 42
 42 (30,33) CARD TROUBLE                       -> 43
 43 (34,35) CARD: random                       -> 44
 44 (38,37) CARD TROUBLE                       -> 45
 45 (42,39) CARD: random                       -> 46
 46 (46,37) MATCH: random slot 2               -> 47
 47 (50,39) GOAL: script 2A                    -> end
 48 (66,15) CARD: random                       -> 49
 49 (62,17) CARD TROUBLE                       -> 50
 50 (58,19) CARD: Tiger Suplex (card 27)       -> 51
 51 (54,21) CARD TROUBLE                       -> 52
 52 (50,23) MATCH: random slot 2               -> 53
 53 (46,21) CARD: random                       -> 54
 54 (50,19) CARD TROUBLE                       -> 55
 55 (54,17) CARD: random                       -> 21

Space counts: card 24, card trouble 13, match 14, story stops 3, goal 1

Map (one column = 2 tiles, one row = 2 tiles; S start, c card, T card trouble, M match, E story stop, G goal, + fork, . path):
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
