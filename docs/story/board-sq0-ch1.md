# Board: sq0-ch1, $012C=12, events $C1:E83C, start pixel (800,784) tile (50,49)

Each line: space number, tile (x,y), what it does, next space(s). * = fork: the player picks with the D-pad.
Tiles are x>>4,y>>4 of the walker position. Counted spaces use one step; STORY STOP and GOAL always stop the walk.

  0 (50,49) START                              -> 1
  1 (46,47) CARD: random                       -> 2
  2 (42,45) MATCH: random slot 0               -> 3
  3 (46,43) CARD: Sixteen-Mon Kick (card 11)   -> 4
  4 (50,41) CARD TROUBLE                       -> 5
  5 (54,39) STORY STOP: script 03              -> 6
  6 (58,37) MATCH: random slot 0               -> 7
  7 (62,35) CARD: random                       -> 8
  8 (62,33) CARD TROUBLE                       -> 9
  9 (58,31) CARD: Neckbreaker Drop (card 12)   -> 10
 10 (54,29) MATCH: random slot 0               -> 11
 11 (50,27) CARD: random                       -> 12
 12 (46,29) CARD TROUBLE                       -> 13
 13 (42,31) CARD: Coconut Crush (card 13)      -> 14
 14 (38,33) MATCH: random slot 0               -> 15
 15 (34,35) CARD: random                       -> 16
 16 (30,37) STORY STOP: script 01              -> 17
 17 (26,39) CARD TROUBLE                       -> 18
 18 (22,37) CARD: Brain Chop (card 14)         -> 19
 19 (18,35) CARD TROUBLE                       -> 20
 20 (14,33) CARD: Brain Chop (card 14)         -> 21
 21 (18,31) MATCH: random slot 0               -> 22
 22 (22,29) CARD: random                       -> 23
 23 (26,27) CARD TROUBLE                       -> 24
 24 (30,25) STORY STOP: script 02              -> 25
 25 (34,23) MATCH: random slot 0               -> 26
 26 (38,21) CARD TROUBLE                       -> 27
 27 (34,19) CARD: Kawazu Drop (card 15)        -> 28
 28 (30,17) GOAL: script 04                    -> end

Space counts: card 11, card trouble 7, match 6, story stops 3, goal 1

Map (one column = 2 tiles, one row = 2 tiles; S start, c card, T card trouble, M match, E story stop, G goal, + fork, . path):
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
