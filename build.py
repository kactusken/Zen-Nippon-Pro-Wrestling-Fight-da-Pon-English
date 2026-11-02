#!/usr/bin/env python3
"""Build the translated image from the original. Standard library only.

  python3 build.py [--name NAME] [--unlocks all|none|GROUP,...] [--clean]
      -> build/NAME.<ext> (default NAME: "<game> (English)")

Steps (default folders shown; move any of them with the folder options - see --help):
  1. verify the original in rom/ (size + SHA-1; --skip-verify skips the hash)
  2. prepare build/NAME: a fresh copy of the original, or - much faster for big images - the last
     build with every range it wrote restored from the original (tools/image.py; --clean copies)
  3. text: translation/script/ and translation/text/ into the game's files (TEXT_STEPS)
  4. code patches picked by --unlocks (CODE_PATCHES, tools/codepatch.py; debug-* groups only when named)
  5. images: for every catalogued image the English file the catalogue picks (hand-made >
     approved > rendered), imported by tools/gfx.py; the final set is copied to review/images-english/
  6. write every changed file back into the image (files that fit in place first)

Two name sets (e.g. real wrestlers' names and the game's parody names, two releases): fill
NAME_SETS; --names picks one (default the first) and text steps read NAMES. Names are written as
tokens in translation/ (`<Name>`) that the project's names tool resolves per set (Fire Pro
Wrestling S tools/names.py, D tools/fpdtext.py); lint's NAME_TOKEN checks them.

Test builds: --boot PART starts the game straight in PART (BOOT_PATCHES, once known);
--no-translation skips text and images, and gameplay patches unless --unlocks is given - on its
own the result is byte-identical to the original (tools/check.py --control proves it).
Developer flags (never for releases): --no-text FILE skips one text file.
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / 'tools'))
import catalog  # noqa: E402
import codepatch  # noqa: E402
import disc  # noqa: E402
import gfx  # noqa: E402
import image  # noqa: E402
import paths  # noqa: E402
import script  # noqa: E402
import cards  # noqa: E402
import title  # noqa: E402

NEW_1AC4 = bytes.fromhex('220000D1' 'A910008D1008' 'AD1208' '490100' '8D1208' '60'
                         # code $0E: $D10010 follows the jump, then back to the reader ($C0:1956), so the
                         # message's first byte goes in this same tick. The end test at $C0:4379 looks at the
                         # byte before the pointer; right after a bare jump that is the last message's end code.
                         '221000D1' '4C5619' '60')
ORIG_1AC4 = bytes.fromhex('0A0A0A0A0AAAA910008D1008AD0208186D0408A8A900E08510A97E00')[:len(NEW_1AC4)]

# Gameplay patches: (group, file, address, original, new, description) - see tools/codepatch.py.
# Groups named debug-* are developer extras (debug menus, cheat windows): never in "all" or the
# default, only when named, never in a release variant.
TEXT_READS = [0xC01959, 0xC01A67, 0xC01A7F, 0xC01A97, 0xC0437D]   # LDA $C40000,X -> LDA $D00000,X
CODE_PATCHES = [
    ('english', '/rom.sfc', a, bytes.fromhex('BF0000C4'), bytes.fromhex('BF0000D0'), None) for a in TEXT_READS
] + [
    # the glyph drawing goes to the renderer in bank $D1 (tools/asm/vwf.asm); the bytes after it
    # hold the jump code $0E, added to the control code table at $C0:196C
    ('english', '/rom.sfc', 0xC01AC4, ORIG_1AC4, NEW_1AC4, 'variable-width text'),
    ('english', '/rom.sfc', 0xC01988, bytes.fromhex('7F1A'), bytes.fromhex('D81A'), 'jump code'),
    # game bug: portrait tick before a scene's first line drew over the first wrestler's sprite (docs/TECHNICAL.md)
    ('english', '/rom.sfc', 0xC0E0E6, bytes.fromhex('A5348902 00'.replace(' ', '')), bytes.fromhex('221400D1EA'), 'portrait before the first line'),
    # the name code reads the English names in bank $D1
    ('english', '/rom.sfc', 0xC01995, bytes.fromhex('BF753DC0'), bytes.fromhex('BF8014D1'), None),
    ('english', '/rom.sfc', 0xC0199E, bytes.fromhex('BF0200C0'), bytes.fromhex('BF0200D1'), None),
    # scenario bubble: draw with the renderer; its tilemap counts 22 cells ($C0:1AE0 sets the pointer)
    ('english', '/rom.sfc', 0xC044E1, bytes.fromhex('48DAA20000'), bytes.fromhex('220400D160'), 'scenario bubble'),
    ('english', '/rom.sfc', 0xC0452C, bytes.fromhex('20B344'), bytes.fromhex('20E01A'), None),
    ('english', '/rom.sfc', 0xC01AE0, bytes.fromhex('8512BF1CC0C82900FF09FF'), bytes.fromhex('A9000B8500A9D100850260'), None),
    # the wrestler list: same names, drawn by the renderer into the cells their record counts
    ('english', '/rom.sfc', 0xC04169, bytes.fromhex('BF753DC0'), bytes.fromhex('BF8014D1'), None),
    ('english', '/rom.sfc', 0xC0416F, bytes.fromhex('A9C000'), bytes.fromhex('A9D100'), None),
    ('english', '/rom.sfc', 0xC041C5, bytes.fromhex('206641A700AA186518'), bytes.fromhex('220C00D1FA68606518'), 'wrestler list'),
    # the battle name bars read bank $D1
    ('english', '/rom.sfc', 0xC015AE, bytes.fromhex('BF2F14C0'), bytes.fromhex('BF0017D1'), None),
    ('english', '/rom.sfc', 0xC015B8, bytes.fromhex('A9C000'), bytes.fromhex('A9D100'), None),
    # password prompts
    ('english', '/rom.sfc', 0xC051F9, bytes.fromhex('0AAABFCB4D'), bytes.fromhex('220800D160'), 'password prompts'),
    # name cell layouts ($C0:3D3D table: byte offsets of the cells of a name 1-6 cells wide). The original spread
    # 2 and 3 cells apart (4,16 / 4,10,16: one kana a cell); the renderer draws running text, so make them
    # contiguous and centred (Otasuke Select's names lost letters in the gaps)
    ('english', '/rom.sfc', 0xC03D4D, bytes.fromhex('04001000'), bytes.fromhex('08000C00'), 'name layout 2 cells'),
    ('english', '/rom.sfc', 0xC03D51, bytes.fromhex('04000A001000'), bytes.fromhex('06000A000E00'), 'name layout 3 cells'),
    # developers' debug menu: the shipped game turned BEQ into BRA after the "hold X, press Select" test
    # in the main loop (docs/PATCHES.md, docs/HIDDEN_CONTENT.md). Released as its own variant, off by default
    ('dev-menu', '/rom.sfc', 0xC08A22, bytes.fromhex('8009'), bytes.fromhex('F009'), 'debug menu: hold X, press Select'),
]
ALWAYS_GROUPS = {'english'}               # in every translated build, not a choice (--unlocks ignores them): the English's own fixes
UNLOCK_GROUPS = sorted({p[0] for p in CODE_PATCHES} - ALWAYS_GROUPS)
PLAYER_GROUPS = [g for g in UNLOCK_GROUPS if not g.startswith('debug-')]
DEFAULT_GROUPS = set()  # without --unlocks: the extras ship as separate patches (make_patches.py VARIANTS)

# --boot: (part, file, address, original, new) - patches that start the game in a given part.
BOOT_PATCHES = {
}


def to_offset(name, addr):
    """File offset of a CPU address in the HiROM cart (banks $C0-$FF)."""
    return addr & 0x3FFFFF


# Text steps: (text file or folder under translation/, function(path, files)). Each inserts the
# English into the game's files through `files` and stops with a clear message if anything doesn't fit.
# Zero-padding files a grown file may take room from when the disc is full (PS2 disc.py
# take_from_padding: their end is cut off) - e.g. ['/DUMMY.DAT']; check they are all zeros.
PADDING_DONORS = []

# Name sets for the --names option, e.g. ('real', 'parody') - empty: one set, no option.
NAME_SETS = ()
NAMES = NAME_SETS[0] if NAME_SETS else None

TEXT_STEPS = [
    ('script/events.txt', script.build_step),
    ('text/cards.csv', cards.build_step),
    ('text/title.txt', title.build_step),
]


class Files:
    """The game's files for this build: read from the image on first use, written back at the end."""

    def __init__(self, d):
        self.d, self.data, self.changed = d, {}, set()

    def get(self, name):
        if name not in self.data:
            self.data[name] = bytearray(self.d.read_file(self.d.find(name)))
        return self.data[name]

    def put(self, name, data):
        self.data[name] = bytearray(data)
        self.changed.add(name)


