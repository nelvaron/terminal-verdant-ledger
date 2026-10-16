# Accessibility

Verdant Ledger for Apple Terminal is a light color profile for Terminal on
macOS, adapted from the
[Verdant Ledger Light theme for VS Code](https://github.com/nelvaron/vscode-verdant-ledger).
It is built so that terminal output stays readable for long sessions and for
people with low vision or color blindness. This page covers what we aim for,
what we test, the barriers we know about, and how to report a new one.

## Priorities

- **Contrast you can read.** The foreground reaches 15.04:1 on the
  background. Every colored ANSI color (red, green, yellow, blue, magenta,
  cyan) reaches at least 4.5:1 in its bright form and 7:1 in its normal form.
- **Normal and bright stay apart.** Each bright color is clearly lighter than
  its normal color, so programs that use both remain readable.
- **Not color alone.** Red is kept much darker than yellow, so errors and
  warnings stay apart with red-green color blindness.
- **Readable selections and a visible cursor.** Every ANSI color except bright
  white keeps at least 3.6:1 on the selection color, and the green block
  cursor reaches 6.08:1.
- **Measured, not judged by eye.** The targets above are checked by the test
  suite on every pull request.

The [palette notes](docs/APPLE-TERMINAL.md#color-palette) list every color
with its contrast ratio.

## Supported environments

| Environment | Status |
| --- | --- |
| Terminal on macOS | Supported; checked visually in zsh with SF Mono Terminal 13 pt |
| Other terminal apps | Not supported; the `.terminal` file is specific to Apple's Terminal |
| Light profile | The only variant |
| Dark and high-contrast profiles | Not provided (see Known barriers) |

The profile does not set a font, so Terminal keeps your font and size; you can
enlarge text with **Command-+**. Screen readers are not affected by a color
profile, and the profile does not change VoiceOver or Terminal's keyboard
behavior.

## What we test

- **Profile:** `python3 -m unittest discover -s tests -v` checks that every
  color archive decodes, that the profile matches `scripts/palette.json`,
  contrast on the background (4.5:1, and 7:1 for normal colors) and on the
  selection (3.5:1), that each bright color is at least 1.5 times lighter
  than its normal color, that bright white is the lightest gray, and that red
  stays at least 1.5 times darker than yellow. The **Validate Terminal
  profile** workflow runs these tests on every pull request, and decodes every
  color with AppKit on macOS.
- **Color blindness:** the colors were compared after simulating deuteranopia
  (Machado, Oliveira and Fernandes, 2009) with the CIEDE2000 color
  difference. Red and yellow are 12.0 units apart.
- **On a Mac:** the current palette was imported into Terminal and checked
  with `scripts/demo.sh`; the README screenshot comes from that check.

## Known barriers

- **No dark or high-contrast variant.** The profile is light only.
- **Bright white is paler than the other colors**, at 3.35:1 on the
  background and 2.65:1 on the selection. It is the lightest gray, which is
  what programs expect when they print bright white on colored backgrounds.
- **Magenta and cyan look alike with deuteranopia**: 2.7 CIEDE2000 units apart
  for the normal colors and 5.1 for the bright ones; blue and magenta are 5.9
  apart. Output that tells these apart only by color can be hard to read.
- **Colors the profile does not control.** Programs can choose colors from the
  256-color and true-color palettes, or set their own backgrounds. Those are
  not checked.

## Reporting a barrier

If something is hard to read or hard to tell apart, please
[open an issue](https://github.com/nelvaron/terminal-verdant-ledger/issues/new)
and start the title with **Accessibility:**. These details help:

- What you were doing, and which program's output was affected.
- Your macOS version, font and size, and any display settings (zoom, color
  filters, Increase Contrast).
- A screenshot, if you can share one. A description works just as well.

If you would rather not write in public, send a direct message to
[@nelvaron@mastodon.social](https://mastodon.social/@nelvaron).

We aim to reply within a week. A barrier that makes output unreadable is
treated as a bug and fixed in the next change to the profile.

## Contributing

Pull requests must keep the tests passing; they reject a color that misses its
contrast target. Change colors in `scripts/palette.json`, regenerate the
profile, and update the palette table in
[docs/APPLE-TERMINAL.md](docs/APPLE-TERMINAL.md).
[CONTRIBUTING.md](CONTRIBUTING.md) explains the workflow.

## Ownership and maintenance

The profile and this page are maintained by
[@nelvaron](https://github.com/nelvaron). This page is reviewed whenever the
palette changes, and whenever a known barrier is fixed or a new one is found.

Last reviewed: 16 October 2026.
