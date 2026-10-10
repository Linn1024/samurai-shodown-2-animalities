# Animals limited to character size

The initial width-and-height cap made horizontal animals look too small.
The final revision matches animal height to human height, instead of capping
the animal's length at human width or height. A wolf may therefore be longer
than a standing human, while remaining comparable in height. Existing animals
are never reduced further by this revision. One uniform scale is used for
every pose; neither axis is stretched independently. Human endpoint frames
remain byte-identical. The seven enabled characters remain enabled; this
does not enable unfinished or untested characters.

The display reduction is stored as `animal_scale` in each build config.
The source artwork is retained, including Galford's detail-cleanup v4.
Nearest-neighbor sampling preserves hard pixels. All 160 GD variants per
set and costume maps are rebuilt; strike contacts are measured again.

Measurements: `animality-character-size-cap.json`.
Current human/animal comparison: `animality-human-height-comparison.png`.
Restore point: each animal folder's `versions/before-character-size-cap`.
Rebuild command: `tools/Python/python.exe reports/resize-animality-roster.py`.

Restart Lua to clear cached drawings. Existing training controls remain
T to enable practice and G/H to preview either player's animality.

The initial smaller cap passed packed, palette and native integration checks;
`character-size-cap-native-verification.txt` records that earlier run.
Checks of the revised middle size are recorded separately.

Middle-size validation passed: packing, clipping and native human return for
all 14 sets; 640 palette variants for each of the seven enabled characters;
native finish and cleanup for Galford (ground) and Charlotte (flight).
See `animality-middle-size-native-verification.txt` and the refreshed
`resized-<slug>-palette.log` files. Galford maximum bounds changed from 80x54
to 107x72; Haohmaru from 78x57 to 96x70. The original oversized sources remain
unchanged, and rebuilding samples those sources directly.

Final human-height revision: Galford maximum height is 106 pixels versus
the human's 109; Haohmaru is 95 versus 97. Other sets use the same height
rule, capped at the retained source size, and already larger sets are kept.
Packing, clipping and native return checks passed for all 14 sets; all seven
enabled characters passed 640 palette variants each. Ground (Galford) and
flight (Ukyo) native integration results are saved separately in
`animality-human-height-native-verification.txt`.
