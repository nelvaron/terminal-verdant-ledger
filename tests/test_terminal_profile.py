import plistlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "profiles" / "Verdant-Ledger-Light.terminal"

EXPECTED = {
    "ANSIBlackColor": "#1B2320",
    "ANSIRedColor": "#8A2621",
    "ANSIGreenColor": "#2D6A3B",
    "ANSIYellowColor": "#8A6408",
    "ANSIBlueColor": "#3D5F7A",
    "ANSIMagentaColor": "#7A4A6E",
    "ANSICyanColor": "#2F6B6B",
    "ANSIWhiteColor": "#5D6864",
    "ANSIBrightBlackColor": "#66716D",
    "ANSIBrightRedColor": "#B8443A",
    "ANSIBrightGreenColor": "#3A7D4A",
    "ANSIBrightYellowColor": "#8F6809",
    "ANSIBrightBlueColor": "#4A6E8E",
    "ANSIBrightMagentaColor": "#8D5A80",
    "ANSIBrightCyanColor": "#367878",
    "ANSIBrightWhiteColor": "#52635A",
}

def decode_nscolor(data):
    archive = plistlib.loads(data)
    if archive.get("$archiver") != "NSKeyedArchiver":
        raise AssertionError("Expected an NSKeyedArchiver NSColor archive")
    root = archive["$top"]["root"].data
    obj = archive["$objects"][root]
    raw = obj["NSRGB"]
    values = [float(v) for v in (raw.decode("ascii") if isinstance(raw, bytes) else str(raw)).split()]
    if len(values) not in (3, 4):
        raise AssertionError(f"Unexpected RGB component count: {len(values)}")
    return "#" + "".join(f"{round(v * 255):02X}" for v in values[:3])

class TerminalProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with PROFILE_PATH.open("rb") as stream:
            cls.profile = plistlib.load(stream)

    def test_profile_identity(self):
        self.assertEqual(self.profile.get("Name"), "Verdant Ledger Light")
        self.assertEqual(self.profile.get("type"), "Window Settings")

    def test_core_and_ansi_colors(self):
        expected = {
            "BackgroundColor": "#F6F8F6",
            "TextColor": "#1B2320",
            "BoldTextColor": "#1B2320",
            "CursorColor": "#2D6A3B",
            "SelectionColor": "#D5E1D8",
            **EXPECTED,
        }
        for key, color in expected.items():
            with self.subTest(key=key):
                self.assertIn(key, self.profile)
                self.assertEqual(decode_nscolor(self.profile[key]), color)

    def test_sixteen_ansi_entries(self):
        self.assertEqual(sum(key in self.profile for key in EXPECTED), 16)

if __name__ == "__main__":
    unittest.main()