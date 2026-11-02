# Zen Nippon Pro Wrestling - Fight da Pon — English Translation

An English translation patch for **Zen Nippon Pro Wrestling - Fight da Pon**, 1994, SNES, released only in Japan.

It covers the whole game: all 861 lines of story dialogue, the 42 card labels, wrestler names,
menus and prompts. The original's fixed Japanese text is replaced by a new variable-width English
font, and the ROM is expanded to 16 Mbit to hold the text.

**[See screenshots](docs/SCREENSHOTS.md)** of the patched game.

> **Status: complete.** Every story mode and screen has been played through in Mesen; please report
> any problems ([how to report](#reporting-problems)). [CHANGELOG.md](CHANGELOG.md) lists what's in
> each release.

## Downloads

Get the latest zip from the [Releases](../../releases) page. It contains two patches. Pick one and apply it to the original game; they don't stack:

| Patch | What you get |
|---|---|
| **Zen Nippon Pro Wrestling - Fight da Pon (English)** | The translation, with the game otherwise unchanged. |
| Zen Nippon Pro Wrestling - Fight da Pon (English) (Debug Menu) | The same, plus the developers' debug menu, which the original game has switched off: hold X and press Select on any screen. Several of its entries show corrupted graphics, as they do in the original code. It's for the curious, not for playing through. Checked in automated emulator runs, not yet played by hand. |

## How to patch

**[Follow the step-by-step guide](docs/HOW_TO_PATCH.md).** You apply the `.bps` patch with
[Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) in a web browser, or with
[Flips](https://github.com/Alcaro/Flips).

You need your own copy of the original Japanese game. ROM images are not provided here.

- Game: *Zen Nippon Pro Wrestling - Fight da Pon* (Japan), serial SHVC-JF.
- The image must match: `Zennihon Pro Wrestling - Fight da Pon! (J).smc`, 1048576 bytes, CRC32 `379645bd`,
  SHA-1 `52aa5ce4612b81c90fd07f6c3dc9a712afb32668`.

Tested in Mesen.

## Notes for players

- **Names.** Wrestlers keep their real names. The villains' names are this translation's own.
- **What's still in Japanese.** The title logo, the copyright line and the staff credits.
- **Saves.** The game has no battery save: it gives you a password instead.
- **Bug fixes.** The patch also fixes two bugs of the original game: a portrait drawn over a
  wrestler's sprite, and a gauge left on screen before a scene's first line.
- **Hidden content.** See [docs/HIDDEN_CONTENT.md](docs/HIDDEN_CONTENT.md).
- **Player's guide.** [The guide](https://kactusken.github.io/Zen-Nippon-Pro-Wrestling-Fight-da-Pon-English/guide/) covers matches, every card and wrestler, maps of all seven boards, passwords and secrets.

## Reporting problems

Open an [issue](../../issues) with:

- a screenshot,
- which patch you used,
- where you were: the mode and menu, or roughly what had just happened.

Text that is cut off, overlaps, or still shows Japanese is especially helpful.

## For ROM hackers and contributors

Everything needed to rebuild the patches from the original ROM is in this repository: the
translated text, the patching code (Python 3, no dependencies for the build) and documentation of
the game's formats and rules.

| Document | What's in it |
|---|---|
| [docs/HOW_TO_PATCH.md](docs/HOW_TO_PATCH.md) | The simplest way to patch your game, with no renaming |
| [docs/BUILDING.md](docs/BUILDING.md) | Setting up, building, making patches, and the checking tools |
| [docs/TRANSLATION.md](docs/TRANSLATION.md) | Text file formats, scope, style guide, glossary, and naming decisions |
| [docs/EDITING.md](docs/EDITING.md) | Editing the in-game text graphics |
| [docs/PATCHES.md](docs/PATCHES.md) | How each code patch works |
| [docs/TECHNICAL.md](docs/TECHNICAL.md) | The game's ROM layout, data formats, and memory map |
| [docs/guide/](docs/guide/index.html) | Source of the [player's guide](https://kactusken.github.io/Zen-Nippon-Pro-Wrestling-Fight-da-Pon-English/guide/), with its data filled by `tools/guidedata.py` |
| [docs/MATCHES.md](docs/MATCHES.md) | How matches work: cards, gauges and the rules behind them |
| [docs/STORY.md](docs/STORY.md) | How the story mode works, with every chapter and board |
| [docs/PLATFORM.md](docs/PLATFORM.md) | SNES pitfalls for this kind of work |
| [docs/HIDDEN_CONTENT.md](docs/HIDDEN_CONTENT.md) | Unlockables, debug features, and unused and cut content |
| [tools/README.md](tools/README.md) | Every tool, what it's for and how to run it |

Quick start:

```sh
python3 tools/extract.py                 # unpack the ROM in rom/ into extracted/
python3 build.py                         # -> build/Zen Nippon Pro Wrestling - Fight da Pon (English).smc
python3 make_patches.py --version v1.0   # -> release/*.bps and a zip
```

## AI disclosure

AI assisted with the translation.

## Legal

This is a non-commercial fan translation, not affiliated with or endorsed by the game's developers
or publishers. It contains no copyrighted game data that would let
anyone play without owning the game. The patches only work on your own copy of the game.
Zen Nippon Pro Wrestling - Fight da Pon and its contents belong to their respective owners. The Japanese text in this
repository is included for translation and reference.

The code in this repository is released under the [MIT License](LICENSE).
