import json
import plistlib
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "profiles" / "Verdant-Ledger-Light.terminal"
PALETTE_PATH = ROOT / "scripts" / "palette.json"
DOCS_PATH = ROOT / "docs" / "APPLE-TERMINAL.md"

with PALETTE_PATH.open(encoding="utf-8") as _stream:
    PALETTE = json.load(_stream)

ANSI_NAMES = [
    "Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White",
]
ANSI_KEYS = [f"ANSI{name}Color" for name in ANSI_NAMES] + [
    f"ANSIBright{name}Color" for name in ANSI_NAMES
]


def decode_nscolor(data):
    archive = plistlib.loads(data)
    if archive.get("$archiver") != "NSKeyedArchiver":
        raise AssertionError("Expected an NSKeyedArchiver NSColor archive")
    objects = archive["$objects"]
    color = objects[archive["$top"]["root"].data]
    class_info = objects[color["$class"].data]
    if class_info.get("$classname") != "NSColor":
        raise AssertionError(f"Expected NSColor, got {class_info.get('$classname')}")
    if color.get("NSColorSpace") not in (1, 2):
        raise AssertionError(f"Expected an RGB color space, got {color.get('NSColorSpace')}")
    raw = color["NSRGB"].rstrip(b"\0").decode("ascii")
    values = [float(v) for v in raw.split()]
    if len(values) not in (3, 4):
        raise AssertionError(f"Unexpected RGB component count: {len(values)}")
    if not all(0 <= v <= 1 for v in values):
        raise AssertionError(f"RGB components out of range: {raw}")
    return "#" + "".join(f"{round(v * 255):02X}" for v in values[:3])


def luminance(color):
    channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [
        c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(a, b):
    high, low = sorted((luminance(a), luminance(b)), reverse=True)
    return (high + 0.05) / (low + 0.05)


class TerminalProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with PROFILE_PATH.open("rb") as stream:
            cls.profile = plistlib.load(stream)

    def test_profile_identity(self):
        self.assertEqual(self.profile.get("Name"), PALETTE["name"])
        self.assertEqual(self.profile.get("type"), "Window Settings")

    def test_palette_defines_all_sixteen_ansi_colors(self):
        self.assertEqual(sorted(PALETTE["ansi"]), sorted(ANSI_KEYS))

    def test_core_and_ansi_colors(self):
        for key, color in {**PALETTE["colors"], **PALETTE["ansi"]}.items():
            with self.subTest(key=key):
                self.assertIn(key, self.profile)
                self.assertEqual(decode_nscolor(self.profile[key]), color.upper())

    def test_every_data_value_is_a_valid_color(self):
        for key, value in self.profile.items():
            if isinstance(value, bytes):
                with self.subTest(key=key):
                    decode_nscolor(value)

    def test_profile_matches_generator(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_profile.py"), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_text_contrast(self):
        background = PALETTE["colors"]["BackgroundColor"]
        selection = PALETTE["colors"]["SelectionColor"]
        text = {"TextColor": PALETTE["colors"]["TextColor"], **PALETTE["ansi"]}
        for key, color in text.items():
            with self.subTest(key=key):
                if key == "ANSIBrightWhiteColor":
                    # The lightest gray: programs use it on colored
                    # backgrounds, so it stays light, but remains legible.
                    self.assertGreaterEqual(contrast(color, background), 3)
                    continue
                self.assertGreaterEqual(contrast(color, background), 4.5)
                self.assertGreaterEqual(contrast(color, selection), 3.5)

    def test_normal_colors_meet_aaa(self):
        background = PALETTE["colors"]["BackgroundColor"]
        for name in ANSI_NAMES[1:7]:
            color = PALETTE["ansi"][f"ANSI{name}Color"]
            with self.subTest(name=name):
                self.assertGreaterEqual(contrast(color, background), 7)

    def test_bright_colors_are_lighter_than_normal(self):
        # Both halves need at least 4.5:1 on a light background, so a bright
        # color can only be told apart from its normal pair by lightness.
        background = PALETTE["colors"]["BackgroundColor"]
        for name in ANSI_NAMES:
            normal = PALETTE["ansi"][f"ANSI{name}Color"]
            bright = PALETTE["ansi"][f"ANSIBright{name}Color"]
            with self.subTest(name=name):
                ratio = contrast(normal, background) / contrast(bright, background)
                self.assertGreaterEqual(ratio, 1.5)

    def test_bright_white_is_the_lightest_gray(self):
        ansi = PALETTE["ansi"]
        bright_white = luminance(ansi["ANSIBrightWhiteColor"])
        for key in ("ANSIBlackColor", "ANSIWhiteColor", "ANSIBrightBlackColor"):
            with self.subTest(key=key):
                self.assertGreater(bright_white, luminance(ansi[key]))

    def test_red_stays_darker_than_yellow(self):
        # With red-green color blindness, red and ochre look alike and
        # lightness is what separates them (see the VS Code theme's DESIGN.md).
        background = PALETTE["colors"]["BackgroundColor"]
        red = contrast(PALETTE["ansi"]["ANSIRedColor"], background)
        yellow = contrast(PALETTE["ansi"]["ANSIYellowColor"], background)
        self.assertGreaterEqual(red / yellow, 1.5)

    def test_cursor_is_visible(self):
        colors = PALETTE["colors"]
        self.assertGreaterEqual(contrast(colors["CursorColor"], colors["BackgroundColor"]), 3)

    def test_documented_palette_matches(self):
        docs = DOCS_PATH.read_text(encoding="utf-8")
        rows = dict(re.findall(r"^\| ((?:Bright )?\w+) \| `(#[0-9A-F]{6})` \|", docs, re.M | re.I))
        background = PALETTE["colors"]["BackgroundColor"]
        for key, color in PALETTE["ansi"].items():
            label = re.sub(r"^ANSI(Bright)?(\w+)Color$", r"\1 \2", key).strip()
            label = label.capitalize()
            with self.subTest(key=key):
                self.assertEqual(rows.get(label, "").upper(), color.upper())
                ratio = f"{contrast(color, background):.2f}:1"
                self.assertRegex(docs, rf"`{color}` \| {re.escape(ratio)} \|")


if __name__ == "__main__":
    unittest.main()
