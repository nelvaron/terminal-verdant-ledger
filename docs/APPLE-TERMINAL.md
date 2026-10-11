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

Contrast ratios are calculated against the specified profile background. They are useful indicators, but perceived readability also depends on display settings and font rendering.

### Bright white adjustment

The original palette's `#8C9894` bright-white value has a contrast ratio of approximately 2.80:1 on `#F6F8F6`. This Terminal profile uses `#52635A` instead, raising the contrast to approximately 5.98:1. The adjustment is local to this Apple Terminal profile; the VS Code theme is unchanged.

## Install

1. Download [`Verdant-Ledger-Light.terminal`](../profiles/Verdant-Ledger-Light.terminal).
2. Open the file to import it, or use **Terminal → Settings → Profiles** and the profile actions menu.
3. Select **Verdant Ledger Light** for a new window.
4. To use it automatically for new windows, choose it as the default profile in **Terminal → Settings → General**.

Menu labels may vary slightly between macOS releases.

## Validation

The repository includes an automated test suite for the profile plist and color archives:

```sh
python3 -m unittest discover -s tests -v
```

These tests verify that the file parses as a plist, the profile identity and key colors are present, and all 16 ANSI values match the documented palette. Automated tests do not emulate Apple's Terminal UI, so a manual import and visual smoke test on macOS remains required.

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

The validated configuration used SF Mono Terminal Regular, 13 pt. Menlo Regular, 13 pt, was also found readable, but is not required.

## Scope

This repository provides an Apple Terminal profile. It does not modify zsh configuration, prompts, aliases, shell scripts, or other dotfiles. The VS Code theme remains in its separate [repository](https://github.com/nelvaron/vscode-verdant-ledger).
