# Complete Jubei native idle capture

The original isolated capture recolored the opponent as background but still drew
him over Jubei. Removing that background also removed covered parts of Jubei's
swords, right hand, trousers and foot.

The new capture uses the game's native idle drawing and the opponent's
projection-only handler (0x385c) so the opponent cannot cover Jubei. This preserves
the original camera zoom, idle pose and every already-visible native pixel.
It restores 365 missing pixels, including the hand and sword tassel.

The user's slot 1 save was found and inspected without modification. The native
idle was recaptured in a separate HBMAME research instance to avoid baking an
active Lua overlay into the repaired sprite.

Reproduction: run reports/capture-jubei-complete.lua in the existing HBMAME
research fixture, then tools/Python/python.exe reports/fix-jubei-native.py.
The repair updates assets/native-roster/jubei.png, jubei-reference.png and
Jubei's roster crop/anchor metadata, then rebuilds the Jubei assets. Frames 00/15
use the repaired native sprite. Frames 01..14 remain byte-identical.
Backup: assets/jubei-animality/versions/before-complete-native-idle.

[Before/after comparison](jubei-native-fixed-comparison.png).
Packing and native-pixel checks: jubei-native-fixed-verification.txt.
Palette checks: jubei-native-fixed-palette-verification.txt (640 variants).
Actual FBNeo both-player playback: fbneo-jubei-test.log.

Restart animality.lua to reload the repaired sprite.
