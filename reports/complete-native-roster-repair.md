# Complete human endpoints for all 17 animalities

All 17 native reference sprites were recaptured with the opponent's drawing fully
disabled, at the original camera zoom. The previous palette-only isolation left
invisible opponent pixels covering hands, feet, clothing and weapons.

Fourteen roster references contained gaps: Haohmaru, Nakoruru, Hanzo, Galford,
Wan-Fu, Ukyo, Kyoshiro, Gen-an, Earthquake, Charlotte, Genjuro, Sieger, Nicotine
and Mizuki. Jubei had already been repaired; Cham Cham and Kuroko were complete.
Each corrected roster reference preserves every previously visible native pixel.
The largest repair is Earthquake, with 1362 restored pixels.

Ukyo's installed endpoints came from a different, older dedicated capture.
That capture retained some opponent pixels and used a different idle animation
moment. Both endpoints now use a clean complete native idle capture, and the
build configuration records its proper horizontal anchor.

Only human frames 00 and 15 and their packed GD variants were replaced.
All generated transformation/animal PNGs and GD sprites were checked byte for
byte against their backups and remain unchanged. Palette maps and previews were
refreshed to include all repaired native colors.

The canonical native capture script now disables opponent drawing, preventing
this problem in subsequent captures.

## Artifacts and reproduction

- [Repaired roster overview](complete-native-fixed-roster.png)
- [Before/after reference comparison](complete-native-audit.png)
- [Per-character repair results](complete-native-repair-results.json)
- [Exact native pixel checks](complete-native-pixel-verification.txt)
- [Palette/packing checks](complete-native-roster-palette-verification.txt)
- [Actual FBNeo playback log](fbneo-complete-native-roster-test.log)

Capture using reports/capture-complete-native-roster.lua in the existing HBMAME
research fixture. Then run reports/audit-native-roster.py,
reports/repair-complete-native-roster.py, and
reports/verify-complete-native-repair.py with tools/Python/python.exe.
Audit before installation so the before/after record refers to the old sprites.
The separate Ukyo research capture remains in reports/capture-ukyo-complete-native.lua.
The repair uses the clean shared roster capture, not that research output.

Backups: reports/before-complete-native-roster stores the original native
references/metadata. Each repaired animality has its old installed assets under
versions/before-complete-native-roster. Jubei's preceding repair has its own backup.

Validation: all 17 endpoint pairs compared exactly with opponent-free native
captures; all generated frames preserved; 34 actual FBNeo previews across both
player slots; 10880 runtime palette/direction/zoom variants checked.

Restart animality.lua in FBNeo to reload the repaired endpoints.
