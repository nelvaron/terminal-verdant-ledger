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

| ANSI color | Hex | Contrast against `#F6F8F6` | VS Code theme |
|---|---|---:|---|
| Black | `#1B2320` | 15.04:1 | same |
| Red | `#651916` | 11.55:1 | `#8A2621` |
| Green | `#236032` | 7.05:1 | `#2D6A3B` |
| Yellow | `#6F4F01` | 7.04:1 | `#8A6408` |
| Blue | `#375873` | 7.01:1 | `#3D5F7A` |
| Magenta | `#744569` | 7.03:1 | `#7A4A6E` |
| Cyan | `#205D5E` | 7.06:1 | `#2F6B6B` |
| White | `#5D6864` | 5.42:1 | same |
| Bright black | `#66716D` | 4.74:1 | same |
| Bright red | `#B8443A` | 5.01:1 | same |
| Bright green | `#3A7D4A` | 4.67:1 | same |
| Bright yellow | `#986702` | 4.60:1 | `#8F6809` |
| Bright blue | `#427698` | 4.60:1 | `#4A6E8E` |
| Bright magenta | `#9B5B8D` | 4.60:1 | `#8D5A80` |
| Bright cyan | `#267C78` | 4.64:1 | `#367878` |
| Bright white | `#7F8A86` | 3.35:1 | `#8C9894` |

The palette lives in [`scripts/palette.json`](../scripts/palette.json). It follows the `terminal.*` colors of the VS Code theme, with the changes below so that every normal color can be told apart from its bright variant.

Contrast ratios are calculated against the specified profile background. They are useful indicators, but perceived readability also depends on display settings and font rendering.

### Normal and bright colors

Both halves of the palette need at least 4.5:1 on a light background, so they share a narrow band of lightness. In the VS Code palette, yellow and bright yellow differ by only 1.6 CIEDE2000 units, and cyan, blue, and magenta by 4.7 to 6.2, which makes them look identical in a terminal. The profile therefore uses two contrast levels:

- **Normal colors reach at least 7:1** (WCAG AAA). Green, yellow, blue, magenta, and cyan are slightly darker versions of the theme colors.
- **Bright colors sit near 4.6:1** (WCAG AA). They stay within a few degrees of the hue of their normal color and are a little more saturated; bright red and bright green are unchanged.

Every normal and bright pair now differs by at least 10 CIEDE2000 units.

Red is darkened further, to 11.55:1. With red-green color blindness, red and ochre look alike and only lightness separates them; the theme's design keeps red darker than the ochre for that reason. After simulating deuteranopia, the profile's red and yellow differ by 12.0 CIEDE2000 units, matching the theme's 11.9.

### Grays

Black, white, bright black, and bright white form a ladder from dark to light. Bright white is `#7F8A86` (3.35:1), the tint the theme uses for input borders and ghost text, one step darker than the theme's own bright white `#8C9894` (2.80:1). It is the lightest gray, as programs expect when they print bright white on colored backgrounds, and it remains legible as plain text. Earlier versions of this profile used `#52635A`, which was darker than white and bright black.

### Selection

VS Code paints the terminal selection as forest green at 20% opacity (`#2D6A3B33`), which comes to about `#CEDCD1` on this background. The profile uses the slightly lighter `#D5E1D8`, the theme's "20% forest green over white" tint, so every ANSI color except bright white keeps at least 3.6:1 contrast while selected.

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

These checks were made with the earlier palette, before the normal and bright colors were separated. The screenshot that prompted that change showed the profile importing and rendering correctly; repeat the smoke test with the current palette.

The validated configuration used SF Mono Terminal Regular, 13 pt. Menlo Regular, 13 pt, was also found readable, but is not required.

## Scope

This repository provides an Apple Terminal profile. It does not modify zsh configuration, prompts, aliases, shell scripts, or other dotfiles. The VS Code theme remains in its separate [repository](https://github.com/nelvaron/vscode-verdant-ledger).
