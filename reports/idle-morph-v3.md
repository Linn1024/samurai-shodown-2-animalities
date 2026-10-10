# Transformations connected to the original human idle poses

Updated Nicotine, Sieger, Haohmaru and Genjuro after user approval. Two new
intermediate drawings for each character connect the native human idle to
the existing completed animal. No other character artwork is changed.

The first hybrid inherits the human stance, weapon position and proportions;
the second lowers/shortens the body gradually toward the animal. Nicotine
retains the tilted hat and shoulder staff; Sieger retains the raised giant
gauntlet in the early stage; Haohmaru and Genjuro retain their sword-ready
stance. Genjuro's later hybrid holds the shrinking sword in a remaining human
hand rather than between its teeth.

Packing aligns the first hybrid to the native idle's exact overall height,
foot baseline and actor-relative horizontal placement. The second interpolates
these measurements toward the animal. This replaces the earlier generic
55-percent-width anchor and crouching hybrids. Exact measurements are saved
in idle-morph-v3-measurements.json.

All native humans (00/15), complete animals and attacks (03-12) are
byte-identical to the installed assets before this change. Only 01/02 and
their reversed return copies 14/13 change. All sixteen-frame runtime timing,
including twelve game frames for each hybrid, remains unchanged.

Built-in imagegen created the artwork, using the exact human and existing
animal endpoint captures as reference. A targeted Genjuro correction changed
the late hybrid's sword hand; the original generated early hybrid is retained.
Processing only crops, reduces with nearest-neighbor, quantizes to the native
palette and packs PNG/GD files. These are generated bitmap assets.

Installed under assets/<slug>-animality/:

- idle-to-animal-reference-v3.png: human/animal endpoint references.
- idle-morph-v3.generated.png: generated source pair.
- idle-morph-v3-01.png and idle-morph-v3-02.png: aligned canvas overrides.
- prompt-idle-morph-v3.txt: exact generation prompt.
- Genjuro also has idle-morph-v3-initial.generated.png and
  prompt-idle-morph-v3-correction.txt.
- build-config.json enables the new transformation_overrides.

Sources and exact prompts: idle-morph-v3-generation.json.
Importer: prepare-idle-morph-v3.py; run to stage and then --install to copy
reviewed assets. --slugs limits the operation to named characters.
Archived previous assets: versions/before-idle-morph-v3 in each changed folder.
Review: idle-morph-v3-review.png and idle-morph-v3-preview.gif.

Verification: idle-morph-v3-verification.txt (four changed sets, 64 unclipped
drawings, 640 packed assets and 2,560 runtime costume variants); actual FBNeo
training preview/restore log: idle-morph-v3-fbneo-live.log (all four for both
players). Native humans and animal attack files are asserted unchanged during
staging. Reversed hybrid files are asserted identical to their forward poses.

FBNeo's Lua 5.1 cannot yield frameadvance through a nested dofile call.
The dedicated fbneo-test-idle-morph-v3.lua therefore prepends the selected IDs
to the common training test as a flat top-level chunk. The initial wrapper
hit this test-harness limitation before any preview; the flattened entry point
is used for the playback validation.
