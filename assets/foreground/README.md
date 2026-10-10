# Native foreground masking

Restart the FBNeo Lua script to load updates. All animalities use this renderer;
no per-character or per-stage mask setup is needed.

`sprite-opacity.bin` stores all 131,072 native C-ROM tiles as sixteen little-endian
16-bit opacity rows per tile (4 MiB total). `zoom-y.bin` is the native hardware
vertical shrink table. `animality-foreground.lua` reads these files and follows
the game's foreground render commands, including animated and broken objects.

The previous barrel-only list is kept as a research reference; the runtime no
longer reads `barrel-masks.lua`.

The native renderer at ROM address `3330` has decoded the frame header but has
not yet emitted the sprite columns. A read-only execution hook records the
command's layer at `A6+4`, its width at `A6+6`, and bank cursor at `100B78`.
Recording ownership during emission keeps both alternating video buffers aligned
with their actual graphics. Layers `010x` represent foreground stage objects;
fighter commands use `006x`. Video write hooks mirror graphics RAM without
changing the game's video registers.

`fixed-opacity.bin` stores eight opacity bytes per native 8x8 S-ROM tile.
The renderer also clips under the live fixed-layer tilemap at VRAM `7000`,
so POW signs (including full-POW flashes), meters and other HUD graphics stay
above every animality. Only opaque glyph pixels mask the animal; the gaps
around the sign stay transparent. This uses the same shared renderer on every
stage and for both players. See `reports/pow-hud-verification.log` for independent
raw S-ROM pixel checks against normal and full-POW tilemaps captured from FBNeo.

Validation covers all 17 backgrounds at three camera positions (51 scenes),
compared independently against the raw C-ROM transparency and hardware shrink
table. See `reports/all-stage-foreground-verification.txt` and
`stage-coverage.png` (magenta marks native foreground pixels).

Rebuild: `tools\Python\python.exe reports/build-foreground-masks.py`.
The detailed capture and verification workflow is in `ANIMALITY-AUTHORING.md`.
