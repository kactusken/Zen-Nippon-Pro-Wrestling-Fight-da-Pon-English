#!/usr/bin/env python3
"""Drive a SNES or GBA game headless in Mesen 2 (--testrunner) from a list of steps: input, screenshots,
savestates, memory reads, writes and dumps, access traces and rule-based autoplay. For research
and automated checks, not for releases. The console comes from tools/paths.py PLATFORM.

  mesen.py [--rom ROM] [--out DIR] [--states DIR] [--max-frames N] [--timeout S] [--mesen PATH]
           [--dry-run] STEP...
  mesen.py --file STEPS.txt [STEP...]

  --rom ROM        the image to run (default: paths.ROM, the ORIGINAL - pass the build to test it)
  --out DIR        screenshots, dumps, trace.txt, peek.txt, auto.log, mesen.log, run.lua
                   (default build/work/mesen)
  --states DIR     where save/load keep NAME.mss (default OUT/states); share one folder between
                   runs to start each run from an earlier one's states
  --max-frames N   stop after N frames (exit 2; default 200000)
  --timeout S      kill Mesen after S seconds (exit 124)
  --mesen PATH     Mesen.exe or its folder (default $MESEN, then <projects>/_emulators/Mesen,
                   /mnt/e/Translations/_emulators/Mesen, /mnt/e/Code/_emulators/Mesen)
  --dry-run        write OUT/run.lua and stop (to read or run the generated script by hand)

Steps (one per argument, or one per line in --file; # starts a comment):
  wait N                      run N frames                                  wait 300
  press BUTTONS [N]           hold buttons for N frames (default 3), then 3 free frames
                                                                            press start / press a+b 6
  mash BUTTONS FRAMES [EVERY] press for 3 frames every EVERY (default 12), for FRAMES frames
                                                                            mash a 600 20
  shot NAME                   screenshot -> OUT/NAME.png                    shot title
  save NAME / load NAME       savestate -> / <- STATES/NAME.mss             save menu / load menu
  peek [MEM] ADDR [LEN]       LEN bytes (default 1; MEM default bus) -> OUT/peek.txt, also printed
                              after the run as "frame MEM ADDR: bytes"      peek $7E:71F0 2
  poke [MEM] ADDR BYTE[,BYTE...]  write bytes (MEM default bus: WRAM is $7E0000-$7FFFFF, PPU/CPU
                              registers at $2100.../$4200...)               poke $7E:71F0 $0C,0
  dump MEM START LEN NAME     memory -> OUT/NAME.bin                        dump wram 0 131072 ram
  write MEM START FILE        a file's bytes into memory from START (hex; e.g. a battery save)
                                                                            write sram 0 base.srm
  trace KIND START END [MAX] [PEEK:LEN]  log accesses (read|write|exec) on the CPU bus in
                              START..END with frame, PC, A/X/Y/DB/P/S and the value, up to MAX lines
                              (default 2000) -> OUT/trace.txt; PEEK:LEN adds LEN bus bytes from
                              PEEK to each line (PEEK below $100: a direct page offset)
                                                                            trace write 7E71F0 7E71F1
  untrace                     stop all traces
  regs PREFIX NAME            Mesen state values starting with PREFIX (ppu., cpu., dma.)
                              -> OUT/NAME.txt                               regs ppu. ppu
  cdl NAME                    Mesen's code/data log of the ROM -> OUT/NAME.cdl (one flag byte per
                              ROM byte: 1 = executed as code, 2 = read as data)    cdl cover
  until ADDR BYTE [LIMIT]     run until bus byte ADDR == BYTE (at most LIMIT frames, default 600)
                                                                            until $7E:0100 1 3000
  onexec ADDR MEM BYTE[,BYTE...]  from now on, whenever the CPU is about to run ADDR, write BYTE
                              to bus address MEM first (e.g. force a random number the code reads);
                              with a list, each run of ADDR writes the next value (cycling)
                                                                            onexec $80:9000 $7E:0042 3
  autoplay FRAMES FILE.lua [KEY=VALUE...]  play by rules for at most FRAMES frames: FILE returns
                              a function rule(frame, api) called every frame; it returns the buttons
                              to hold ({b=true}, or nil) or "stop" to go on with the next step. api
                              has rb(addr) / rw(addr) (bus byte / word), shot(name), log(text)
                              (-> OUT/auto.log) and args (the KEY=VALUE pairs, as strings)
                                                                            autoplay 30000 rules.lua stop=3

Buttons: a b x y l r start select up down left right, joined with + (a+b).
MEM: wram vram cgram oam rom sram bus (GBA: ewram iwram vram pal oam rom sav bus). Addresses are hex:
$80:8000, 808000, 0x808000 (GBA: 02001000). Byte values,
LEN, MAX and frame counts are DECIMAL unless written $xx or 0x.. (dump wram 0 1000 reads 1000 bytes).
Exit status: 0 all steps done, 2 frame limit, 124 timeout, anything else from Mesen itself.

Pitfalls (learned on Super Wrestle Angels, Bishoujo Wrestler Retsuden and Jikkyou Power Pro
Wrestling '96): Mesen must run in portable mode with Lua I/O allowed and a controller in port 1 -
this adds those two settings to settings.json next to Mesen.exe (other settings are kept); without
the controller every press is ignored. Savestates only work inside an exec callback (save/load do
that for you; load then runs two frames, so a shot after it shows the loaded screen). A savestate
keeps the WRAM and VRAM of the build that made it, so text and graphics changes need a run from
power-on, or a state from before the screen is loaded; check graphics on a freshly loaded screen,
never by writing VRAM into a state (a block that decodes right that way can still be garbled for
real). Start traces before the input steps whose effect they should catch; a trace of one byte
catches nothing, so this widens START..START to two bytes and drops the extra hits. I/O registers
only match the address form the code uses ($80:2118 is not $00:2118), DMA transfers don't show as
CPU reads, and read traces on WRAM caught nothing in JPPW (trace writes, or exec on the reading
code). The test runner exits by itself (exit 255) after about 35,000-40,000 frames: run long
sessions in segments (save, then load in the next run). Savestates made during some games' matches
crash Mesen (exit 255): save before. The game's battery save lives in Mesen's Saves/ folder and
carries over between runs - `write sram 0 FILE` first for a known start.

On GBA: buttons a b l r start select and the d-pad. Trace lines give the running instruction's PC,
r0-r3, lr, sp and T=1 in Thumb; trace `bus` addresses as the CPU sees them (02xxxxxx, 08xxxxxx), and
a ROM read trace shows who reads a string or a pointer table. Mesen needs a BIOS for GBA games:
Firmware/gba_bios.bin next to Mesen.exe, without which the first SWI runs into nothing and the screen
stays black. The open one at https://github.com/Cult-of-GBA/BIOS (MIT) works; this stops if none is there.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

HERE = Path(__file__).resolve().parent
# Where Mesen 2 has lived for the kit's projects: next to the project folders, or the shared copy
MESEN_CANDIDATES = [HERE.parents[1] / '_emulators/Mesen', Path('/mnt/e/Translations/_emulators/Mesen'),
                    Path('/mnt/e/Code/_emulators/Mesen')]
SNES_REGS = r'''  local s = emu.getState()
  return hex(s["cpu.k"], 2) .. ":" .. hex(s["cpu.pc"], 4) .. " A=" .. hex(s["cpu.a"], 4) ..
    " X=" .. hex(s["cpu.x"], 4) .. " Y=" .. hex(s["cpu.y"], 4) .. " DB=" .. hex(s["cpu.dbr"], 2) .. " P=" .. hex(s["cpu.ps"], 2) .. " S=" .. hex(s["cpu.sp"], 4)'''
GBA_REGS = r'''  local s = emu.getState()
  return "PC=" .. hex(s["cpu.pipeline.execute.address"], 8) .. " R0=" .. hex(s["cpu.r0"], 8) .. " R1=" .. hex(s["cpu.r1"], 8) ..
    " R2=" .. hex(s["cpu.r2"], 8) .. " R3=" .. hex(s["cpu.r3"], 8) .. " LR=" .. hex(s["cpu.r14"], 8) .. " SP=" .. hex(s["cpu.r13"], 8) ..
    " T=" .. (s["cpu.cpsr.thumb"] and "1" or "0")'''
CONSOLES = {
    'SNES': {'mem': {'wram': 'snesWorkRam', 'vram': 'snesVideoRam', 'cgram': 'snesCgRam', 'oam': 'snesSpriteRam',
                     'rom': 'snesPrgRom', 'sram': 'snesSaveRam', 'bus': 'snesMemory'},
             'buttons': {'a', 'b', 'x', 'y', 'l', 'r', 'start', 'select', 'up', 'down', 'left', 'right'},
             'cpu': 'snes', 'bus': 'snesMemory', 'prg': 'snesPrgRom', 'top': 0xffffff, 'width': 6, 'regs': SNES_REGS,
             'section': ('Snes', 'Port1'), 'controller': 'SnesController'},
    'GBA': {'mem': {'ewram': 'gbaExtWorkRam', 'iwram': 'gbaIntWorkRam', 'vram': 'gbaVideoRam', 'pal': 'gbaPaletteRam',
                    'oam': 'gbaSpriteRam', 'rom': 'gbaPrgRom', 'sav': 'gbaSaveRam', 'bus': 'gbaMemory'},
            'buttons': {'a', 'b', 'l', 'r', 'start', 'select', 'up', 'down', 'left', 'right'},
            'cpu': 'gba', 'bus': 'gbaMemory', 'prg': 'gbaPrgRom', 'top': 0x0fffffff, 'width': 8, 'regs': GBA_REGS,
            'section': ('Gba', 'Controller'), 'controller': 'GbaController'},
}
CONSOLE = CONSOLES.get(getattr(paths, 'PLATFORM', 'SNES').upper(), CONSOLES['SNES'])
MEM = CONSOLE['mem']
BUTTONS = CONSOLE['buttons']

LUA_HEAD = r'''
local OUT = %(out)s
local STATES = %(states)s
local steps = %(steps)s
local MAXF = %(maxf)d
local i, f, wait, held, mash = 1, 0, 0, nil, nil
local tracefile, peekfile, cbs = nil, nil, {}
local auto, autobtn, autolog = nil, nil, nil
local function path(p) return OUT .. p end
local function hex(n, w) return string.format("%%0" .. (w or %(width)d) .. "X", n) end
local function regs()
%(regs)s
end
local function screenshot(n) local h = io.open(path(n .. ".png"), "wb"); h:write(emu.takeScreenshot()); h:close() end
-- a callback on one byte never fires: register at least two and filter (lo, hi = the real range)
local function addcb(fn, kind, lo, hi)
  local b = hi
  if b <= lo then b = lo + 1 end
  local id = emu.addMemoryCallback(function(addr, value)
    if addr >= lo and addr <= hi then fn(addr, value) end
  end, emu.callbackType[kind], lo, b, emu.cpuType.%(cpu)s, emu.memType.%(bus)s)
  return {id, kind, lo, b}
end
local function addtrace(kind, a, b, max, pa, pn)
  if not tracefile then tracefile = io.open(path("trace.txt"), "a") end
  local n = 0
  cbs[#cbs + 1] = addcb(function(addr, value)
    if n < max then
      n = n + 1
      local peek = ""
      if pn and pn > 0 then
        local t = {}
        local base = pa
        if pa < 0x100 then base = emu.getState()["cpu.d"] + pa end   -- direct page offset
        for k = 0, pn - 1 do t[#t + 1] = string.format("%%02X", emu.read(base + k, emu.memType.%(bus)s, false)) end
        peek = " @" .. table.concat(t)
      end
      tracefile:write(string.format("%%6d %%s %%s=%%02X %%s%%s\n", f, kind, hex(addr), value or 0, regs(), peek))
    end
  end, kind, a, b)
end
local function untrace()
  for _, c in ipairs(cbs) do emu.removeMemoryCallback(c[1], emu.callbackType[c[2]], c[3], c[4], emu.cpuType.%(cpu)s, emu.memType.%(bus)s) end
  cbs = {}
  if tracefile then tracefile:flush() end
end
local function finish(code)
  untrace()
  if tracefile then tracefile:close() end
  if peekfile then peekfile:close() end
  if autolog then autolog:close() end
  emu.stop(code)
end
emu.addEventCallback(function()
  if auto then if autobtn then emu.setInput(autobtn, 0) end
  elseif held then emu.setInput(held, 0) elseif mash and (f %% mash.every) < 3 then emu.setInput(mash.buttons, 0) end
end, emu.eventType.inputPolled)
emu.addEventCallback(function()
  f = f + 1
  if f > MAXF then finish(2) return end
  if auto then
    local r = auto.rule(f, auto.api)
    auto.left = auto.left - 1
    if r == "stop" or auto.left <= 0 then auto = nil; autobtn = nil else autobtn = r; return end
  end
  if wait > 0 then
    wait = wait - 1
    if wait == 0 then held = nil; mash = nil; if steps[i - 1] and steps[i - 1][1] == "press" then wait = -3 end end
    return
  end
  if wait < 0 then wait = wait + 1 return end
  while i <= #steps do
    local s = steps[i]; i = i + 1
    local op = s[1]
    if op == "wait" then wait = s[2] return
    elseif op == "press" then held = s[2]; wait = s[3] return
    elseif op == "mash" then mash = {buttons = s[2], every = s[4]}; wait = s[3] return
    elseif op == "shot" then screenshot(s[2])
    elseif op == "save" or op == "load" then
      -- savestates only work inside an exec callback: run once on the next instruction
      local id
      id = emu.addMemoryCallback(function()
        emu.removeMemoryCallback(id, emu.callbackType.exec, 0, %(top)d, emu.cpuType.%(cpu)s, emu.memType.%(bus)s)
        if op == "save" then
          local h = io.open(STATES .. s[2] .. ".mss", "wb"); h:write(emu.createSavestate()); h:close()
        else
          local h = io.open(STATES .. s[2] .. ".mss", "rb"); emu.loadSavestate(h:read("a")); h:close()
        end
      end, emu.callbackType.exec, 0, %(top)d, emu.cpuType.%(cpu)s, emu.memType.%(bus)s)
      -- after a load the screen shows the old frame until one has been drawn: one more frame
      if op == "load" then wait = 2 else wait = 1 end
      return
    elseif op == "peek" then
      if not peekfile then peekfile = io.open(path("peek.txt"), "a") end
      local mt = emu.memType[s[2]]; local t = {}
      for a = s[3], s[3] + s[4] - 1 do t[#t + 1] = string.format("%%02X", emu.read(a, mt, false)) end
      peekfile:write(string.format("%%d %%s %%s: %%s\n", f, s[5], hex(s[3]), table.concat(t, " "))); peekfile:flush()
    elseif op == "dump" then
      local h = io.open(path(s[5] .. ".bin"), "wb"); local mt = emu.memType[s[2]]
      local t = {}
      for a = s[3], s[3] + s[4] - 1 do t[#t + 1] = string.char(emu.read(a, mt, false)) end
      h:write(table.concat(t)); h:close()
    elseif op == "poke" then
      local mt = emu.memType[s[2]]
      for k, v in ipairs(s[4]) do emu.write(s[3] + k - 1, v, mt) end
    elseif op == "write" then
      local h = io.open(s[4], "rb"); local b = h:read("a"); h:close(); local mt = emu.memType[s[2]]
      for k = 1, #b do emu.write(s[3] + k - 1, b:byte(k), mt) end
    elseif op == "trace" then addtrace(s[2], s[3], s[4], s[5], s[6], s[7])
    elseif op == "untrace" then untrace()
    elseif op == "regs" then
      local st = emu.getState(); local t = {}
      for k, v in pairs(st) do if k:sub(1, #s[2]) == s[2] then t[#t + 1] = k .. "=" .. tostring(v) end end
      table.sort(t); local h = io.open(path(s[3] .. ".txt"), "w"); h:write(table.concat(t, "\n")); h:close()
    elseif op == "cdl" then
      -- the table starts at index 0 (offset 0): from 1 would drop it and shift every flag by one
      local c = emu.getCdlData(emu.memType.%(prg)s); local t = {}
      local k0 = 1; if c[0] ~= nil then k0 = 0 end
      for k = k0, #c do t[#t + 1] = string.char(c[k]) end
      local h = io.open(path(s[2] .. ".cdl"), "wb"); h:write(table.concat(t)); h:close()
    elseif op == "autoplay" then
      local api = {}
      api.rb = function(a) return emu.read(a, emu.memType.%(bus)s, false) end
      api.rw = function(a) return api.rb(a) + 256 * api.rb(a + 1) end
      api.shot = screenshot
      api.log = function(t) if not autolog then autolog = io.open(path("auto.log"), "a") end; autolog:write(t .. "\n"); autolog:flush() end
      api.args = s[4]
      auto = {rule = dofile(s[3]), left = s[2], api = api}
      return
    elseif op == "onexec" then
      local m, vals, n = s[3], s[4], 0
      addcb(function()
        emu.write(m, vals[n %% #vals + 1], emu.memType.%(bus)s); n = n + 1 end, "exec", s[2], s[2])
    elseif op == "until" then
      if emu.read(s[2], emu.memType.%(bus)s, false) ~= s[3] and s[4] > 0 then s[4] = s[4] - 1; i = i - 1 return end
    end
  end
  finish(0)
end, emu.eventType.endFrame)
'''


def find_mesen(arg=None):
    """Mesen.exe (or a native Mesen binary) from --mesen, $MESEN or the known folders."""
    tried = []
    for c in ([arg] if arg else []) + ([os.environ['MESEN']] if os.environ.get('MESEN') else []) + MESEN_CANDIDATES:
        p = Path(c)
        for exe in ([p / 'Mesen.exe', p / 'Mesen'] if p.is_dir() else [p]):
            if exe.is_file():
                return exe.resolve()
        tried.append(str(c))
        if c in (arg, os.environ.get('MESEN')):   # an explicit choice that's wrong is an error
            sys.exit(f'mesen: no Mesen at {c}; give Mesen.exe or its folder (--mesen PATH or MESEN=PATH)')
    sys.exit('mesen: Mesen 2 not found (tried ' + ', '.join(tried) + '); unzip Mesen 2 there or give '
             '--mesen PATH / MESEN=PATH (Mesen.exe or its folder)')


def is_windows_exe(mesen):
    return mesen.suffix.lower() == '.exe' and shutil.which('wslpath') is not None


def hostpath(p, win=True):
    """The path as Mesen sees it: a Windows path for Mesen.exe under WSL."""
    if not win:
        return str(Path(p).resolve())
    return subprocess.run(['wslpath', '-w', str(Path(p).resolve())], capture_output=True, text=True,
                          check=True).stdout.strip()


def lua_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def num(s):
    """A count or byte value: decimal, or hex as $xx / 0x.. (as the earlier project copies read them)."""
    s = s.strip()
    return int(s[1:], 16) if s.startswith('$') else int(s, 0)


def buttons(s):
    bs = set(s.lower().split('+'))
    if bs - BUTTONS:
        raise SystemExit(f'mesen: unknown button(s) {sorted(bs - BUTTONS)}: use {" ".join(sorted(BUTTONS))}')
    return '{' + ', '.join(f'{b}=true' for b in sorted(bs)) + '}'


def addr(s):
    s = s.strip().lower().replace(':', '').replace('$', '')
    return int(s, 16) if not s.startswith('0x') else int(s, 0)


def mem(s):
    if s not in MEM:
        raise SystemExit(f'mesen: unknown memory {s!r}: use {" ".join(MEM)}')
    return MEM[s]


def compile_step(line, win=True):
    """One step line -> a Lua table literal."""
    w = line.split()
    op = w[0]
    try:
        if op == 'wait':
            return f'{{"wait", {num(w[1])}}}'
        if op == 'press':
            return f'{{"press", {buttons(w[1])}, {num(w[2]) if len(w) > 2 else 3}}}'
        if op == 'mash':
            return f'{{"mash", {buttons(w[1])}, {num(w[2])}, {num(w[3]) if len(w) > 3 else 12}}}'
        if op in ('shot', 'save', 'load', 'cdl'):
            return f'{{"{op}", {lua_str(w[1])}}}'
        if op == 'peek':
            m = w.pop(1) if w[1] in MEM else 'bus'
            return f'{{"peek", "{MEM[m]}", {addr(w[1])}, {num(w[2]) if len(w) > 2 else 1}, "{m}"}}'
        if op == 'poke':
            m = w.pop(1) if w[1] in MEM else 'bus'
            vals = ', '.join(str(num(x)) for x in ','.join(w[2:]).split(',') if x)
            return f'{{"poke", "{MEM[m]}", {addr(w[1])}, {{{vals}}}}}'
        if op == 'dump':
            return f'{{"dump", "{mem(w[1])}", {addr(w[2])}, {num(w[3])}, {lua_str(w[4])}}}'
        if op == 'write':
            return f'{{"write", "{mem(w[1])}", {addr(w[2])}, {lua_str(hostpath(w[3], win))}}}'
        if op == 'trace':
            if w[1] not in ('read', 'write', 'exec'):
                raise SystemExit(f'mesen: trace kind {w[1]!r}: use read, write or exec')
            peek = w[5].split(':') if len(w) > 5 else ['0', '0']
            return (f'{{"trace", "{w[1]}", {addr(w[2])}, {addr(w[3])}, {num(w[4]) if len(w) > 4 else 2000}, '
                    f'{addr(peek[0])}, {num(peek[1])}}}')
        if op == 'untrace':
            return '{"untrace"}'
        if op == 'regs':
            return f'{{"regs", {lua_str(w[1])}, {lua_str(w[2])}}}'
        if op == 'autoplay':
            kv = ', '.join(f'[{lua_str(k)}] = {lua_str(v)}' for k, _, v in (a.partition('=') for a in w[3:]))
            return f'{{"autoplay", {num(w[1])}, {lua_str(hostpath(w[2], win))}, {{{kv}}}}}'
        if op == 'onexec':
            vals = ', '.join(str(num(x)) for x in w[3].split(','))
            return f'{{"onexec", {addr(w[1])}, {addr(w[2])}, {{{vals}}}}}'
        if op == 'until':
            return f'{{"until", {addr(w[1])}, {num(w[2])}, {num(w[3]) if len(w) > 3 else 600}}}'
    except (IndexError, ValueError) as e:
        raise SystemExit(f'mesen: bad step {line!r} ({e}); see mesen.py --help')
    raise SystemExit(f'mesen: unknown step {line!r}; see mesen.py --help')


def ensure_settings(mesen):
    """Portable mode: settings.json next to Mesen must allow Lua I/O and have a controller plugged in.
    Adds just those two to an existing file (the GUI's other settings stay)."""
    s = mesen.parent / 'settings.json'
    section, port_name = CONSOLE['section']
    if not s.exists():
        s.write_text(json.dumps({'Debug': {'ScriptWindow': {'AllowIoOsAccess': True}},
                                 section: {port_name: {'Type': CONSOLE['controller']}}}, indent=2) + '\n')
        return
    try:
        d = json.loads(s.read_text(encoding='utf-8-sig'))
    except ValueError as e:
        sys.exit(f'mesen: {s} is not valid JSON ({e}); fix or delete it (this writes a minimal one)')
    sw = d.setdefault('Debug', {}).setdefault('ScriptWindow', {})
    port = d.setdefault(section, {}).setdefault(port_name, {})
    if sw.get('AllowIoOsAccess') is True and port.get('Type') == CONSOLE['controller']:
        return
    sw['AllowIoOsAccess'] = True
    port['Type'] = CONSOLE['controller']
    s.write_text(json.dumps(d, indent=2) + '\n', encoding='utf-8')
    print(f'mesen: {s}: allowed Lua I/O and plugged in a controller')


def clean_steps(steps):
    steps = [s.split('#')[0].strip() for s in steps]
    return [s for s in steps if s]


def script(steps, out, states, max_frames, win=True):
    """The Lua program for the steps (out/states: folders, already created)."""
    sep = '\\' if win else '/'
    return LUA_HEAD % {'out': lua_str(hostpath(out, win) + sep), 'states': lua_str(hostpath(states, win) + sep),
                       'steps': '{' + ',\n  '.join(compile_step(s, win) for s in steps) + '}',
                       'maxf': max_frames, 'regs': CONSOLE['regs'], 'width': CONSOLE['width'],
                       'cpu': CONSOLE['cpu'], 'bus': CONSOLE['bus'], 'prg': CONSOLE['prg'], 'top': CONSOLE['top']}


def run(steps, rom=None, out=None, max_frames=200000, quiet=False, states=None, mesen=None, timeout=None,
        dry_run=False):
    """Run the steps; returns the exit status (0 = all steps done, 2 = frame limit, 124 = timeout)."""
    mesen = find_mesen(mesen)
    win = is_windows_exe(mesen)
    out = Path(out or paths.WORK / 'mesen').resolve()
    out.mkdir(parents=True, exist_ok=True)
    states = Path(states).resolve() if states else out / 'states'
    states.mkdir(parents=True, exist_ok=True)
    for old in ('trace.txt', 'peek.txt'):
        if (out / old).exists():
            (out / old).unlink()
    rom = Path(rom or paths.ROM).resolve()
    if not rom.is_file():
        sys.exit(f'mesen: no ROM at {paths.show(rom)}; give --rom FILE')
    lua = out / 'run.lua'
    lua.write_text(script(clean_steps(steps), out, states, max_frames, win))
    if dry_run:
        print(f'mesen: wrote {paths.show(lua)}')
        return 0
    ensure_settings(mesen)
    if CONSOLE['cpu'] == 'gba' and not (mesen.parent / 'Firmware' / 'gba_bios.bin').is_file():
        sys.exit(f'mesen: no {mesen.parent / "Firmware" / "gba_bios.bin"}: without a BIOS a GBA game stops at its first SWI '
                 'and the screen stays black. Use your own dump, or bios.bin from https://github.com/Cult-of-GBA/BIOS (MIT)')
    # Mesen logs every uninitialised read: keep the other lines (Lua errors) in OUT/mesen.log
    p = subprocess.Popen([str(mesen), '--testrunner', hostpath(rom, win), hostpath(lua, win)], cwd=mesen.parent,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors='replace')
    errors, killed = [], []
    timer = None
    if timeout:
        import threading

        def kill():
            killed.append(1)
            p.kill()
            if win:   # killing the WSL side leaves Mesen.exe running: stop it by its script path
                subprocess.run(['powershell.exe', '-NoProfile', '-Command',
                                "Get-CimInstance Win32_Process -Filter \"Name='Mesen.exe'\" | Where-Object "
                                "{ $_.CommandLine -like '*" + hostpath(lua, win).replace("'", "''") + "*' } | "
                                "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"],
                               capture_output=True)
        timer = threading.Timer(timeout, kill)
        timer.start()
    with open(out / 'mesen.log', 'w') as log:
        for line in p.stdout:
            if 'ninitialized' not in line and 'ninitialised' not in line:
                log.write(line)
                if 'error' in line.lower() or '.lua:' in line:
                    errors.append(line.rstrip())
    code = p.wait()
    if timer:
        timer.cancel()
    if killed:
        code = 124
    if not quiet:
        for e in errors[:10]:
            print(f'mesen: {e}')
        peek = out / 'peek.txt'
        if peek.exists():
            sys.stdout.write(peek.read_text())
        note = {2: ' (frame limit)', 124: ' (timeout)',
                255: ' (Mesen ended the run: past ~35,000 frames, a crash, or a savestate in a bad spot)'}
        print(f'mesen: exit {code}{note.get(code, "")}, output in {paths.show(out)}')
    return code


def main(argv=None):
    argv = paths.configure(sys.argv[1:] if argv is None else argv)   # takes --rom, --root, --build
    out = states = mesen = timeout = None
    maxf = 200000
    dry = False
    steps = []
    it = iter(argv)
    try:
        for a in it:
            if a == '--out':
                out = next(it)
            elif a == '--states':
                states = next(it)
            elif a == '--max-frames':
                maxf = int(next(it))
            elif a == '--timeout':
                timeout = float(next(it))
            elif a == '--mesen':
                mesen = next(it)
            elif a == '--dry-run':
                dry = True
            elif a == '--file':
                steps += Path(next(it)).read_text().splitlines()
            elif a in ('-h', '--help'):
                print(__doc__ + '\n' + paths.FOLDER_HELP)
                return 0
            else:
                steps.append(a)
    except StopIteration:
        sys.exit(f'mesen: {a} needs a value; see mesen.py --help')
    if not clean_steps(steps):
        sys.exit(__doc__)
    sys.exit(run(steps, paths.ROM, out, maxf, states=states, mesen=mesen, timeout=timeout, dry_run=dry))


if __name__ == '__main__':
    main()
