# Adjustable POW in training

T enables training. [ decreases P1 POW, ] increases it. Numpad - / + adjusts P2.
The full native range is 0..32 in single-level steps (3.125% of the gauge).
Keys repeat after a 25-frame delay and every 8 frames thereafter. The HUD shows
both current levels. The controls affect only training and a live match.

The native meter is actor+0xf0 and queued meter adjustment is actor+0x114.
The native routine at 0x25cd2 increments/decrements the meter and initializes
the character-specific full-rage duration at actor+0xb8 upon reaching 32.
To reach full POW, the shortcut sets 31 and queues +1 so this routine handles
the normal timer, flags and palette effects. Lowering from full retires the
rage timer and its pending entry flag. Other intermediate values are written
directly and left to normal game behavior. Full POW is not permanently pinned.

An anonymous checkpoint saves after three settling frames. Preview/reset keeps
the chosen POW value. Using the shortcut during a preview restores the practice
position before changing the meter.

Validation:

- reports/training-pow-verification.log: disabled/menu guards, both slots,
  intermediate values, clamping, native full-entry queue, rage exit, slow
  keyboard repeat and checkpoint preservation.
- reports/fbneo-pow-control-test.log: actual native meter values 0..32 for
  every hero in both slots, native full-rage timer, reduction to 16/32, animal
  preview and restoration of the selected meter.
  The fixture separates the fighters while sweeping the meter and resets
  character-specific recovery poses only after verifying the native rage timer
  and reduced meter, before starting the separate animality preview.

Restart the loaded Lua script to use these controls.
