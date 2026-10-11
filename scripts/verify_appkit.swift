// Decode every profile color with AppKit, the way Apple Terminal does, and
// compare it with scripts/palette.json. Runs on macOS only:
//
//     swift scripts/verify_appkit.swift profiles/Verdant-Ledger-Light.terminal scripts/palette.json

import AppKit
import Foundation

func fail(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

let arguments = CommandLine.arguments
guard arguments.count == 3 else {
    fail("usage: swift verify_appkit.swift <profile.terminal> <palette.json>")
}

let profileData = try Data(contentsOf: URL(fileURLWithPath: arguments[1]))
guard
    let profile = try PropertyListSerialization.propertyList(
        from: profileData, format: nil) as? [String: Any]
else {
    fail("\(arguments[1]) is not a dictionary property list")
}

let paletteData = try Data(contentsOf: URL(fileURLWithPath: arguments[2]))
guard
    let palette = try JSONSerialization.jsonObject(with: paletteData) as? [String: Any],
    let core = palette["colors"] as? [String: String],
    let ansi = palette["ansi"] as? [String: String]
else {
    fail("\(arguments[2]) is missing the colors or ansi tables")
}

if (profile["Name"] as? String) != (palette["name"] as? String) {
    fail("Profile name does not match the palette")
}

func hex(_ value: CGFloat) -> String {
    String(format: "%02X", Int((value * 255).rounded()))
}

var failures = 0
for (key, expected) in core.merging(ansi, uniquingKeysWith: { a, _ in a }).sorted(by: { $0.key < $1.key }) {
    guard let archive = profile[key] as? Data else {
        print("FAIL \(key): missing")
        failures += 1
        continue
    }
    do {
        guard
            let color = try NSKeyedUnarchiver.unarchivedObject(ofClass: NSColor.self, from: archive),
            let rgb = color.usingColorSpace(.deviceRGB)
        else {
            print("FAIL \(key): not an RGB NSColor")
            failures += 1
            continue
        }
        let actual = "#" + hex(rgb.redComponent) + hex(rgb.greenComponent) + hex(rgb.blueComponent)
        if actual == expected.uppercased() && rgb.alphaComponent == 1 {
            print("ok   \(key) \(actual)")
        } else {
            print("FAIL \(key): expected \(expected), got \(actual) alpha \(rgb.alphaComponent)")
            failures += 1
        }
    } catch {
        print("FAIL \(key): \(error.localizedDescription)")
        failures += 1
    }
}

if failures > 0 {
    fail("\(failures) color(s) failed AppKit decoding")
}
print("All \(core.count + ansi.count) colors decode with AppKit.")
