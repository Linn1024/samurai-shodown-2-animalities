# Animality style review — 2026-10-10

Compared all 14 currently built animal asset sets against their captured native fighters. Only seven are enabled in the Lua registry; this review does not enable unfinished characters.

Haohmaru's tiger and Galford's wolf had the clearest continuous dark contour mismatch. Redrew their twelve source poses with built-in image_gen, using each existing sheet as the edit target and the actual native fighter capture as the style reference. The new sheets use warm brown/olive edges for the tiger and indigo/lavender edges for the wolf, with simpler shading. Dark hair, tiger stripes, eyes, claws and deep interior shadows remain intentional details.

Sources and exact prompts:

- `assets/haohmaru-animality/source-v2.png` and `prompt-v2.txt`
- `assets/galford-animality/source-v2.png` and `prompt-v2.txt`

The v1 sheets and prompts are preserved. `build-config.json` selects the new source. The builder quantizes the artwork to the existing character palette and exports sixteen frames and 160 GD sprites per character. Actual native human start/end frames remain pixel exact. Tiger scale remains 0.33 with a 192px canvas and crouch_pounce movement; wolf scale remains 0.22 with a 128px canvas. Wolf strike contact was recalculated to (31,23) from the new impact silhouette.

The other built animals were visually reviewed and left as they are in this pass. Their contrast depends on the corresponding native fighter: Charlotte and Kuroko, for example, already use strong dark contour/shadow colors. This is a visual review, not a claim that every animation is a perfect native-art match.

For future artwork: view the actual native capture first; request broad pixel clusters and a few tones per material, selective colored contours, lit edges meeting transparency, and no uniform black perimeter or opaque ground shadow. Preserve the animation pose order and character accessories. Inspect the final palette-mapped game render as well as the high-resolution source: palette quantization and costume remapping can alter edge contrast.

Validation: native human pixel comparison; both characters' native integration checks in default, left-facing, P2, ordinary KO, and cancellation modes; 640 runtime GD images per character checked across two costumes, both players/directions and five zoom sizes. Actual FBNeo captures are saved in each animality asset folder.

Restart the Lua script in FBNeo to reload the rebuilt GD sprites and discard its old sprite/palette caches.
