# How to Patch Zen Nippon Pro Wrestling - Fight da Pon

You apply one patch to your ROM in a web browser, then open the new file in an emulator.

## What you need

- **Your own copy of the Japanese game:** a ROM file with these details:
  - Name: `Zennihon Pro Wrestling - Fight da Pon! (J).smc` (yours may be named differently)
  - Size: 1048576 bytes, with no copier header
  - CRC32: `379645bd`
- **The patch:** download the zip from the [Releases](../../../releases) page and unzip it.
- **A patcher:** [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/) runs in your web
  browser, so there is nothing to install. [Flips](https://github.com/Alcaro/Flips) also works.

## Steps

1. Open [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/).
2. Under **ROM file**, choose your original game.
3. Under **Patch file**, choose `Zen Nippon Pro Wrestling - Fight da Pon (English).bps`.
4. Click **Apply patch** and save the new file. It can have any name.
5. Open the new file in your emulator. It has been tested in Mesen.

## If it goes wrong

| What you see | Likely cause | Fix |
| --- | --- | --- |
| The patcher says the checksum or the source file is wrong | The ROM is already patched, is a different dump, or has a copier header | Start again from a clean ROM with the size and CRC32 above |
| The game is still in Japanese | You opened the original file | Open the new, patched file |