def unlock_groups(value):
    if value == 'all':
        return set(PLAYER_GROUPS)
    if value == 'none':
        return set()
    groups = {g.strip() for g in value.split(',') if g.strip()}
    if groups - set(UNLOCK_GROUPS):
        raise argparse.ArgumentTypeError(f'expected all, none or some of {",".join(UNLOCK_GROUPS) or "(no groups yet)"}')
    return groups


def images_step(files):
    final = catalog.final_images()
    missing, changed, _ = catalog.stale()
    if missing or changed:
        print(f'note: {len(missing) + len(changed)} automatic renders are out of date - run tools/render.py '
              f'(building with the frozen files there are)')
    n = gfx.import_images({k: p for k, (tag, p) in final.items()}, files)
    if paths.ENGLISH_IMAGES.exists():
        shutil.rmtree(paths.ENGLISH_IMAGES)
    if final:
        paths.ENGLISH_IMAGES.mkdir(parents=True)
        for name, (tag, p) in final.items():
            dst = paths.ENGLISH_IMAGES / f'{name}.png'
            dst.parent.mkdir(parents=True, exist_ok=True)      # ids can be archive paths
            shutil.copyfile(p, dst)
        counts = {}
        for tag, _ in final.values():
            counts[tag] = counts.get(tag, 0) + 1
        print(f'images: {n} imported (' + ', '.join(f'{c} {t}' for t, c in sorted(counts.items())) + ')')


