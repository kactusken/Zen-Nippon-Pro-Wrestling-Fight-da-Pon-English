# Board: sq4-tsuruta, $012C=2, events $C1:E566, start pixel (992,176) tile (62,11)

Each line: space number, tile (x,y), what it does, next space(s). * = fork: the player picks with the D-pad.
Tiles are x>>4,y>>4 of the walker position. Counted spaces use one step; STORY STOP and GOAL always stop the walk.

  0 (62,11) START                              -> 1
  1 (58,15) CARD: random                       -> 2
  2 (54,13) MATCH: random slot 3               -> 3
  3 (50,15) CARD TROUBLE                       -> 4
  4 (54,17) CARD: Kitchen Sink (card 16)       -> 5
  5 (58,19) MATCH: random slot 3               -> 6
  6 (62,21) CARD: random                       -> 7
  7 (66,23) CARD TROUBLE                       -> 8
  8 (70,25) CARD: Jumping Knee (card 17)       -> 9
  9 (68,28) MATCH: random slot 3               -> 10
 10 (72,30) CARD: random                       -> 11
 11 (68,32) CARD TROUBLE                       -> 12
 12 (64,30) CARD: Throat Thrust (card 18)      -> 13
 13 (60,28) MATCH: random slot 3               -> 14
 14 (56,30) CARD: random                       -> 15
 15 (52,28) CARD TROUBLE                       -> 16
 16 (48,26) CARD: Kitchen Sink (card 16)       -> 17
 17 (44,24) MATCH: random slot 3               -> 18
 18 (40,22) CARD: random                       -> 19
 19 (44,20) MATCH: random slot 3               -> 20
 20 (40,18) CARD TROUBLE                       -> 21
 21 (36,16) CARD: Throat Thrust (card 18)      -> 22
 22 (34,19) MATCH: random slot 3               -> 23
 23 (30,21) CARD: random                       -> 24
 24 (34,23) CARD TROUBLE                       -> 25
 25 (30,25) CARD: random                       -> 26
 26 (26,27) MATCH: random slot 3               -> 27
 27 (30,29) CARD TROUBLE                       -> 28
 28 (34,31) CARD: random                       -> 29
 29 (38,29) MATCH: random slot 3               -> 30
 30 (42,31) CARD: random                       -> 31
 31 (46,33) CARD TROUBLE                       -> 32
 32 (50,35) CARD: random                       -> 33
 33 (54,37) MATCH: random slot 3               -> 34, 63 *
 34 (58,35) CARD: Jumping Knee (card 17)       -> 35
 35 (62,37) CARD TROUBLE                       -> 36
 36 (66,39) CARD: random                       -> 37
 37 (70,41) MATCH: random slot 3               -> 38
 38 (66,43) CARD: random                       -> 39
 39 (70,45) CARD TROUBLE                       -> 40
 40 (66,49) CARD: random                       -> 41
 41 (62,51) MATCH: random slot 3               -> 42
 42 (58,53) CARD: Throat Thrust (card 18)      -> 43
 43 (54,51) CARD TROUBLE                       -> 44
 44 (50,49) CARD: random                       -> 45
 45 (46,47) CARD TROUBLE                       -> 46
 46 (42,45) STORY STOP: script 31              -> 47
 47 (38,47) MATCH: random slot 3               -> 48
 48 (34,45) CARD: random                       -> 49
 49 (30,43) CARD TROUBLE                       -> 50
 50 (34,41) CARD: Jumping Knee (card 17)       -> 51
 51 (30,39) MATCH: random slot 3               -> 52
 52 (26,37) CARD: random                       -> 53
 53 (22,39) MATCH: random slot 3               -> 54
 54 (18,41) CARD TROUBLE                       -> 55
 55 (14,43) CARD: random                       -> 56
 56 (12,46) MATCH: random slot 3               -> 57
 57 ( 8,48) CARD: random                       -> 58
 58 (12,50) CARD TROUBLE                       -> 59
 59 (16,52) CARD: Throat Thrust (card 18)      -> 60
 60 (20,54) MATCH: random slot 3               -> 61
 61 (16,56) CARD TROUBLE                       -> 62
 62 (12,58) GOAL: script 34                    -> end
 63 (58,39) CARD TROUBLE                       -> 64
 64 (54,41) CARD TROUBLE                       -> 65
 65 (50,45) CARD: Jumping Knee (card 17)       -> 45

Space counts: card 28, card trouble 18, match 17, story stops 1, goal 1

Map (one column = 2 tiles, one row = 2 tiles; S start, c card, T card trouble, M match, E story stop, G goal, + fork, . path):
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
