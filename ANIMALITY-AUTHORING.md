# Making animalities in this Samurai Shodown II workbench

This guide documents the implementation in `C:\TEMP2\SS2`, using Ukyo's swan as the worked example. Follow the numbered steps to add another character. The current runtime supports Ukyo only; the multi-character structure proposed in step 9 still needs implementing when another animality is added.

The playable effect runs in **FBNeo with Lua enabled**. Lua replaces the winner's drawing with custom sprites, moves the winner during the sequence, synchronizes the strike with the game's native blood fountain, and resumes the native victory animation. It is an emulator mod: the custom animal graphics are not installed into the ROM. HBMAME is useful for capturing and testing the native game, but normal `Play.cmd` does not display the animality overlay.

## 1. Start from the working files

Open PowerShell in the workspace:

```powershell
Set-Location C:\TEMP2\SS2
```

The tools used below are already installed. Python scripts import Pillow from `tools/pillow`; no global Python or Pillow installation is needed.

| File or directory | Purpose |
|---|---|
| [ultimate.lua](ultimate.lua) | Main entry point: F ultimate input, steady shadows, and animality callbacks |
| [animality.lua](animality.lua) | Trigger, native actor suspension, timing, movement, costume colors, rendering, cleanup |
| [ANIMALITY-UKYO.txt](ANIMALITY-UKYO.txt) | Current player instructions and Ukyo reel description |
| [assets/ukyo-animality/](assets/ukyo-animality/) | Native references, source sheet, PNG frames, packed GD sprites, palette map, previews |
| [reports/](reports/) | Capture scripts, asset builders, test fixtures, and verification output |
| [work/hack/](work/hack/) | Editable working ROM files used for research and palette extraction |
| `tools/FBNeo/` | Emulator used to play the animality |
| `tools/HBMAME/` | Emulator used for native captures and Lua research |
| `tools/Python/python.exe` | Portable Python used by asset scripts |

Keep a copy of the working Lua files and the character's asset directory before replacing them. Keep the original ROM ZIPs as inputs. Adding an animality through this workflow does not require running `romtools.py build`.

Create a separate asset directory for each character, for example `assets/haohmaru-animality/`. Copy the relevant build/capture scripts to character-specific names before changing their hardcoded paths. The current builders overwrite Ukyo's files.

## 2. Define the animal and the sequence

Write a short specification before drawing:

- Character name and RAM character ID.
- Animal, silhouette, size, and characteristic movement.
- At least two recognizable features inherited from the character: hairstyle, costume trim, weapon motif, markings, or accessories.
- Attack contact point: beak, claws, bite, horn, etc.
- Required native death animation and intended victory animation.
- Grounded or airborne approach, target height, retreat, and landing.
- Approximate drawing count, hold times, and which drawings can be reused.

For Ukyo, the animal is an ivory swan with his swept-back blue crest, hanging forelock, sash, sword-grip accent, and three hakama-like tail feathers. The sequence is human → transformation → launch → approach → torso strike → recoil → return → human → native victory.

Use actual game art as the visual reference. An animal should remain recognizable as the transformed fighter in both costume palettes.

## 3. Capture the actual character from the game

Use [reports/capture-ukyo-native.lua](reports/capture-ukyo-native.lua) as the capture template and [reports/extract-native-ukyo.py](reports/extract-native-ukyo.py) as the extraction template.

The existing capture fixture:

1. Starts a match and selects Ukyo by writing character ID `5` at the fixture's selection address `0x100D0B`.
2. Resolves the live player pointers at `0x100A46` and `0x100A4A`.
3. Removes player input through temporary write taps.
4. Replaces unrelated palette colors with a known backdrop color to isolate P1.
5. Captures native idle and victory-related poses at known frame numbers.
6. Dumps VRAM for research.

For another fighter, change the selected character, capture timings, output names, and crop rectangle. The palette-isolation cutoff in this fixture is specific to its setup; verify that it retains every palette used by the new fighter. Do not run the isolation fixture in a normal play session: it intentionally changes colors and input handling.

Here is a way to run the existing capture from the workspace in a separate HBMAME process:

```powershell
"dofile('reports/capture-ukyo-native.lua')" | .\tools\HBMAME\hbmame.exe samsho2s29 -rompath tools/HBMAME/roms -pluginspath tools/HBMAME/plugins -nvram_directory reports/test-nvram -video none -sound none -nothrottle -seconds_to_run 75 -console -skip_gameinfo
.\tools\Python\python.exe reports/extract-native-ukyo.py
```

The first command runs an automated fixture, not interactive play. If the match does not reach the expected state, inspect its selection/input timings instead of using the resulting screenshots blindly.

For a manual capture, pause in the desired pose, save a screenshot, remove the backdrop, and crop to the sprite's visible bounds. Preserve the opaque pixels and their colors. Save a transparent PNG, then make a nearest-neighbor enlarged copy for drawing reference.

Ukyo's reference files are `native-idle.png`, `native-idle-reference.png`, `native-kneel.png`, and `native-kneel-reference.png`. The first and last human frames use the captured native idle sprite; the game itself supplies the final victory pose.

## 4. Plan a coherent reel

Ukyo uses 16 drawings. Drawing numbers are zero-based and are separate from elapsed emulation frames.

