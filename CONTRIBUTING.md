# Contributing

Thank you for your interest in Verdant Ledger for Apple Terminal.

- Keep changes focused and explain their purpose.
- Do not edit `profiles/Verdant-Ledger-Light.terminal` by hand. Change `scripts/palette.json` and run `python3 scripts/generate_profile.py`.
- Do not change the canonical palette without updating the documentation; the tests check that the palette table matches.
- Run `python3 -m unittest discover -s tests -v`.
- For changes to the `.terminal` profile, import it into Apple Terminal on macOS and perform a visual smoke test.
- Prefer a branch and pull request for review.

This repository contains a Terminal profile; it does not manage shell configuration or other dotfiles.