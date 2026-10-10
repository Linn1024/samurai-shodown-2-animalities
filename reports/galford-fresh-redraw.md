# Galford wolf: complete fresh drawing (v5)

This replaces the previous wolf sheet with twelve newly generated drawings.
The only reference used for initial generation was the actual native Galford
sprite (`assets/native-roster/galford-reference.png`). No earlier wolf sheet
was supplied as an image reference. Built-in imagegen created the sheet;
a second pass corrected its sheet-edge spacing using only that new sheet.

The new wolf has adult proportions, longer muzzle and lean legs, a blond
forelock, orange scarf, indigo coat and silver underside. Full wolf poses no
longer carry human arm armor. Both human endpoint frames remain the exact
native capture. Standing return reuses the initial stand exactly.

The original generated output is retained as `source-v5.generated.png`.
The tool returned 1448x1086 rather than the requested 768x576. Packing uses
an exact 2:1 nearest-neighbor reduction (`source-v5.png`, 724x543), then a
uniform 0.84375 display reduction to a maximum height of 108 game pixels
(Galford's human frame is 109). This is generated artwork with deterministic
packing, not a claim of manually authored pixel-perfect SNK art. Current
canvas remains 192x192 with anchor (96,176). Source silhouettes are extracted
as connected shapes, because generated rows do not have exact cell baselines.

Exact generation prompt: `assets/galford-animality/prompt-v5.txt`.
Spacing correction: `assets/galford-animality/prompt-v5-spacing.txt`.
Before/after: `galford-fresh-redraw-comparison.png`, both at exact 2x display.
Prior installed art: `assets/galford-animality/versions/before-complete-redraw-v5`.

The size script reads `size_reference` from the config so later sizing uses
this new art's measurements rather than the retired wolf sheet. Runtime
contact is remeasured from the new impact pose; gameplay timing and controls
are unchanged. Restart Lua to clear cached sprites and palette data.

Validation passed: all 16 frames unclipped, binary alpha, 160 valid GD files,
byte-identical human endpoints, repeated standing pose, maximum height 108;
native default/left/P2/ordinary-KO/cancellation integration checks; 640 exact
runtime palette variants; live FBNeo fountain, animality, native victory and
callback restoration. Logs: `galford-fresh-native-verification.txt`,
`galford-animality-palette-verification.txt`, `fbneo-galford-test.log`.
Live preview: `assets/galford-animality/fbneo-live-finish.gif`.