| Drawing | Pose | Runtime timing |
|---|---|---|
| 00 | Native human stance | Initial 8 emulation frames |
| 01 | Early transformation: mostly human, visibly emerging animal anatomy | 12 frames |
| 02 | Late transformation: mostly animal, visibly remaining human anatomy | 12 frames |
| 03 | Animal at rest | 12 frames |
| 04 | Launch preparation | 10 frames |
| 05 | Wing upstroke | 10 frames initially; reused in flight loop |
| 06 | Wing downstroke | 10 frames initially; reused in flight loop |
| 07 | Glide | Used in flight loop |
| 08 | Torso strike | 7 frames from fountain detection |
| 09 | Recoil | 9 frames |
| 10 | Brake | 9 frames |
| 11 | Land | 9 frames |
| 12 | Rest after landing | 34 frames |
| 13 | Reverse of drawing 02 | 12 frames |
| 14 | Reverse of drawing 01 | 12 frames |
| 15 | Native human stance | 8 frames, then native victory |

After the initial approach, the flight loop uses `05, 07, 06, 07`, holding each for 7 emulation frames until the native fountain appears. This accommodates the game's hit-stop and animation timing.

For a new animal, replace the flight loop with its appropriate running, crawling, jumping, or attack-ready loop. Preserve a waiting phase so impact can synchronize to the native event rather than a fixed timer.

Keep the same body proportions, accessories, palette roles, and anchor throughout. Reuse identical transformation drawings in reverse when that makes sense. Check that the neck, limbs, wings, and body follow continuous arcs between drawings.

## 5. Draw or generate the source sheet

Ukyo's sheet was generated using the built-in image generation tool with the actual native sprite as the reference. The exact prompt is saved in [assets/ukyo-animality/prompt-v2.txt](assets/ukyo-animality/prompt-v2.txt). The accepted source is `swan-source-v2.png`.

Use a drawing editor or generate a new sheet with these requirements:

- Transparent background; no stage, opponent, labels, grid lines, or baked-in ground shadow.
- Strict, evenly spaced grid with one pose per cell.
- Every sprite fully contained in its cell, with space for the widest pose.
- Consistent side view, body size, baseline, and character details.
- Deliberate pixel-art shading with a shared limited palette.
- A clearly listed pose for every cell, in reading order.
- Default costume colors as the source palette; alternate colors are applied later.

Ukyo's generated sheet has **12 cells, arranged 4 × 3**. The builder adds the native human at the beginning and three return drawings at the end to make **16 runtime drawings**. Do not confuse these two counts.

Inspect the source at game size. Grid generation may introduce stray pixels, inconsistent anatomy, or poses crossing cell boundaries. Correct the source or tune extraction before integration. Preserve the source image, reference image, and prompt so another person can reproduce the decisions.

## 6. Normalize and pack the sprites

Adapt [reports/build-animality-assets.py](reports/build-animality-assets.py) for the new directory and source sheet.

The current builder performs these operations:

1. Splits the source into its 4 × 3 cells.
2. Converts alpha below 160 to transparent and the remaining pixels to opaque.
3. Removes connected components smaller than 45 source pixels from generated cells. This is a cleanup heuristic; inspect small intentional details before using the same threshold elsewhere.
4. Crops each sprite to its visible bounds.
5. Reduces generated poses by `0.22` with nearest-neighbor resampling. Adjust this for the new animal's intended game size.
6. Quantizes generated pixels to native character colors plus the selected extra animal shades, without dithering.
7. Places the drawing on a transparent `128 × 128` canvas with logical anchor `(64, 112)`.
8. Prepends the native human frame and appends the reverse transformation and native human.
9. Exports PNG frames, a reel image, a preview GIF, and runtime GD assets.

The current generated-pose horizontal anchor is estimated at 55% of its cropped width. That worked for the swan but is not a universal anatomical anchor. For another animal, choose a stable body point and, if necessary, record an anchor per drawing instead of relying on the estimate. Preview the sequence to catch body jitter.

Each drawing is packed facing right and left at sizes `64, 80, 96, 112, 128`. Sixteen drawings therefore produce **160 GD files**:

```text
gd/right-128-00.gd
gd/right-128-01.gd
...
gd/left-64-15.gd
```

The GD format expected here has:

- An 11-byte header: `FF FE`, big-endian width and height, truecolor flag `1`, transparent value `FFFFFFFF`.
- Four bytes per pixel: **GD alpha, red, green, blue**.
- GD alpha `0` for opaque and `127` for transparent, unlike PNG alpha.
- Total length `11 + width × height × 4` bytes.

Rebuild Ukyo with:

```powershell
.\tools\Python\python.exe reports/build-animality-assets.py
.\tools\Python\python.exe reports/build-animality-palette-map.py
```

Always rebuild the palette map after changing frame colors. The GIF's preview durations are presentation settings; actual gameplay timing is controlled by `animality.lua`.

## 7. Map colors to the fighter's selected costume

Adapt [reports/build-animality-palette-map.py](reports/build-animality-palette-map.py). It creates `palette-map.lua` and `palette-map.json`.

For Ukyo, the default palette starts at game address `0x214600`. The corresponding bytes are at file offset `0x14600` in `work/hack/063sp.p2`, after swapping adjacent bytes in each 16-bit word. The alternate palette used in the tests starts at `0x214700`. **These are Ukyo addresses: discover the new fighter's addresses instead of copying them.**

To discover the selected palette, resolve the fighter's player slot and read the game's eight palette pointers:

