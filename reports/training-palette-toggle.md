# Training palette shortcuts

Enable training with T. O toggles P1's main/alternate palette; P toggles P2's.
The training HUD displays both shortcuts. Holding a key toggles only once.
Character switches retain the selected variant. Reset and automatic preview
restoration retain it as well.

Changing palette during a preview first restores the practice position, then
applies the requested palette. Menu/OFF/loading guards prevent inappropriate
memory writes. Palette switching updates all eight native bank pointers and
the live palette colors, then replaces the anonymous practice checkpoint.
It preserves the current hero and position.

The animals use one drawing set. Each source RGB shade maps to the nearest
nontransparent native hero palette slot at build time. At runtime that slot is
read from the selected costume's eight ROM palette banks. Thus costume changes
recolor human, intermediate and animal frames consistently without generating
a second set of drawings. This is automatic palette substitution, not separate
art direction for fur, horns, armor or cloth.

Validation:

- reports/training-palette-toggle-verification.log: OFF/menu guards, keyboard
  debounce, independent player slots, checkpoint preservation, and cancellation
  of an active preview before a palette change.
- reports/fbneo-palette-toggle-test.log: main/alternate/back toggles for all 17
  heroes in both player slots, eight-bank pointer checks, animal previews,
  palette retention after reset and return to native victory.

Restart the loaded Lua script to activate O/P.
