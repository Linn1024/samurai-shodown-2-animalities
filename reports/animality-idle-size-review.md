# Animality idle and size review — 2026-10-10

All fourteen existing animal sets were reviewed and rebuilt. Seven remain enabled.
Snake, rhinoceros and spider do not yet have completed assets.

Ground animals hold preparation pose 4; flying animals hold perched pose 3.
They stay at their starting position and ground height until the native E1
animation's final eight wind-up ticks. Ground animals then use pounce pose 7;
flyers use wingbeats 5/6 and thrust pose 7. Legacy `pounce` definitions receive
the same fix. Retreat now completes before planted landing/rest poses, preventing
sliding on return.

All dimensions below are opaque impact-pose bounds at native zoom. Original
human pixels remain unchanged. No animal was reduced. These are deliberate
arcade display sizes: small species are exaggerated for clarity, while large
beasts have greater bulk. Standing height and strike width both inform scale.

| Animal | Before | After |
|---|---:|---:|
| Tiger | 118 x 81 | 118 x 81 |
| Wolf | 71 x 51 | 124 x 89 |
| Elephant | 90 x 50 | 185 x 104 |
| Boar | 84 x 53 | 160 x 100 |
| Leopard | 77 x 54 | 135 x 95 |
| Fox | 78 x 52 | 110 x 74 |
| Turtle | 82 x 41 | 115 x 57 |
| Monkey | 75 x 56 | 100 x 75 |
| Bat | 76 x 39 | 115 x 60 |
| Hawk | 71 x 55 | 95 x 74 |
| Peacock | 69 x 53 | 105 x 80 |
| Owl | 75 x 44 | 105 x 61 |
| Raven | 69 x 47 | 102 x 69 |
| Swan | 67 x 33 | 107 x 51 |

See `animality-size-overview.png` for native humans and animals at identical zoom,
and `animality-size-review.json` for source scales, standing sizes and original
human pixel hashes. Build configs preserve the sizes and movement; registry
contact offsets were measured again after resizing. Use
`build-roster-registry.py --existing-only` to refresh the enabled roster safely.
Ukyo's builder now supports configurable source scale and canvas size too.

Existing artwork was resized/repacked through the builders; no new drawings.
Validation:

- `animality-waiting-verification.log`: all fourteen built definitions, both
  directions, 180-frame stationary wait, timed takeoff, strike, no resting slide,
  cleanup and restored native callbacks.
- `resized-assets-verification.txt`: correct GD dimensions and unclipped frames
  for all fourteen; 640 runtime images per enabled character checked across two
  costumes, both players/directions and five zoom levels.
- `resized-roster-native-verification.txt`: native integration for all seven
  enabled characters. `resized-galford-modes-verification.txt`: wolf also checked
  left-facing, P2, ordinary KO and cancellation.
- `assets/galford-animality/fbneo-live-finish.gif`: actual FBNeo enlarged wolf,
  native fountain and restored human victory.

Restart the Lua script in FBNeo to load the assets and movement changes.

Follow-up: a coarse pixel-grid experiment was rejected and fully reverted.
All five affected beasts (tiger, wolf, boar, elephant, leopard) now use the exact
pre-experiment sprite sheets at their enlarged sizes. No replacement artwork
from that experiment is installed. `sprite-detail-restoration.txt` records the
byte-identical sheet comparisons and hashes. Training now includes its missing
preparation wait: the live preview fountain begins at frame 232 instead of 52,
with a stationary preparation pose visible at frame 100. This controlled delay
is for animation inspection; actual finishing-attack hit-stop varies.
