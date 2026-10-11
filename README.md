# Verdant Ledger for Apple Terminal

A light Apple Terminal profile adapted from the [Verdant Ledger Light theme for Visual Studio Code](https://github.com/nelvaron/vscode-verdant-ledger).

## Profile

- **Profile:** `Verdant Ledger Light`
- **File:** [`profiles/Verdant-Ledger-Light.terminal`](profiles/Verdant-Ledger-Light.terminal)
- **Background:** `#F6F8F6`
- **Foreground:** `#1B2320`
- **Cursor:** `#2D6A3B`
- **Selection:** `#D5E1D8`
- **Font used during visual validation:** SF Mono Terminal Regular, 13 pt
- **Shell tested:** zsh

The `Bright White` ANSI entry is adjusted to `#52635A` for better contrast against the light background. This change applies only to this Terminal profile; it does not alter the [original VS Code theme](https://github.com/nelvaron/vscode-verdant-ledger).

## Install

1. Download `profiles/Verdant-Ledger-Light.terminal`.
2. Open the file, or import it from **Terminal → Settings → Profiles**.
3. Select **Verdant Ledger Light** for a window. Set it as the default profile in **Terminal → Settings → General** only if desired.

## Validate

The automated test checks the outer plist, required profile settings, all 16 ANSI color archives, and their RGB values. It does not emulate Apple's Terminal GUI or replace a visual import test on macOS.

Run with Python 3:

```sh
python3 -m unittest discover -s tests -v
```

A macOS visual smoke test is still required after importing: inspect the background, text, ANSI colors, text styles, selection, and cursor in Apple Terminal. The manual commands and detailed palette are in [`docs/APPLE-TERMINAL.md`](docs/APPLE-TERMINAL.md).
