# Galford: entirely fresh wolf sheet (v6)

The wolf was generated from scratch with built-in imagegen. The ONLY image
reference for the initial generation was assets/native-roster/galford-reference.png,
the original human sprite. No prior wolf images, reels, previews or reference
sheets were opened or supplied. A spacing pass used only the newly generated
sheet. The old installed files were archived by file copy without visual inspection.

All twelve source drawings are new: early human/wolf hybrid, late hybrid,
standing wolf, anticipation, two running strides, pounce, bite impact, recoil,
brake, landing and readiness. The packed reel has 16 frames including the exact
native human endpoints and reversed hybrid drawings. The return stand is an
exact copy of the initial stand. Ground waiting holds the crouch; timing is
unchanged, with both hybrids displayed for 12 game frames each.

The new wolf uses steel-blue/indigo fur, pale silver underside, a small gold
forehead accent and a narrow orange neckband inspired by Galford's costume.
The animal has four canine paws and no human armor. The two hybrids visibly
retain human anatomy at different stages. No previous wolf palette/configuration
was consulted: colors are quantized from the native human capture and shared
ivory shades, with the native ROM costume map rebuilt from scratch.

Sizing preserves the latest smaller-size intent: all non-human poses fit
within 87px height, approximately 80% of Galford's 109px human reference.
The sheet is 1448x1086; source-v6.png is its exact 2:1 nearest-neighbor reduction
to 724x543. Runtime asset packing uses animal_scale 0.798165, never enlargement.
These are generated bitmap drawings with deterministic cropping, reduction,
palette conversion and packing, rather than manually authored SNK pixel art.

Installed assets: assets/galford-animality/.
Raw generated sheet: source-v6.generated.png; normalized sheet: source-v6.png.
Exact prompts: prompt-v6.txt and prompt-v6-spacing.txt in that directory.
Source paths/prompts: reports/galford-fresh-v6-generation.json.
Review: reports/galford-fresh-v6-review.png; complete animation: preview.gif.
Actual FBNeo capture: fbneo-live-finish.gif in the installed asset directory.
Importer/installer: reports/prepare-galford-v6.py (stage; then --install).
Size baseline: versions/fresh-v6-size-reference.
Archive of superseded installed files: versions/before-fresh-v6.

Validation: reports/galford-v6-verification.txt covers 16 unclipped frames,
160 GD assets and all 640 costume variants (both costumes/players/directions,
five zooms). Native finish logs: reports/test-galford-animality-default.log,
test-galford-animality-left.log and test-galford-animality-p2.log.
Actual FBNeo training/preview/restore log: reports/galford-v6-fbneo-live.log.
