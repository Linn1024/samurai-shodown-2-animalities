# Follow native POW bank selection

The first live-palette implementation read the displayed palette RAM words but
missed the renderer's bank selectors. POW can change the selected bank while all
RAM color words stay unchanged. This caused alternate Gen-an's bat to remain
purple even though his native skin was orange. It affected the shared renderer,
not just training.

Native routine 0x25d3e selects actor+0x81 based on the POW meter: 0 for 0..9,
1 for 10..19, 2 for 20..32 (plus 8 for the other player). Actor+0x82 selects
the weapon bank. The render-command builder at 0x3642 uses the selector table
at 0x3656 (0x81, 0x82, 0x83). Sprite output adds that selector to tile palette
attributes. The overlay now accounts for body and weapon selectors as well as
live RGB values, and invalidates scaled-frame caches when either changes.

This preserves drawings and automatically applies to every animality. No redraw
or alternate-palette-only special case was used.

Validation:

- reports/live-palette-bank-verification.log: 5304 checks across all 17 heroes,
  both slots and both costumes. Includes all three body banks and both weapon
  selectors, plus live RGB flashes and restoration. Alternate Gen-an must produce
  different bat colors at each POW bank.
- reports/fbneo-genan-live-banks-test.log: actual FBNeo alternate Gen-an at full
  POW, native bank 2, both player slots, animality and checkpoint restoration.
- reports/preview-genan-live-banks.py checks that the orange skin colors from the
  actual native POW palette appear in both captured animal overlays.
- [Native hero / animal comparison](genan-live-bank-comparison.png).

Palette mock fixtures now use a stable research RAM snapshot rather than the
user's latest save, which can be taken during a transition. The user's numbered
save was read without modifying it.

Restart the loaded Lua script in FBNeo to activate the fix.