def verify_original(original):
    """SHA-1 of the original image, once: the result is remembered with the file's size and
    modification time (build/original.verified), so later builds only re-hash a changed file
    (a DVD image takes ~20 s to hash)."""
    st = original.stat()
    stamp = f'{original.resolve()} {st.st_size} {st.st_mtime_ns} {paths.ORIGINAL["sha1"]}'
    memo = paths.BUILD / 'original.verified'
    if memo.exists() and memo.read_text() == stamp:
        return
    print('verifying the original...')
    if image.sha1(original) != paths.ORIGINAL['sha1']:
        sys.exit(f'{original.name} does not match the expected SHA-1 {paths.ORIGINAL["sha1"]}')
    paths.BUILD.mkdir(parents=True, exist_ok=True)
    memo.write_text(stamp)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0], epilog=paths.FOLDER_HELP,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--name', default=f'{paths.GAME_FILE} (English)')
    ap.add_argument('--skip-verify', action='store_true', help="don't hash the original image")
    ap.add_argument('--clean', action='store_true', help='copy the original instead of restoring the last build')
    ap.add_argument('--no-translation', action='store_true', help='skip text and images (alone: identical to the original)')
    ap.add_argument('--unlocks', type=unlock_groups, metavar='all|none|GROUP,...',
                    help='gameplay patches: all (debug-* groups only when named), none or some groups (default: DEFAULT_GROUPS); '
                         'none with --no-translation')
    if NAME_SETS:
        ap.add_argument('--names', choices=NAME_SETS, default=NAME_SETS[0],
                        help=f'name set: {" or ".join(NAME_SETS)} (default {NAME_SETS[0]})')
    ap.add_argument('--boot', choices=sorted(BOOT_PATCHES), help='TEST BUILD: start the game in this part')
    ap.add_argument('--no-text', action='append', default=[], metavar='FILE',
                    help='developer: leave this text file untranslated (repeatable)')
    args = ap.parse_args(paths.configure(sys.argv[1:] if argv is None else argv))
    global NAMES
    NAMES = getattr(args, 'names', NAMES)
    if args.unlocks is None:
        args.unlocks = set() if args.no_translation else set(DEFAULT_GROUPS)

    original = paths.ROM
    if not original.exists():
        sys.exit(f'put the original image in {paths.show(paths.ROM_DIR)} (or pass --rom): {paths.ORIGINAL_NAME}')
    if original.stat().st_size != paths.ORIGINAL['size']:
        sys.exit(f'{original.name}: {original.stat().st_size} bytes, expected {paths.ORIGINAL["size"]} - not the right image')
    if not args.skip_verify:
        verify_original(original)

    out = paths.BUILD / (args.name + original.suffix)
    with image.prepare(original, out, clean=args.clean) as f:
        d = disc.Disc(f, writable=True)
        files = Files(d)

        if not args.no_translation:
            for rel, step in TEXT_STEPS:
                if rel in args.no_text:
                    print(f'text: skipped {rel} (--no-text)')
                    continue
                step(paths.TRANSLATION / rel, files)

        codepatch.apply(files, CODE_PATCHES, set(args.unlocks) | (set() if args.no_translation else ALWAYS_GROUPS), to_offset)

        if not args.no_translation:
            images_step(files)

        if args.boot:
            codepatch.apply(files, [(args.boot, *p, f'TEST BUILD: boots into {args.boot}') for p in BOOT_PATCHES[args.boot]],
                            {args.boot}, to_offset)

        def fits(name):
            return (len(files.data[name]) + disc.SECTOR - 1) // disc.SECTOR <= d.allocated_sectors(d.find(name))
        for name in sorted(files.changed, key=lambda n: (not fits(n), n)):  # fixed order: same disc layout every build
            d.write_file(d.find(name), bytes(files.data[name]), relocate=True,
                         **({'donors': PADDING_DONORS} if PADDING_DONORS else {}))
            print(f'patched {name}')
    disc.companion_files(out, original)
    print(f'done: {paths.show(out)}  ({len(files.changed)} files patched)')
    return out


if __name__ == '__main__':
    main()
