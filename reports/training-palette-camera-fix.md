# Training costume preservation and camera scaling

Training J/K and N/M character changes now retain each player's current main or
alternate costume. The old character's selected native ROM palette pointer
determines the costume; the new character receives its corresponding palette,
including all eight palette-bank pointers and live colors. Preview/reset saves
retain that selection.

Animal overlays previously snapped to five prebuilt sizes (50%, 62.5%, 75%,
87.5%, 100%). They now follow all 129 native compression values between 50% and
100%, rounding only to whole output pixels. Every frame samples the original
128-size asset directly using nearest-neighbor sampling. Position anchors use
the actual output dimensions, keeping the feet aligned during zoom changes.
No artwork or animation timing was changed.

A bounded 32-entry cache belongs to the active animality and is discarded when
that sequence ends. This avoids storing every frame at every possible scale.
Pixel art still changes individual pixels when reduced; exact Neo Geo per-tile
hardware shrink patterns can differ from a whole-sprite nearest-neighbor image.
The large artificial 12.5% size jumps are removed.

Validation:

- reports/training-palette-preservation-verification.log: main/alternate,
  both slots, forward/back changes, preview interruption and reset.
- reports/camera-scaling-verification.txt: all 129 compression values, both
  directions, human/animal/impact drawings at 128, 192 and 256 canvas sizes
  (2322 rendered images). Comparison against Pillow nearest-neighbor allows
  its lower-neighbor floating-point choice only at exact half-pixel ties;
  the Lua renderer consistently chooses the upper original neighbor.
- reports/fbneo-alternate-camera-test.log: actual FBNeo all-character alternate
  costume switching and animality previews for both players.

Restart the loaded Lua script in FBNeo to activate these changes.
