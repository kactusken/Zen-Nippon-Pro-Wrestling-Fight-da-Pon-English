# Translation

## Where the text is

| File | Holds | Checked by |
|---|---|---|
| `translation/script/*.txt` | *(story/dialogue)* | `tools/lint.py` |
| `translation/text/*.txt`, `*.csv` | *(menus, names, ...)* | `tools/lint.py` |
| `translation/graphics.csv` | images with text | `tools/check.py` |

## File formats

Message blocks: `@ id`, source lines (`JP `), translation lines (`EN `); no `EN` lines = original
kept. A file's header says what it holds and its limits (`# limit lines=3 chars=28` is checked by
lint). Tables: original columns beside English ones (`japanese`/`english`, or `X`/`en_X`). See
`tools/blocks.py` and `tools/textdb.py`.

Control codes: *(list them here as they're found, e.g. `{name}` = player name)*.

## Style guide

- Name order, romanization: *(decide)*
- Quotes, ellipses, speaker labels, continuation-line indent: *(decide)*
- Voice and register per character type: *(decide)*
- Line and box limits: *(pixels / letters per screen)*

House style: the build wraps English to the 176 px box, two lines; each character keeps a verbal
tic (zumida, Weee!, y'know, usa, kuma, Poh!). Only ASCII and the ellipsis have glyphs.

## Glossary

`translation/glossary.csv` (`japanese, english, notes`): lint warns when a source line contains a
term and the English doesn't use its translation (several accepted forms: `A | B`). Prefer
established community names (existing English guides) over new coinages.

## Decisions

| Decision | Who / why |
|---|---|
| Wrestler names are the real wrestlers' names | Owner, 2026-11-01 |
| Card text is required, in text or in art | Owner, 2026-11-01 |
| Villain names as translated: Villains Inc., Black Wrestling Gang, Hyperspace Mask, Tutan Mask, Red Bear, Zebra Mask, Grand Director Spider Crab | Owner, 2026-11-02 |
| The foreign wrestlers' broken English and Izumida's "zumida" tic stay, as the Japanese has them | Owner, 2026-11-02 |
| Chapter 1 title stays "All Japan Pro Wrestling Roll Call!", which suits the story | Owner, 2026-11-02 |
| "Show by Shobai" stays the bare name, without "the TV quiz" | Owner, 2026-11-02 |
| "Champion" stays singular everywhere, including fa56 and fd85 | Owner, 2026-11-02 |
| Card labels stay abbreviated to fit 29 px (B.BUSTER, 16 MON, THROAT and the rest) | Owner, 2026-11-02 |
| Bold/Bald stands in for the ハゲしい/ハゲ pun at cf36, cf54, d852 | Owner, 2026-11-02 |
| Two bugs of the original game stay fixed in the English patches: a portrait drawn on a wrestler's sprite, and the gauge left on screen before a scene's first line | Owner, 2026-11-02 |
| USA Mask, not Usa Mask: a masked foreigner with USA on the head. The tic stays lowercase "usa" | Owner, 2026-11-02 |
| The restored debug menu ships as a separate `(English) (Debug Menu)` patch, not in the main one | Owner, 2026-11-02 |
| Zebra Mask stays documented only: no patch makes him fightable | Owner, 2026-11-02 |

## What stays untranslated

Staff credits, and game art that isn't critical to playing the game (the owner's call, 2026-11-01).
Art that carries information a player needs is translated.
