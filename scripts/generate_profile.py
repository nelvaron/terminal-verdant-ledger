#!/usr/bin/env python3
"""Generate the Apple Terminal profile from scripts/palette.json.

Apple Terminal stores each color as a binary NSKeyedArchiver archive of an
NSColor, embedded as base64 <data> in an XML property list. Hand-editing that
base64 is error-prone, so the profile is always built by this script:

    python3 scripts/generate_profile.py          # rewrite the profile
    python3 scripts/generate_profile.py --check  # fail if it is out of date
"""

import argparse
import json
import plistlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PALETTE_PATH = ROOT / "scripts" / "palette.json"
PROFILE_PATH = ROOT / "profiles" / "Verdant-Ledger-Light.terminal"

# NSColorSpace 2 is NSDeviceRGBColorSpace, the encoding Terminal itself has
# long used for profile colors.
NS_DEVICE_RGB = 2

SETTINGS = {
    "FontAntialias": True,
    "ProfileCurrentVersion": "2.07",
    "UnlimitedScrollback": True,
    "UseBoldFonts": True,
    "UseBrightBold": False,
    "UseOptionAsMetaKey": False,
    "columnCount": 100,
    "rowCount": 30,
    "scrollbackLines": 10000,
    "shellExitAction": 1,
    "type": "Window Settings",
}


def load_palette():
    with PALETTE_PATH.open(encoding="utf-8") as stream:
        return json.load(stream)


def hex_to_components(value):
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected #RRGGBB, got #{value}")
    return [int(value[i : i + 2], 16) / 255 for i in (0, 2, 4)]


def archive_color(value):
    """Return a binary NSKeyedArchiver archive of an opaque NSColor."""
    rgb = " ".join(f"{c:.10g}" for c in hex_to_components(value))
    archive = {
        "$archiver": "NSKeyedArchiver",
        "$version": 100000,
        "$top": {"root": plistlib.UID(1)},
        "$objects": [
            "$null",
            {
                "$class": plistlib.UID(2),
                "NSColorSpace": NS_DEVICE_RGB,
                # AppKit writes NSRGB as a NUL-terminated ASCII string.
                "NSRGB": rgb.encode("ascii") + b"\0",
            },
            {"$classname": "NSColor", "$classes": ["NSColor", "NSObject"]},
        ],
    }
    return plistlib.dumps(archive, fmt=plistlib.FMT_BINARY, sort_keys=False)


def build_profile(palette):
    profile = {"Name": palette["name"], **SETTINGS}
    for key, value in {**palette["colors"], **palette["ansi"]}.items():
        profile[key] = archive_color(value)
    return plistlib.dumps(profile, fmt=plistlib.FMT_XML, sort_keys=True)


def normalize(data):
    """Parse a profile, decoding nested color archives, for comparison."""
    profile = plistlib.loads(data)
    return {
        key: plistlib.loads(value) if isinstance(value, bytes) else value
        for key, value in profile.items()
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit with an error if the committed profile is out of date",
    )
    args = parser.parse_args()

    generated = build_profile(load_palette())
    relative = PROFILE_PATH.relative_to(ROOT)
    if args.check:
        try:
            current = normalize(PROFILE_PATH.read_bytes())
        except Exception:  # missing, malformed plist, or corrupt color archive
            current = None
        if current != normalize(generated):
            print(
                f"{relative} is out of date; run python3 scripts/generate_profile.py",
                file=sys.stderr,
            )
            return 1
        print(f"{relative} is up to date")
        return 0

    PROFILE_PATH.write_bytes(generated)
    print(f"Wrote {relative}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
