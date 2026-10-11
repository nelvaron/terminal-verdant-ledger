# Apple Terminal Profile

This document describes the `Verdant Ledger Light` profile for Apple Terminal.

## Overview

The profile adapts the [Verdant Ledger Light VS Code theme](https://github.com/nelvaron/vscode-verdant-ledger) for Apple's built-in Terminal app. It uses a pale green-gray background, deep evergreen text, a green cursor, and a restrained set of ANSI colors.

- **Profile name:** `Verdant Ledger Light`
- **Profile file:** [`profiles/Verdant-Ledger-Light.terminal`](../profiles/Verdant-Ledger-Light.terminal)
- **Background:** `#F6F8F6`
- **Foreground:** `#1B2320`
- **Cursor:** `#2D6A3B`
- **Selection:** `#D5E1D8`
- **Window size:** 100 × 30, unlimited scrollback
- **Font used in visual validation:** SF Mono Terminal Regular, 13 pt
- **Shell used for functional checks:** zsh

## Color palette

| ANSI color | Hex | Contrast against `#F6F8F6` |
|---|---|---:|
| Black | `#1B2320` | 15.04:1 |
| Red | `#8A2621` | 8.27:1 |
| Green | `#2D6A3B` | 6.08:1 |
| Yellow | `#8A6408` | 5.04:1 |
| Blue | `#3D5F7A` | 6.31:1 |
| Magenta | `#7A4A6E` | 6.49:1 |
| Cyan | `#2F6B6B` | 5.73:1 |
| White | `#5D6864` | 5.42:1 |
| Bright black | `#66716D` | 4.74:1 |
| Bright red | `#B8443A` | 5.01:1 |
| Bright green | `#3A7D4A` | 4.67:1 |
| Bright yellow | `#8F6809` | 4.74:1 |
| Bright blue | `#4A6E8E` | 5.03:1 |
| Bright magenta | `#8D5A80` | 5.04:1 |
| Bright cyan | `#367878` | 4.78:1 |
| Bright white | `#52635A` | 5.98:1 |

The palette lives in [`scripts/palette.json`](../scripts/palette.json). Every value except bright white matches the `terminal.*` colors of the VS Code theme.

Contrast ratios are calculated against the specified profile background. They are useful indicators, but perceived readability also depends on display settings and font rendering.

### Selection

VS Code paints the terminal selection as forest green at 20% opacity (`#2D6A3B33`), which comes to about `#CEDCD1` on this background. The profile uses the slightly lighter `#D5E1D8`, the theme's "20% forest green over white" tint, so every ANSI color keeps at least 3.7:1 contrast while selected.

### Bright white adjustment

The original palette's `#8C9894` bright-white value has a contrast ratio of approximately 2.80:1 on `#F6F8F6`. This Terminal profile uses `#52635A` instead, raising the contrast to approximately 5.98:1. The adjustment is local to this Apple Terminal profile; the VS Code theme is unchanged.

## Install

1. Download [`Verdant-Ledger-Light.terminal`](../profiles/Verdant-Ledger-Light.terminal).
2. Open the file to import it, or use **Terminal → Settings → Profiles** and the profile actions menu.
3. Select **Verdant Ledger Light** for a new window.
4. To use it automatically for new windows, choose it as the default profile in **Terminal → Settings → General**.

Menu labels may vary slightly between macOS releases.

## Changing the profile

Terminal stores every color as a binary `NSKeyedArchiver` archive of an `NSColor`, embedded as base64 in the XML plist. A single missing character makes the whole file unreadable, so never edit the `.terminal` file by hand:

1. Change the colors in [`scripts/palette.json`](../scripts/palette.json), or other settings in [`scripts/generate_profile.py`](../scripts/generate_profile.py).
2. Regenerate the profile with `python3 scripts/generate_profile.py`.
3. Update the palette table above, including the contrast ratios. The tests compare it with the palette.
4. Run the tests, then import the profile on macOS and check it visually.

## Validation

The repository includes an automated test suite for the profile plist and color archives:

```sh
python3 -m unittest discover -s tests -v
```

These tests verify that:

- the file parses as a plist and every color archive decodes;
- the profile matches `scripts/palette.json` and the generator output (`python3 scripts/generate_profile.py --check`);
- the text and all 16 ANSI colors reach 4.5:1 on the background and 3.5:1 on the selection, and the cursor reaches 3:1;
- the palette table in this document matches the profile.

GitHub Actions runs the tests on Ubuntu, and on macOS lints the plist with `plutil` and decodes every color with AppKit's `NSKeyedUnarchiver` into an `NSColor`. Automated tests do not emulate Apple's Terminal UI, so a manual import and visual smoke test on macOS remains required.

### Demo session

[`scripts/demo.sh`](../scripts/demo.sh) prints the session shown in the README preview: the 16 ANSI colors, text styles, `git status`, `git diff`, `git log`, and a colored `ls`. It works in a temporary Git repository and removes it afterwards:

```sh
sh scripts/demo.sh
```

To capture a window screenshot on macOS, press **Shift-Command-4**, then **Space**, and click the Terminal window.

### ANSI color swatches

Run this in zsh to display all 16 standard ANSI colors as background swatches:

```zsh
for i in {0..15}; do
  printf '\e[48;5;%sm  %2s  \e[0m' "$i" "$i"
  (( (i + 1) % 8 == 0 )) && printf '\n'
done
```

### Text styles and status colors

```zsh
printf '\e[0mNormal  \e[1mBold\e[0m  \e[2mDim\e[0m  \e[3mItalic\e[0m  \e[4mUnderline\e[0m\n'
printf '\e[32mSuccess\e[0m  \e[33mWarning\e[0m  \e[34mInfo\e[0m  \e[31mError\e[0m\n'
```

## Visual validation results

The profile was imported successfully into Apple Terminal and checked in a zsh window.

- The 16 ANSI colors were distinguishable in the provided swatches.
- Foreground and background appeared readable.
- Bold, dim, italic, and underline styles rendered.
- Success, warning, information, and error colors were distinguishable.
- The green cursor was clearly visible.

These checks were made before the profile file was regenerated by `scripts/generate_profile.py`; the colors are unchanged, but repeat the import and smoke test to confirm the regenerated file.

The validated configuration used SF Mono Terminal Regular, 13 pt. Menlo Regular, 13 pt, was also found readable, but is not required.

## Scope

This repository provides an Apple Terminal profile. It does not modify zsh configuration, prompts, aliases, shell scripts, or other dotfiles. The VS Code theme remains in its separate [repository](https://github.com/nelvaron/vscode-verdant-ledger).
