# Sieger rhinoceros: gauntlet foreleg v4

The near foreleg now retains Sieger's signature oversized black metal gauntlet,
golden knuckles and orange/red flame emblem. The other feet remain ordinary rhino
feet. The late human/rhino intermediate also retains this gauntlet.

The original native human frames 00/15 and upright early intermediate 01/14 are
byte-identical to their previous versions. The late intermediate returns in frame
13. Animation timing, movement and character sizes are unchanged.

## Sources and prompts

Created with the built-in imagegen tool. Exact prompts and generated source paths
are recorded in [sieger-gauntlet-generation.json](sieger-gauntlet-generation.json).
Project copies:

- [Edited rhino sheet](../assets/sieger-animality/source-v4.generated.png)
- [Edited transformation pair](../assets/sieger-animality/idle-morph-v4.generated.png)
- [Sheet prompt](../assets/sieger-animality/prompt-source-v4.txt)
- [Transformation prompt](../assets/sieger-animality/prompt-idle-morph-v4.txt)

Inputs: the living-rhino source-v2 sheet, idle-morph-v3 pair, and original
native-roster/sieger-reference.png. The old rejected armored-rhino art was not used.

## Packing

Run `tools/Python/python.exe reports/prepare-sieger-gauntlet.py` to stage and
inspect [the review](sieger-gauntlet-review.png), then rerun with `--install`.
The importer only crops, reduces with nearest-neighbor sampling, quantizes to
native colors, and packs generated artwork. It keeps the existing early
intermediate exactly. Complete rhino drawings stay at the previous source size
723 by 543, with 192-pixel canvases and ground anchor (96,176).

Run `tools/Python/python.exe reports/build-roster-registry.py --existing-only`
after installing to refresh the attack contact position. The installed assets
live in assets/sieger-animality; the previous installed assets are saved in
versions/before-gauntlet-v4. Future resizing uses versions/gauntlet-v4-size-reference.

## Validation

The importer checks exact unchanged native/early frames, symmetric reverse
transformation, binary alpha and safe canvas bounds.

Runtime and palette test commands:

```
tools/Python/python.exe reports/check-complete-roster.py --slugs sieger --report reports/sieger-gauntlet-verification.txt
tools/Python/python.exe reports/run-fbneo-roster-test.py 14 sieger --script reports/fbneo-test-sieger-gauntlet.lua --expected-events 2 --capture-frames 90 --completion-timeout 60
```

The FBNeo test entry is flat so Lua 5.1 can yield from frameadvance. It previews
both player slots and checks the native fountain, return to human and victory.
Restart animality.lua in FBNeo to reload changed sprites.

Results: PASS all 640 runtime costume/direction/zoom variants and all 16 safe
frames. Actual FBNeo passed both player previews (2 events), native fountain,
human restoration and victory-handler restoration (25314).
