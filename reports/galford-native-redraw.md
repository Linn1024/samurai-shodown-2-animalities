# Galford wolf — native-size redraw

The earlier source was sampled with a fractional scale (0.38732), producing
uneven detail in the enlarged wolf. This revision uses a new drawing with the
existing design and twelve poses specified at their intended in-game size.
It preserves the blond crest, orange scarf, indigo/silver coat and hybrid armor.

The built-in image_gen tool received `galford-native-size-edit-target.png`
(the twelve current game-size poses) and the actual native Galford capture.
The exact prompt is `assets/galford-animality/prompt-v3.txt`.

The generator returned a 1448 x 1086 raster rather than the requested 768 x 576.
That original is saved as `source-v3.generated.png`. The packable source is an
exact 2:1 nearest-neighbor reduction, 724 x 543, saved as `source-v3.png`.
No small sprite is enlarged: the native source is packed at scale 1.0, with
one source pixel per game pixel at full camera zoom. Existing smaller camera
zooms still use the usual nearest-neighbor sprite variants. This does not claim
the generator produced a manually authored pixel-exact raster at the requested
dimensions; the final packed artwork is inspected at actual game resolution.

The strike is 122 x 89 pixels (previously 124 x 89); standing pose is 129 x 102
(previously 133 x 105). Native human frames remain byte-identical. The return
standing frame repeats the initial standing drawing exactly. Canvas remains
192 x 192 and the measured impact contact is refreshed in `animalities.lua`.

`native_size_source` and `source_size` in the build config assert a 1:1 source
and prevent accidental later enlargement. The normal builder can also write
into a review folder using `--asset-dir`, so future artwork can be inspected
before installation. Earlier source files are retained. Complete old output
assets and config are in `assets/galford-animality/versions/before-native-redraw`.

Comparison: `galford-native-redraw-comparison.png` (before above, redraw below,
same 3x display zoom). Live capture: the wolf asset folder's
`fbneo-live-finish.gif`. Only Galford's artwork changes in this revision.

Validation: real-game default/left/P2/ordinary-KO/cancellation checks; exact
human pixels, identical standing frames, unclipped frame bounds, opaque or
transparent alpha only; 640 runtime sprites across two costumes, both players,
both directions and five camera zooms. Palette log:
`galford-native-redraw-palette.log`. Native integration log:
`galford-native-redraw-integration.txt`.

Restart the Lua script to discard the previous sprite and palette caches.
