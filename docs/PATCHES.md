# Patches

What the build changes besides text and images, one section per patch: what the original code
does, what changed, why it works, the tool that makes it, limits to respect, and whether it was
*verified in game*.

## dev-menu
Released as the separate `(English) (Debug Menu)` patch, off in the main one; `build.py --unlocks dev-menu` builds it.

**The original:** the main loop tests hold X + press Select at $C0:8A14, then `BIT #$2000` / `BRA $8A2D` at $C0:8A22 skips the
code that opens the debug menu ($38=1, $3A=0, $3C=0) whatever the result.

**The change:** one byte, $80 to $F0, so the branch is the `BEQ` the test was written for.

**Why it works:** the bytes after the branch are intact, and the offset needs no change.

**Limits:** the menu opens over any screen and rows assume setup they don't do, so several show corrupted graphics
([HIDDEN_CONTENT.md](HIDDEN_CONTENT.md#debug-menu)). That's the original code, not this patch.

**Verified:** *seen headless* (2026-11-02) on the original plus the byte and on the English build: the write to $3A comes from C0:8A2B
on the press. Not yet tried in game by hand.
