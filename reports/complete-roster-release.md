# Complete animality roster and training character switching

All 17 requested character/animal mappings are enabled in `animalities.lua`.
The seven previously disabled complete sets are now tested and enabled;
Hanzo/Snake, Sieger/Rhinoceros and Mizuki/Spider have new complete sheets.
Galford's fresh v5 wolf is reduced uniformly by exactly 20 percent, using
animal_scale 0.675 instead of 0.84375. Native human frames are unchanged.

Start a match and restart Lua after installing:

| Key | Action |
| --- | --- |
| T | Training on/off |
| J / K | Previous/next P1 character |
| N / M | Previous/next P2 character |
| G / H | P1/P2 animality preview |
| R | Restore current practice checkpoint |

Changing character initializes its native animation/weapon/companion state,
loads the standard costume, and replaces the checkpoint. Switching during a
preview cancels/restores first. Numbered save slots are never overwritten.

New art was created using built-in imagegen with actual native fighter
references, followed by spacing corrections. Generated output is retained;
the pipeline reduces it exactly 2:1 and packs at or below source resolution.
Exact prompts, correction prompts, source PNGs and complete 16-frame reels:

- `assets/hanzo-animality/prompt-v1.txt`, `prompt-v1-spacing.txt`, `source-v1.generated.png`, `source-v1.png`, `reel.png`.
- `assets/sieger-animality/prompt-v1.txt`, `prompt-v1-spacing.txt`, `source-v1.generated.png`, `source-v1.png`, `reel.png`.
- `assets/mizuki-animality/prompt-v1.txt`, `prompt-v1-spacing.txt`, `source-v1.generated.png`, `source-v1.png`, `reel.png`.

Overview: `complete-animality-roster.png`. Authoring and training instructions
are updated in `ANIMALITY-AUTHORING.md`.

Validation passed:

- 272 unclipped frames and 2,720 GD sprites, binary alpha, exact native human endpoints.
- 10,880 exact runtime palette variants (640 per character).
- 17 native fountain/animality/victory/cleanup checks. Eight fixtures earn the native lethal attack; nine enter native death state directly, like training, and do not assert a natural next-round transition.
- 34 actual FBNeo character switches and previews, all 17 for each player, automatic restores retain the chosen fighter.
- Menu/OFF guards, key debounce/wrap, preview interruption, checkpoint replacement, selected-owner helper retirement.
- All 17 stationary preparation/timed takeoff/landing sequences, both directions.

Logs: `complete-roster-verification.txt`, `complete-roster-native-verification.txt`,
`training-roster-live-verification.log`, `complete-training-guard-verification.log`.
Live training capture: `training-roster-preview.gif`.