| Player slot | Eight 32-bit ROM pointers begin at |
|---|---|
| P1 | `0x10EC40` |
| P2 | `0x10EC60` |

Each pointer names a 16-color palette. Together these eight palettes provide 128 color entries. Capture the pointers while the new character is active, then compare the decoded colors with the native screenshot. Do not assume that every new fighter uses identical color roles or ROM spacing.

The mapper relates each source RGB color to a zero-based native palette entry. For Ukyo, all **19 native human colors match exactly**; the five additional swan shades map to the nearest native colors. Palette index 0 of each 16-color bank is excluded as a source mapping candidate.

Review the mappings by material: hair, outfit, skin, weapon, feathers, and trim. If two materials share one source RGB value but should change independently in an alternate costume, RGB replacement cannot distinguish them. Give them distinct source colors or build an explicit per-pixel palette-index map before proceeding.

At runtime, `select_palette()` reads the actual selected ROM palette entries for the winner's player slot. `colored_sprite()` recolors and caches the packed frames. The cache retains up to four palette signatures. Reading the selected ROM colors avoids copying temporary POW/hit flashes into the animality.

The native reference was captured in HBMAME; its RGB conversion differs slightly from FBNeo's. The builder accounts for the capture colors, while the runtime uses FBNeo's resistor-based RGB conversion. Do not replace this with ordinary RGB555 expansion. Conversion reference: [FBNeo neo_palette.cpp](https://github.com/finalburnneo/FBNeo/blob/master/src/burn/drv/neogeo/neo_palette.cpp).

Keep transparent pixels transparent, and ensure that the first and last human drawings match the selected costume. For new anatomy, manually review any nearest-color choice that makes a highlight or outline change to the wrong material.

## 8. Understand the native trigger and memory layout

The current trigger requires:

1. Two valid player actor pointers.
2. Living Ukyo (`character ID 0x05`, HP greater than zero).
3. Opponent HP equal to zero and native state `0x0318`.
4. Both actors using the expected native callback `0x25314`.
5. A new transition into the fatal state, not the same state on every frame.

It works for either player. A normal KO (`0x0316`) or bisection (`0x0317`) does not trigger this animality. The mod observes the game's chosen death animation; it does not force a fatality during normal play. The exact eligibility/probability rules for every native finishing attack have not been fully traced.

These addresses were researched for this installed **Samurai Shodown II Special 2017** setup. Re-verify them if the ROM or game version changes.

| Address or actor offset | Meaning used by this implementation |
|---|---|
| `0x100A46`, `0x100A4A` | 32-bit P1/P2 actor pointers |
| Actor `+0x00` | Native object callback pointer |
| Actor `+0xF6` | Character ID byte |
| Actor `+0xBA` | HP word |
| Actor `+0xE6` | State word |
| Actor `+0xC4` | Previous-state tracking; set to `FFFF` when entering victory |
| Actor `+0x4E`, `+0x50` | World position fields |
| Actor `+0x5C`, `+0x5E` | Projected screen position |
| Actor `+0x52`, `+0x56` | Movement fields cleared on completion |
| Actor `+0x60`, `+0x62` | Projection offsets cleared on completion |
| Actor `+0x64`, `+0x66` | Native animation group and animation ID |
| Actor `+0x7A` | Camera compression byte |
| Actor `+0x7C`, `+0x7D` | Animation pose/tick bytes used for fountain anticipation |
| Actor `+0x26`, `+0x3A` | Collision-list fields cleared to `FFFF` |
| Actor `+0xCA`, `+0x103` | Collision/attack fields cleared while suspended |
| Actor `+0xF9`, `+0xFB` | State progression bytes reset when entering victory |

Actor pointers are checked for even alignment and range `0x102000` through `0x10FD00`. Words are read and written big-endian. Use signed conversion when interpreting screen/world coordinates. The current initial facing comparison uses raw world words; if extending to positions crossing signed boundaries, update that comparison too.

Use the character-ID table at the top of `ultimate.lua`. Examples: Haohmaru `0x00`, Nakoruru `0x01`, Ukyo `0x05`, Jubei `0x09`, Charlotte `0x0B`, Genjuro `0x0C`, Mizuki `0x10`, Kuroko `0x11`. Do not infer IDs from selection-screen order.

## 9. Add the new character without replacing Ukyo

The present code hardcodes Ukyo in `begin()`, `before()`, and `cancel()`, and hardcodes his asset paths, 16 drawings, swan movement, and log text. Changing just `5` to another ID is insufficient.

For the second animality, introduce a character definition table inside the **single existing animality engine**. A useful design is:

```lua
-- Proposed structure: this is a design example, not a drop-in implementation.
local definitions = {
    [0x05] = {
        name = 'Ukyo Swan',
        assets = 'assets/ukyo-animality/',
        frame_count = 16,
        victory_state = 0x600,
        -- timing, contact offsets, movement function, palette map
    },
    -- [NEW_CHARACTER_ID] = { ... },
}
```

Implement the following changes together:

1. Look up `definitions[character_id]` when a fatality begins; skip characters without a definition.
2. Store the chosen definition and character ID in the active sequence.
3. Load/cache that definition's assets and palette map. Keep frame/zoom/direction keys scoped to the definition so different animals cannot share the wrong cached frame.
4. Validate against the active sequence's character ID instead of literal `5`.
5. Move pose selection, movement, attack contact offset, and return timing into definition-specific data/functions.
6. Use the definition's native victory state after confirming it works for that fighter.
7. Include the animality name in logs.
8. Keep one shared callback owner and one active sequence. Test Ukyo again after the refactor.

Do not register independent `before`, `after`, or GUI callbacks for every animal. FBNeo's registration calls replace callbacks, and overlay clearing by one module can erase another module's drawing. The existing F/shadow integration expects one `api.animality` exposing `before()`, `after()`, `draw()`, `cancel()`, and `status()`.

## 10. Suspend the human actor for one emulated frame at a time

The important ordering is:

```text
before(): validate actors, replace winner callback, clear attack collisions
game frame: native camera projection runs, human drawing/attack logic is skipped
after(): restore native callback FIRST, then advance the animality
draw(): clear the previous overlay, then draw the current animality pose
```

`0x25314` is the normal player callback. During an active animality, `before()` temporarily replaces it with `0x385C`, the native camera-projection routine. `after()` restores the original callback immediately.

Keep this replacement temporary. A saved state between frames should retain the native player callback. Clearing the completed attack's collision fields prevents it from continuing to hit while its normal animation is suspended.

Validate actor identity, character ID, victim HP, and callback before patching. Cancel if the match changes or the victim is revived. Use the existing 600-frame timeout as a recovery path, adjusting it only if the new sequence genuinely requires longer.

## 11. Synchronize contact with the native fountain

The current victim's native fountain animation is `0xE1`. Its first pose lasts 40 native animation ticks. Ukyo begins the final thrust during ticks 32–40, then treats the fountain emitter's appearance as the actual impact event.

`fountain(victim)` walks the linked object list beginning at `0x102000`. It recognizes fountain callbacks `0x4452A` and `0x4456A`, and requires the object's parent pointer at `+0xCC` to match the victim. This avoids synchronizing to an unrelated effect.

The walker follows the low-word next link at `+0x0E`, recognizes the `FFFF` terminator at `+0x10`, tracks visited objects, and caps traversal at 256 objects.

For another animal, retain this event detection if it uses the same native fountain. Adapt the anticipation pose and movement so its contact point reaches the victim's torso when the emitter appears. Do not drive impact solely from wall-clock time or a fixed number of frames after KO; hit-stop can change the delay.

This is a finishing presentation after the opponent has already reached zero HP. The swan strike does not apply a second damage event. Adding a new damaging move during ordinary combat would require a different design.

## 12. Align movement, camera scale, and contact

The current drawing code uses:

```lua
scale = (256 - camera_byte) / 256
screen_x = signed(projected_x)
screen_y = signed(projected_y) - 16
```

The `-16` corrects the Neo Geo visible-area origin for this setup. The runtime selects the nearest packed size from `64, 80, 96, 112, 128` and clamps scale to the supported range. Right-facing anchor X is `64`, left-facing is `63`, accounting for mirroring a 128-pixel canvas; anchor Y is `112`.

For Ukyo:

- The beak is treated as approximately 34 full-size pixels ahead of the animal's origin.
- Target world X is victim X minus facing direction times `34 / scale`.
- The approach initially travels 55% of the distance, then completes the thrust as the fountain animation advances.
- A victim-character lookup estimates torso height; the flight lift subtracts the beak's local vertical offset.
- After impact, the winner returns to its saved starting X and lowers to the ground.

For a new animal, measure the contact point in the actual attack drawing and replace the swan-specific 34-pixel offset and lift behavior. Test short opponents, Earthquake, both facings, and zoomed-out camera positions. The existing height table is an empirical starting point, not a universal collision model.

## 13. Restore native victory and clear every overlay

On successful completion, the current `finish()`:

1. Restores starting world X.
2. Clears movement and projection offsets.
3. Enters state `0x0600` and resets native state progression fields.
4. Releases the active sequence.
5. Explicitly clears the GUI overlay.

Confirm the victory state and progression for each new fighter in a real match, including transition to the next round or opponent. Do not assume a forced test pose proves the full match flow works.

**FBNeo retains the last overlay until it is cleared or replaced.** Returning from `draw()` without drawing does not remove it. This caused the previously reported extra human/transformation sprite.

Keep `gui.clearuncommitted()` at the start of `draw()`, even when inactive, and on initialization, completion, and cancellation. If more overlays are added later, compose them through one GUI callback that clears once and then draws all layers.

The main script also cancels on state load, game restart, and script exit. Loading a state cancels Lua's active sequence; it does not restore its previous animation progress. Mid-animality save/load resumption would require additional Lua state serialization and is not implemented.

## 14. Connect it to FBNeo and check logs

`ultimate.lua` loads the animality module with:

```lua
local factory = assert(loadfile(folder .. 'animality.lua'))(true)
local result = factory(memory, gui)
```

The `true` requests module mode. Without it, selecting `animality.lua` directly in FBNeo starts `ultimate.lua`, so both file choices work. Preserve this distinction to avoid recursive loading.

The integration registers `result.after` and `result.draw`; the main tick calls `result.before`. While an animality is active, it cancels/blocks the F input macro. Keep the existing shadow callback and exit cleanup connected.

To play:

1. Run `Play-FBNeo.cmd` and open the hack (`samsh2sp`).
2. Open FBNeo's Lua Script window.
3. Select `C:\TEMP2\SS2\ultimate.lua` or `animality.lua` and click Run.
4. Confirm startup messages for the F button, shadows, animality, and costume palettes.
5. After editing files, click Restart in the Lua window.

Logs appear in the Lua console and append to [animality.log](animality.log). Log initialization, KO state, skipped triggers with reasons, selected costume palette, sequence start, impact, victory, cancellation, and timeout. Avoid per-frame file writes in the play script. Use a dedicated timeline fixture when researching timing.

## 15. Test the assets and runtime separately

### Asset and palette checks

Confirm every cell fits its canvas, all intended detail survives reduction, and no neighboring sheet pixels leak into a frame. Preview the GIF and both costume reels before running a match.

Existing focused checks can run through HBMAME's Lua console from the workspace:

```powershell
"dofile('reports/check-animality-entry.lua'); dofile('reports/check-animality-cleanup.lua'); dofile('reports/check-animality-palettes.lua')" | .\tools\HBMAME\hbmame.exe samsho2s29 -rompath tools/HBMAME/roms -pluginspath tools/HBMAME/plugins -nvram_directory reports/test-nvram -video none -sound none -nothrottle -seconds_to_run 10 -console -skip_gameinfo
.\tools\Python\python.exe reports/verify-animality-palettes.py
```

These focused tests use the extracted saved RAM snapshot at `reports/fbneo-state-game-ram.bin` and mocked memory/GUI functions. They check entry-point behavior, cleanup, and actual runtime GD recoloring, but they **do not replace an actual FBNeo match test**.

The palette test renders 640 sprites: two costumes × two player slots × two directions × five sizes × sixteen drawings. The Python verifier compares every pixel, alpha byte, and header, and writes `assets/ukyo-animality/costume-palettes-preview.png` and `reports/animality-palette-verification.txt`.

When adding a character, adapt the fixture's ID, palette ROM addresses, source assets, frame count, and expected file names. Add assertions for the new character while retaining Ukyo's assertions.

### Native-game integration checks

Use [reports/test-animality.lua](reports/test-animality.lua) to exercise the native game in HBMAME. It writes a timeline and captures screenshots/overlay bytes. Its mode is read from `reports/animality-test-config.txt`: blank/default, `left`, `p2`, `other`, `normal`, or `cancel`.

Example for one default run:

```powershell
Set-Content -Path reports/animality-test-config.txt -Value '' -Encoding ascii
"dofile('reports/test-animality.lua')" | .\tools\HBMAME\hbmame.exe samsho2s29 -rompath tools/HBMAME/roms -pluginspath tools/HBMAME/plugins -nvram_directory reports/test-nvram -video none -sound none -nothrottle -seconds_to_run 75 -console -skip_gameinfo | Out-File -Encoding utf8 reports/animality-new-run.log
```

Run the other modes separately and give each output log a distinct name. The fixture deliberately chooses state `0318` after a lethal attack so animation development does not depend on native fatality selection. Keep that forced choice confined to test fixtures.

[reports/verify-animality.py](reports/verify-animality.py) checks the existing named integration logs and asset invariants. It does not launch the emulator or regenerate those logs; old passing logs are historical evidence, not proof of a new change. Generate fresh mode logs with its expected filenames or adapt the verifier to the new run names before using it to validate a release.

### Actual FBNeo checks

Run a real FBNeo match and watch the rendered result. [reports/fbneo-test-animality.lua](reports/fbneo-test-animality.lua) is a dedicated automated fixture that loads the main script, selects Ukyo, forces a native fountain after KO, logs events, and pauses at the strike for inspection. Use it in a separate test session started from a fresh game; its timings are not intended for an arbitrary loaded save.

The fixture sets `SS2_NO_MAIN_LOOP=true` because it supplies its own `emu.frameadvance()` loop. Call `emu.pause()` from that main coroutine, not from a registered frame callback: pausing inside a callback previously produced a yield error. Memory write hooks must guard against recursion when writing the address they observe.

Pass this matrix for each animality:

| Case | Required result |
|---|---|
| Correct winner + native fountain | Exactly one complete animality |
| Character without an animality | No custom sequence |
| Normal KO or bisection | No fountain-triggered sequence |
| P1 and P2 winner | Correct actor, costume, and victim |
| Facing left and right | Contact point reaches torso, no anchor jump |
| Default and alternate costumes | Human and animal colors follow selection |
| Short/large victims and camera zoom | Contact height and sprite scale remain plausible |
| Completion | Native human victory, no leftover overlay |
| Save/load, reset, and script restart | Active sequence cancelled cleanly; normal actor callback |
| Next round/opponent | Game continues and controls work |
| F button and shadows | Existing features still work outside the sequence |

## 16. Package the new animality

Keep the following together:

- Updated Lua engine and entry point.
- Character-specific asset directory, including GD files and `palette-map.lua`.
- Native reference, accepted source sheet, prompt or drawing notes, PNG frames, and preview.
- Character-specific build/capture scripts and updated tests.
- A reel table, trigger description, tested cases, and any remaining limitations.

Update the player instructions to list the new supported character. Restart the play script and confirm a real trigger before considering it complete.

## Training and repeatable animality previews

Training is included in the normal FBNeo `ultimate.lua` / `animality.lua` entry
point. Restart the script after installing `training.lua`. Start a match and
select the fighter/costume/stage you want to inspect, then use these keys:

| Key | Action |
|---|---|
| T | Toggle training: refill both health bars, freeze the timer, passive P2 |
| G | Preview the current P1 character's installed animality |
| H | Preview the current P2 character's installed animality |
| R | Restore the practice checkpoint, including during a preview |
| J / K | Previous / next P1 character |
| N / M | Previous / next P2 character |

All 17 roster characters now have enabled animalities, including Hanzo's snake,
Sieger's rhinoceros and Mizuki's spider. Character switching is available in a
live match with training enabled. It wraps through the complete roster,
including Mizuki and Kuroko. Holding a key changes the fighter once.

Changing character loads the standard costume and its native animation bank,
updates the native selection ID and palette pointers, and runs the game's
fighter initialization handler (`252ec` -> `25314`). Old companions and
projectiles owned by that fighter retire through the native `3052` handler;
the other player's owned objects are preserved. The new checkpoint is saved
after initialization completes, so R and automatic preview restores keep the
new fighter. Changing during a preview restores/cancels it before switching.
J/K and N/M do nothing to game RAM while training is off or in menus.

Previews save the current position, enter the victim's native `0318` death state,
and run the ordinary animality engine. The blood fountain and victory remain
native game animations. After the human returns, the victory is shown for
45 frames, then the checkpoint restores both fighters alive. Press G/H again
to repeat; no attack, POW, remaining-health or random-death setup is needed.
Training includes a 180-frame preparation delay to replace the lethal-hit stop
that a direct preview skips. The animal transforms and holds its preparation
pose while the native E1 death animation is paused, then E1 resumes for the
normal takeoff and fountain timing. `training.lua` sets this with
`preparation_frames`. This is a repeatable inspection delay; actual hit-stop
length varies by attack. Training does not change the emulator speed setting.
The victim's native callback is restored after every emulated frame and before
save/load/reset cleanup.
Animalities are available only for characters currently in `animalities.lua`.
The screen and Lua console explain when the selected character has no asset.

Checkpoints use anonymous FBNeo save objects; numbered player save slots are
never overwritten. Each preview captures its own starting position. R can also
restore the initial practice checkpoint before the first preview. Loading an
external save or resetting the game invalidates the old checkpoint; a fresh one
is captured when a live fight is available. T restores an active preview before
turning training off. Training starts off and is FBNeo-only; F retains its normal
POW/move requirements. Turning training off removes the passive-opponent hook.

Implementation: `training.lua` is loaded by `ultimate.lua`; it shares the existing
before/after/GUI/reset callbacks. Dummy input suppression also merges with the
F-button macro. It checks both native fighter handlers before touching game RAM,
so character selection and BIOS startup are left alone.

Validation: `reports/training-live-verification.log` records two consecutive P1
previews, a P2 preview, automatic restores, interruption with R and training OFF
in actual FBNeo. `reports/training-guard-verification.log` checks disabled/menu
guards, held-key debounce, unsupported characters, input merging, checkpoint
reuse, external-load invalidation and hook removal. The live preview recording
is `reports/training-preview.gif`.

Full-roster validation: `reports/training-roster-live-verification.log` records
all 17 native character changes and previews for both player slots (34 events)
in actual FBNeo. `reports/check-training-switch.lua` verifies key debounce,
wraparound, owned-object cleanup, menu/OFF guards, preview interruption and
checkpoint replacement. `reports/complete-roster-verification.txt` checks every
frame, native human pixels and 640 costume variants per character.

The three new sheets use built-in imagegen, with the native character capture
as reference. Sources and exact prompts are in `assets/hanzo-animality`,
`assets/sieger-animality` and `assets/mizuki-animality` (`source-v1.generated.png`,
`source-v1.png`, `prompt-v1.txt`, `prompt-v1-spacing.txt`). The generated
1448x1086 sheets are reduced exactly 2:1, then uniformly fitted to character
height and packed without enlarging a small sprite. Galford's fresh v5 wolf
uses `animal_scale: 0.675`, exactly 80% of the preceding 0.84375 scale.

## Troubleshooting

### Foreground objects on every level

All animalities share `animality-foreground.lua`. It follows the game's native
render queue, including the separate sprite buffers used on alternating frames.
The hook at `3330` records each command's layer and emitted columns after frame
header decoding: queue offset `+4` is the layer, `+6` is the width, and `100B78`
is the current sprite-bank cursor. Native stage foreground commands use layers
`010x`; fighters use `006x`. The mask therefore follows the same foreground
ordering as the original characters, across all 17 backgrounds.

The module mirrors CPU video writes without changing the video registers. It
clips animal pixels only beneath opaque pixels of current foreground columns,
using the original graphics for all 131,072 native tiles. Positions, flips,
hardware shrink, and automatic tile animation are respected. Animated or broken
objects use their current native graphics; removed columns stop masking. There
are no stage-specific screen rectangles or prop lists to maintain.

Rebuild masks with `tools\Python\python.exe reports/build-foreground-masks.py`.
The required runtime files are `animality-foreground.lua`,
`assets/foreground/sprite-opacity.bin`, and `assets/foreground/zoom-y.bin`.
Restart the Lua script after updating them. The video mirror repopulates on the
next game frames and resets with save-state loading, cancellation, or game reset.

`reports/capture-all-stages.py` captures every native background at left, center,
and right camera positions. `reports/check-all-stage-foreground.lua` renders
their masks through the actual Lua module. `reports/verify-all-stage-foreground.py`
independently compares all 51 scenes against raw C-ROM pixels and hardware zoom.
The resulting coverage atlas is `assets/foreground/stage-coverage.png`; magenta
marks native foreground pixels. A zero count means that scene has no foreground
sprite overlapping the visible screen, so it leaves animal pixels untouched.

`reports/check-foreground.lua` verifies bus-width, modulo, wrap, reset, and zoom.
`reports/fbneo-test-foreground.lua` replays
`reports/barrel-stage-test.fs` in an owned test emulator and records a real barrel
overlap. The resulting screenshot is
`assets/haohmaru-animality/foreground-preview.png`.

### Haohmaru size and pounce settings

`assets/haohmaru-animality/build-config.json` keeps the tiger source scale at
`0.33` as the source sampling scale and movement at `crouch_pounce`.
The separate `animal_scale` reduces the final drawing to the character size cap.
Rebuild with `tools\Python\python.exe reports/build-roster-animality.py haohmaru`.
The builder expands the canvas to 192 pixels to fit all poses; it preserves the
native human's original pixel size. The registry's canvas, anchor, and contact
offsets must match the rebuilt assets. `reports/build-roster-registry.py`
calculates these fields and reads the movement setting, but also enables any
other characters whose complete assets are present. Use `--existing-only` to
refresh dimensions and contacts while keeping the current enabled roster.

The `crouch_pounce` movement holds pose 4 after transformation. It waits at the
starting position until the native death animation's final eight wind-up ticks,
then moves in pose 7 and strikes in pose 8 when the blood fountain starts.
Running poses 5 and 6 are deliberately skipped during this wait. Legacy `pounce`
definitions now use the same preparation behavior. Flying animals hold perched
pose 3 until the native wind-up, then use wingbeats 5/6 and thrust pose 7.
Retreat reaches the starting position before planted landing and rest poses.
See `reports/animality-idle-size-review.md` for the size review and checks for
all fourteen existing animal sets.

### Animal size cap (current policy)

Match the animal reel's maximum height to the native human frame 00 height,
using the retained source art. A horizontal animal can be longer than the
standing human: limiting its length to human width or height made wolves and
tigers too small. Existing native-size art is not enlarged beyond its source.
Measure opaque pixels, excluding transparent canvas.
Use one uniform reduction for the entire reel so proportions and relative pose
sizes remain consistent. Human frames 00 and 15 remain unchanged.

Run `tools\Python\python.exe reports/resize-animality-roster.py` to reduce all
existing built sets, refresh contacts, and retain the current enabled roster.
The script stores the display reduction as `animal_scale` in each build config;
both builders apply it only to animal frames with nearest-neighbor sampling.
Native-size source drawings keep `source_scale: 1` and their original raster.
Do not restore the earlier minimum-size enlargement targets.

Review `reports/animality-human-height-comparison.png` and the JSON measurements
in `reports/animality-character-size-cap.json`.
Pre-reduction assets are saved under each animal folder's
`versions/before-character-size-cap` directory.

### Matching the original sprite style

For new game-size drawings, use `native_size_source: true`, `source_scale: 1`
and the exact `source_size: [width,height]` in the build config. This prevents
later enlargement of a finished small pixel sprite. Inspect at actual game size
and compare against the previous frames before installing. A review candidate
can be built with `--asset-dir reports/<candidate-folder>`. The wolf example and
its generator-output normalization are documented in
`reports/galford-native-redraw.md`; its standing pose is reused on return using
`repeat_stand: true`.

Use the native fighter capture as the style reference and the existing sheet as
the pose reference. Favor broad pixel clusters, a few tones per material, and
selective colored contours. Avoid a continuous black perimeter, noisy tiny fur
details, smooth gradients, and an opaque shadow beneath the animal. Preserve
intentional dark hair, stripes, pupils, and deep interior shadows.

Save revised sheets and their prompts as `source-v2.png` / `prompt-v2.txt` (or the
next version). Set `source_file` in the animal's `build-config.json`; keep the
existing `source_scale` and movement unless a size or timing change is intended.
Rebuild the assets, measure the strike contact from the new impact frame, and
update its registry entry. An optional `contact: [x,y]` in the config preserves
that contact when regenerating the registry. Review the final costume-mapped
FBNeo render, since quantization can change the apparent edge contrast. Restart
the Lua script to discard cached old sprites. See
`reports/animality-style-review.md` for the tiger/wolf redraw and checks.

| Symptom | Check |
|---|---|
| No startup logs | Correct Lua file path; Run/Restart; direct-entry versus module mode |
| KO logs but no animality | Winner ID, HP, callback, and victim state; `0316`/`0317` are not `0318` |
| Asset load error | Character asset path, every packed filename, and palette-map presence |
| Human remains visible underneath | `before()` callback runs; native callback is replaced only during the frame |
| Extra pose remains after victory/load | Explicit `gui.clearuncommitted()` on inactive draw and all cleanup paths |
| Animal changes size or jumps | Shared anatomical anchor, cell cropping, scale selection, and mirror anchor |
| Strike misses torso | Measured contact offset, facing, camera scale, victim-height estimate |
| Blood begins before contact | Native tick anticipation and correct victim-parent emitter detection |
| Alternate colors look wrong | Selected player slot, palette pointers, material mapping, RGB conversion |
| Palette changes have no effect | Rebuild palette-map and Restart; cached frames belong to the old script run |
| Controls or match flow remain frozen | Callback restored in `after()`, cancellation path, native victory progression |
| HBMAME does not show custom animal | Expected for normal play; custom overlay runtime is FBNeo |

## Distinct transformation artwork (current revision)

Two separate files are insufficient if both already depict a complete animal.
Review 00 -> 01 -> 02 -> 03 together at actual game size: frame 01 must show
an early hybrid and frame 02 a visibly later hybrid. A pose change alone does
not count. Preserve identity, costume colors, body scale and foot baseline.
See reports/distinct-transformations-v2.md for current art, exact prompts,
import steps, backup locations and verification logs.

For a transition-only redraw, use the original human and existing full animal
as reference endpoints. Generate two distinct hybrid drawings. Import with
reports/prepare-distinct-transformations.py. The roster builder accepts two
normalized PNGs through transformation_overrides in build-config.json and
preserves the shared canvas with canvas_size. Overrides are included before
palette-map generation and before copying frames 02/01 into reverse frames
13/14. Do not overwrite only frame-01.png/frame-02.png: rebuild GD files,
palette maps and previews together. Ukyo uses its separate swan builder.

Sieger now uses source-v2.png, a fresh living-rhino design referenced only from
his native human sprite. Its full twelve-pose sheet replaces the old rhino.
The seven other updated characters retain their existing attack drawings.


## Galford fresh wolf v6

Galford now uses source-v6.png and versions/fresh-v6-size-reference. The complete
sheet was generated anew from only the original human reference; prior wolf
artwork was not inspected. Both hybrid stages and all animal poses are new.
See reports/galford-fresh-v6.md for exact prompts, import steps and verification.


## Human idle continuity (v3)

Nicotine, Sieger, Haohmaru and Genjuro use idle-morph-v3-01.png / -02.png
through transformation_overrides. The first morph must inherit the native
idle stance, weapon position, overall height and foot baseline. Begin anatomy
changes before lowering the posture. Interpolate the second morph toward the
animal, and keep a recognizable remaining human feature. Do not anchor every
hybrid at 55% of its width: a staff or raised gauntlet shifts the bounding box
without shifting the fighter. Use the native actor-to-bounds ratio for the early
pose and interpolate it toward the animal for the later pose.

See reports/idle-morph-v3.md for prompts, sources, exact alignment measurements,
installer, unchanged-frame checks and FBNeo validation.

## Capture complete native humans

Palette isolation alone is insufficient: an opponent recolored as the backdrop
still covers the fighter before transparency extraction. This produces gaps in
feet, hands, clothing and weapons. Suppress opponent rendering with the verified
projection-only actor handler 0x385c in an isolated capture fixture. Keep the
original actor positions and camera zoom; moving the opponent far away changes
the zoom and invalidates pixel comparisons.

Use reports/capture-animality-roster.lua for new captures; it now hides the
opponent fully. Check the extracted pixels in actor coordinates against a second
opponent-free capture. Confirm complete hands, feet, weapon shafts/blades and
accessories. Never use generated art to fill missing original game pixels.

All 17 installed human endpoints were audited and repaired in
reports/complete-native-roster-repair.md. Human frames 00/15 must match the clean
native sprite; preserve the generated frames when repairing native captures.
Ukyo's dedicated builder reads native_anchor from build-config.json rather than
assuming the old cropped sprite origin.

## Training palettes and animal recoloring

With training enabled (T), O toggles P1's main/alternate palette and P toggles
P2's. J/K and N/M character changes preserve that choice. Reset restores the
selected palette; changing palette during a preview first restores the practice
position. Holding O or P toggles once per press.

Animals share one set of drawings across both costumes. During packing, each
used RGB shade is mapped to the nearest nontransparent slot in the hero's native
128-color palette. The mapping is saved in palette-map.lua. At runtime the engine
reads the live fighter palette RAM (P1 0x400200, P2 0x400300) each draw and
substitutes the same slot's current displayed color, including POW effects and
hit flashes. Original human colors match exactly;
generated animal shades use their assigned nearest native slot. This is automatic
color substitution, so it does not independently art-direct fur, horn, armor or
cloth colors. All frames and camera sizes use the same selected palette.
When live colors change, recolored camera caches are invalidated immediately;
returning to normal colors cannot reuse a stale POW or flash tint.
The native renderer also changes palette banks without changing their RGB words.
Follow actor+0x81 for the body/skin bank (0/1/2, with the player-slot offset
removed) and actor+0x82 for the weapon bank. Include both selectors in the cache
signature. Reading palette RAM alone is insufficient: alternate Gen-an can have
purple base skin while his selected full-POW skin bank is orange.

## Training POW adjustment

Enable training with T. Use [ / ] to decrease/increase P1 POW, or numpad - / +
for P2. Every press moves one native level (0..32); holding starts repeating
after 25 frames, then once per 8 frames. The HUD shows each player's raw level.
Full POW enters through the game's native meter update, so its timer/tint and
rage animation initialize normally. Reducing below full clears the active rage
duration. Intermediate values are not forced to minimum or maximum each frame.
The practice checkpoint updates after three settling frames so R and preview
restoration keep the selection. Full POW can still expire naturally.
See reports/training-pow-control.md for implementation and verification.

Nicotine's owl also has a per-pixel hat material map. After rebuilding its frames, run `.\tools\Python\python.exe reports/build-owl-hat-palette.py` and review the generated hat preview. See [owl hat palette notes](reports/owl-hat-palette-fix.md) for the mask format and verification. This keeps straw details out of the POW skin shades.
