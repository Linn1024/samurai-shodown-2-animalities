# Live fighter palette colors

Animality rendering now reads the hero's current displayed palette from RAM:
P1 0x400200 through 0x4002ff, P2 0x400300 through 0x4003ff.
It no longer derives the visible colors from the base costume ROM pointers.
All 128 colors are sampled on every draw, including during the transformation
and return to human form. If the game applies POW tints or other palette flashes
to these colors, the animal follows those changes on its next draw.

The existing source-shade-to-native-slot mapping stays unchanged. Generated
artwork, dimensions, movement, timing and palette toggle controls are unchanged.
The four-entry recolor cache uses a signature of the actual live color words.
Any change invalidates the active camera-size cache, preventing stale colors
at reduced zoom levels. Logging reports the player's live palette RAM address
once at the start of the animality.

Validation:

- reports/live-palette-verification.log: 4896 render checks across all 17 heroes,
  both player slots, both costumes, both directions, three sizes and human,
  animal and attack frames. Test palettes transition from main/alternate colors
  to red, to white, and back. Alpha stays unchanged and original colors return
  exactly. ROM pointers deliberately disagree with live alternate colors to
  prove that the renderer uses RAM. These color-transition fixtures simulate
  changes to palette RAM; they do not claim to trigger every native POW event.
- reports/fbneo-palette-toggle-test.log: 34 actual FBNeo character-switch,
  main/alternate toggle, animal preview, reset and native victory checks.

The legacy palette fixture now initializes live palette RAM as well as ROM
pointers, so future packing/zoom checks exercise the displayed color source.

Restart the loaded Lua script to activate live palette following.
