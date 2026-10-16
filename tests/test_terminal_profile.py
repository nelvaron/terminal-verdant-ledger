import json
import math
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


# Color vision deficiency, simulated with Machado, Oliveira and Fernandes
# (2009) at full severity in linear RGB, the same method as the VS Code
# theme's scripts/color.mjs.
DEUTERANOPIA = [
    [0.367322, 0.860646, -0.227968],
    [0.280085, 0.672501, 0.047413],
    [-0.01182, 0.04294, 0.968881],
]
PROTANOPIA = [
    [0.152286, 1.052583, -0.204868],
    [0.114503, 0.786281, 0.099216],
    [-0.003882, -0.048116, 1.051998],
]


def _linear(value):
    c = value / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def simulate(color, matrix):
    rgb = [_linear(int(color[i : i + 2], 16)) for i in (1, 3, 5)]
    out = []
    for row in matrix:
        v = min(1, max(0, sum(row[j] * rgb[j] for j in range(3))))
        v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        out.append(round(v * 255))
    return "#" + "".join(f"{v:02X}" for v in out)


def _lab(color):
    r, g, b = (_linear(int(color[i : i + 2], 16)) for i in (1, 3, 5))
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def delta_e_2000(a, b):
    L1, a1, b1 = _lab(a)
    L2, a2, b2 = _lab(b)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cbar = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cbar**7 / (Cbar**7 + 25**7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1 = math.degrees(math.atan2(b1, a1p)) % 360
    h2 = math.degrees(math.atan2(b2, a2p)) % 360
    dh = 0
    if C1p * C2p:
        dh = h2 - h1
        if dh > 180:
            dh -= 360
        elif dh < -180:
            dh += 360
    dL, dC = L2 - L1, C2p - C1p
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lbar, Cbarp = (L1 + L2) / 2, (C1p + C2p) / 2
    hbar = h1 + h2
    if C1p * C2p:
        if abs(h1 - h2) <= 180:
            hbar = (h1 + h2) / 2
        else:
            hbar = (h1 + h2 + 360) / 2 if h1 + h2 < 360 else (h1 + h2 - 360) / 2
    T = (
        1
        - 0.17 * math.cos(math.radians(hbar - 30))
        + 0.24 * math.cos(math.radians(2 * hbar))
        + 0.32 * math.cos(math.radians(3 * hbar + 6))
        - 0.2 * math.cos(math.radians(4 * hbar - 63))
    )
    d_theta = 30 * math.exp(-(((hbar - 275) / 25) ** 2))
    Rc = 2 * math.sqrt(Cbarp**7 / (Cbarp**7 + 25**7))
    Sl = 1 + 0.015 * (Lbar - 50) ** 2 / math.sqrt(20 + (Lbar - 50) ** 2)
    Sc = 1 + 0.045 * Cbarp
    Sh = 1 + 0.015 * Cbarp * T
    Rt = -math.sin(math.radians(2 * d_theta)) * Rc
    return math.sqrt(
        (dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh)
    )


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

    def test_colors_stay_apart_with_color_blindness(self):
        # Pairs that programs commonly use side by side stay at least 7
        # CIEDE2000 units apart after simulating deuteranopia and protanopia.
        # The bright magenta and cyan both sit near 4.5:1 and cannot differ
        # enough in lightness; ACCESSIBILITY.md lists them.
        ansi = PALETTE["ansi"]
        pairs = [("ANSIRedColor", "ANSIYellowColor"), ("ANSIMagentaColor", "ANSICyanColor")]
        for a, b in pairs:
            for name, matrix in (("deuteranopia", DEUTERANOPIA), ("protanopia", PROTANOPIA)):
                with self.subTest(pair=(a, b), vision=name):
                    difference = delta_e_2000(simulate(ansi[a], matrix), simulate(ansi[b], matrix))
                    self.assertGreaterEqual(difference, 7)

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
