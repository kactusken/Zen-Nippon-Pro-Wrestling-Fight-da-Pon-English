; Variable-width text renderer. Called from the game's text reader at $C0:1AC4 by JSL, with
; A = character code; M and X 16-bit. Text area: buffer $7E:E000, two lines $300 bytes apart, each
; 11 cells of $40 bytes holding tiles TL, TR, BL, BR (2bpp); ink = bit clear in the high plane.
; $0802 = pen x * 4 (176 px = $2C0, the game's own end-of-line test); $0804 = line base.
; Direct page $10-$1E is scratch, as in the original renderer ($14-$1E are saved here).
.m16
.x16
  JMP.w draw_two   ; $D10000
  NOP
  JMP.w title      ; $D10004: scenario title, from $C0:44E1
  NOP
  JMP.w prompt     ; $D10008: password prompt, from $C0:51F9
  NOP
  JMP.w listname   ; $D1000C: a name in the wrestler list, from $C0:41C5
  NOP
  JMP.w follow     ; $D10010: jump code $0E, from $C0:1AD8
  NOP
  JMP.w portrait   ; $D10014: the speaker's portrait tick, from $C0:E0E6
  NOP
follow:
  LDA $D00000,X
  STA $0806
  RTL
; The game's own bug: before a scene's first line this tick redraws the portrait object, whose
; fields the scene has cleared, so tile 0 of the sprites (the first wrestler) gets portrait tiles.
; Z set = no portrait this tick, the caller goes on to the text tick as on the other frames.
portrait:
  LDA $34
  AND #$0002
  BEQ portrait_end
  LDX $080A
  LDA $0206,X
  BNE portrait_end
; Also the game's own: the board's gauge stays on BG3 until the first line. Clear its 3 x 12 cells
; once and queue the map upload ($C0:D5EA, table entry 5) in place of this frame's text tick: drop
; our return address, so its RTS goes back to the caller of $C0:E0E6.
  LDA $7E6384
  CMP #$2000
  BEQ no_gauge
  PHY
  LDX #$6382
  LDY #$000C
gauge:
  LDA #$2000
  STA $7E0000,X
  STA $7E0002,X
  STA $7E0004,X
  TXA
  CLC
  ADC #$0040
  TAX
  DEY
  BNE gauge
  PLY
  PLA
  SEP #$20
  PLA
  REP #$20
  LDA #$0005
  JML $C0D5EA
no_gauge:
  LDA #$0000
portrait_end:
  RTL
draw_two:
  LDY #$0001       ; print two characters per tick: English runs twice as long
  BRA draw
draw_one:
  LDY #$0000
draw:
  PHD
  PHB
  LDX $14
  PHX
  LDX $16
  PHX
  LDX $18
  PHX
  LDX $1A
  PHX
  LDX $1C
  PHX
  LDX $1E
  PHX
  LDX $0E
  PHX
  STY $0E
one:
  SEC
  SBC #$0020
  BCC blank
  CMP #$0060
  BCC known
blank:
  LDA #$0000
known:
  TAX
  LDA WIDTHS,X
  AND #$00FF
  STA $1A
  TXA
  ASL A
  ASL A
  ASL A
  ASL A
  STA $14          ; glyph offset
  LDA $0802
  LSR A
  LSR A
  STA $16          ; pen x
  AND #$0007
  STA $18          ; shift
  LDA #$E000
  STA $10
  LDA #$007E
  STA $12
  STZ $1C          ; row
row:
  LDX $14
  LDA FONT,X
  AND #$00FF
  BEQ next
  XBA
  LDX $18
  BEQ shifted
shift:
  LSR A
  DEX
  BNE shift
shifted:
  PHA
  LDA $16
  JSR cell
  TAY
  PLA
  PHA
  XBA
  AND #$00FF
  EOR #$FFFF
  SEP #$20
  AND [$10],Y
  STA [$10],Y
  REP #$20
  LDA $16
  CLC
  ADC #$0008
  JSR cell
  TAY
  LDA $01,S
  AND #$00FF
  EOR #$FFFF
  SEP #$20
  AND [$10],Y
  STA [$10],Y
  REP #$20
  PLA
next:
  INC $14
  INC $1C
  LDA $1C
  CMP #$0010
  BCC row
  LDA $1A
  ASL A
  ASL A
  CLC
  ADC $0802
  STA $0802
  LDX $0E
  BEQ done
  DEC $0E
  LDX $0806
  LDA $D00000,X
  AND #$00FF
  CMP #$0020
  BCC done
  CMP #$0080
  BCS done
  INC $0806
  JMP one
done:
  PLX
  STX $0E
  PLX
  STX $1E
  PLX
  STX $1C
  PLX
  STX $1A
  PLX
  STX $18
  PLX
  STX $16
  PLX
  STX $14
  PLB
  PLD
  RTL
; A = x in pixels, $1C = row: returns the buffer offset of the high-plane byte
cell:
  PHA
  LSR A
  LSR A
  LSR A
  LSR A
  ASL A
  ASL A
  ASL A
  ASL A
  ASL A
  ASL A            ; cell * $40
  STA $1E
  PLA
  AND #$0008
  ASL A            ; right tile: +$10
  CLC
  ADC $1E
  CLC
  ADC $0804
  STA $1E
  LDA $1C
  AND #$0007
  ASL A
  INC A
  CLC
  ADC $1E
  STA $1E
  LDA $1C
  AND #$0008
  BEQ top
  LDA $1E
  CLC
  ADC #$0020
  RTS
top:
  LDA $1E
  RTS

; Scenario title in the select bubble: $00 = the message's address in bank $C4. Line 2 sits at $2C0
; here, right after the first (the game's tilemap at $C0:4529 counts cells straight on).
title:
  PHA
  PHX
  LDA #$FFFF
  STA $7EE000
  LDX #$E000
  LDY #$E001
  LDA #$05FE
  PHB
  db $54,$7E,$7E
  PLB
  STZ $0802
  STZ $0804
  LDX $00
  LDA $D00000,X
  AND #$00FF
  CMP #$000E
  BNE tloop
  INX
  LDA $D00000,X
  STA $00
tloop:
  LDX $00
  LDA $D00000,X
  AND #$00FF
  INC $00
  CMP #$000B
  BEQ tend
  CMP #$0000
  BEQ tend
  CMP #$0002
  BEQ tnl
  CMP #$0010
  BCC tloop
  JSL draw_one
  BRA tloop
tnl:
  LDA #$02C0
  STA $0804
  STZ $0802
  BRA tloop
tend:
  STZ $0802
  STZ $0804
  LDA #$0016
  STA $06D8
  PLX
  PLA
  RTL

; Password screen: A = string, Y = buffer offset of its first cell. Returns Y past the cells the
; original string took, so the next string lands where it did.
prompt:
  ASL A
  TAX
  LDA PROMPTS,X
  STA $00
  LDA PROMPTCELLS,X
  STA $02
  PHX
  PHY
  TYA
  TAX
  LDY $02
pclear:
  LDA #$FFFF
  PHY
  LDY #$0020
pc2:
  STA $7EE000,X
  INX
  INX
  DEY
  BNE pc2
  PLY
  DEY
  BNE pclear
  PLA
  PHA
  STA $0802
  STZ $0804
ploop:
  LDX $00
  LDA $D10000,X
  AND #$00FF
  BEQ pend
  INC $00
  JSL draw_one
  BRA ploop
pend:
  STZ $0802
  PLA
  PLX
  CLC
  ADC PROMPTSTEP,X
  TAY
  RTL

; Wrestler list: A = wrestler, Y = buffer offset. The record's count is cells here, and the game's
; tilemap reads the same count through $C0:4166. Returns Y past the cells and $18 advanced.
listname:
  ASL A
  TAX
  LDA $D11480,X
  TAX
  LDA $D10000,X
  PHA
  CLC
  ADC $18
  STA $18
  TYA
  PHA
  STA $0802
  STZ $0804
  INX
  INX
lloop:
  LDA $D10000,X
  CMP #$000B
  BEQ lend
  PHX
  JSL draw_one
  PLX
  INX
  INX
  BRA lloop
lend:
  STZ $0802
  PLA
  TAY
  PLX
lstep:
  TYA
  CLC
  ADC #$0040
  TAY
  DEX
  BNE lstep
  RTL
