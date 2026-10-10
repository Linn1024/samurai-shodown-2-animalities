# Galford wolf detail cleanup

Built-in imagegen edited the twelve v3 poses using the actual native Galford
sprite as a style reference. The exact prompt is saved in
`assets/galford-animality/prompt-v4.txt`. Changes target fur clusters, face,
crest, paws and selective outlines; the design, movement and intended size
are preserved. This is a focused visual revision, not a claim that generated
art perfectly matches hand-authored SNK sprites.

The tool returned 1448 x 1086. `source-v4.generated.png` preserves that output;
`source-v4.png` is its exact 2:1 nearest-neighbor reduction to 724 x 543.
The builder packs this source at scale 1.0. No coarse pixel-grid filter is used.
The complete previous installed assets are backed up under
`assets/galford-animality/versions/before-detail-cleanup-v4`.

`galford-cleanup-comparison.png` shows four corresponding poses before and
after, at exact 3x nearest-neighbor display size. All 16 frames are unclipped,
human frames are byte-identical, standing return matches the initial stand,
alpha is binary, and 160 GD files have valid dimensions. Native default,
left-facing, P2, ordinary KO and cancellation integration checks passed.
640 palette variants passed exact alpha/RGB verification across two costumes,
both players, both directions and five camera zooms.

Restart the Lua script to discard cached drawings, then use T and G/H for
the existing training preview.
