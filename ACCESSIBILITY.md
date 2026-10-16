# Accessibility

Verdant Ledger for Apple Terminal is a color profile, so its accessibility
work is about color: readable contrast, colors that can be told apart, and
honest documentation of where that falls short.

## Priorities

- **Readable text.** The foreground reaches 15.04:1 on the background. Every
  colored ANSI color (red, green, yellow, blue, magenta, cyan, normal and
  bright) reaches at least 4.5:1; the normal ones reach 7:1.
- **Distinct pairs.** Each bright color is clearly lighter than its normal
  color (at least 1.5 times the luminance contrast), so programs that use
  both remain readable.
- **Color blindness.** Red is kept much darker than yellow, so the two stay
  apart with red-green color blindness (12.0 CIEDE2000 units after simulating
  deuteranopia).
- **Readable selections.** Every ANSI color except bright white keeps at least
  3.6:1 on the selection color.
- **A visible cursor.** The green block cursor reaches 6.08:1.

The [palette notes](docs/APPLE-TERMINAL.md#color-palette) list every color
with its contrast ratio.

## Supported environments

- Terminal on macOS, imported from `profiles/Verdant-Ledger-Light.terminal`.
- Checked visually in zsh with SF Mono Terminal 13 pt.
- The profile does not set a font, so it keeps your font and size; you can
  enlarge text with **Command-+** or choose another font in the profile
  settings. Its colors do not affect VoiceOver, which reads Terminal's text.

## Known barriers

- **Bright white is paler than the other colors**, at 3.35:1 on the
  background and 2.65:1 on the selection. It is the lightest gray, which is
  what programs expect when they print bright white on colored backgrounds.
- **Magenta and cyan look alike with deuteranopia**: 2.7 CIEDE2000 units apart
  for the normal colors and 5.1 for the bright ones. Blue and magenta are
  5.9 apart. Output that tells these apart only by color can be hard to read.
- **There is only a light variant.** The profile has no dark or
  high-contrast version.
- **Programs can choose their own colors.** Colors from the 256-color or
  true-color palettes, and backgrounds that programs set, are outside the
  profile and are not checked.

## Reporting a barrier

[Open an issue](https://github.com/nelvaron/terminal-verdant-ledger/issues/new)
and mention accessibility in the title. It helps to include:

- what you were doing and which colors were hard to read or tell apart;
- a screenshot, if you can share one;
- your macOS version, font and size, and any display or accessibility
  settings you use, such as color filters or Increase Contrast.

## Contributing

Changes to the palette must keep the targets above. The test suite checks
contrast, the normal and bright pairs, the gray order, and red against
yellow:

```sh
python3 -m unittest discover -s tests -v
```

Contrast is measured, not judged by eye. When a change trades one target
against another, describe the trade-off in the pull request and in
[docs/APPLE-TERMINAL.md](docs/APPLE-TERMINAL.md). See
[CONTRIBUTING.md](CONTRIBUTING.md) for the rest of the workflow.

## Ownership and maintenance

The profile is maintained by [@nelvaron](https://github.com/nelvaron), who
reviews accessibility reports and changes. The automated checks run on every
pull request. This page is reviewed whenever the palette changes, and the
known barriers are updated with it.

The [Verdant Ledger Light theme for VS Code](https://github.com/nelvaron/vscode-verdant-ledger)
uses the same terminal palette and has its own accessibility page.
