# Samurai Shodown II animalities

An FBNeo Lua mod for **Samurai Shodown II Special 2017 v1.1** (`samsh2sp`). It adds animal finishing animations for all 17 characters, a keyboard shortcut for weapon-breaking specials, and steady translucent shadows.

## What the mod does

- **Animalities:** the winning fighter transforms into their animal, attacks during the opponent's native blood fountain, returns to human form, and plays the game's victory animation. Either player can perform one.
- **Live colors:** animal sprites follow the fighter's selected costume and live POW palette.
- **Scene integration:** animations follow camera zoom and appear behind stage foreground objects and the HUD, including POW signs.
- **Ultimate shortcut:** press **F** for Player 1's weapon-breaking special. Normal POW and move requirements still apply.
- **Steady shadows:** ground and airborne shadows use constant translucency instead of blinking when the supplied blend table is installed.

This is a running Lua overlay. Keep the script running while playing; it does not permanently patch your ROM. Training mode is not included in the GitHub distribution.

## What you need

| Requirement | Details |
| --- | --- |
| Windows PC | The complete mod is intended for the Windows standalone FBNeo application. |
| FinalBurn Neo with Lua support | Download a Windows build from the [official FBNeo releases](https://github.com/finalburnneo/FBNeo/releases). It must recognize the `samsh2sp` game and provide the Lua Script window. |
| Compatible game ROM set | **Samurai Shodown II Special 2017 v1.1**, short name `samsh2sp`. An ordinary Samurai Shodown II set is not the target for this mod. |
| Neo Geo BIOS and any required parent ROMs | Supply the files requested by FBNeo's ROM audit for your set. |
| This repository | Download and extract the complete project, including `assets` and `support`. |

Game ROMs, BIOS files and the emulator are supplied separately. **Python, Pillow, Git, HBMAME and image-generation tools are not required to play.** All runtime artwork is already included. The full renderer needs FBNeo's GUI/Lua API; use the standalone application for this installation.

## Installation

1. **Extract FBNeo** into a writable folder and run it once.
2. **Install your game and BIOS files.** Put the ROM ZIPs in FBNeo's `roms` folder, or configure a ROM search path in the emulator. Keep the ROM archives zipped. Refresh the game list, audit the set, and confirm that `samsh2sp` starts successfully before loading the mod. Resolve any missing-ROM messages first.
3. **Download the mod.** On this repository's GitHub page, choose **Code → Download ZIP**, then extract it completely. You can also clone the repository. A simple writable path such as `C:\Games\SS2-Animalities` is suitable. Keep `ultimate.lua`, `animality.lua`, `animalities.lua`, `animality-foreground.lua` and the complete `assets` folder together.
4. **Install the shadow blend table.** Copy this project's `support\blend\samsh2sp.bld` into `<your FBNeo folder>\support\blend\samsh2sp.bld`. Create the directories if needed. If you configured a custom blending-table support path in FBNeo, use that location instead.
5. **Enable shadow blending.** In FBNeo's video settings, enable alpha blending and 32-bit color output. Close and reopen the game after installing the blend table so it is loaded.
6. **Start the game and script.** Load `samsh2sp`, open FBNeo's **Lua Script** window, browse to the extracted project's **`ultimate.lua`**, then click **Run**. Selecting `animality.lua` directly also starts the complete mod. Run one entry script at a time.
7. **Check startup.** The Lua output console should show `Ultimate button ready`, `Shadows v2`, and `Animalities ready`. Keep the script running. Start it again when you begin a new emulator session; restart it after updating the mod's files.
8. **Enable the boss characters if desired.** In the Special 2017 hack's start menu, set **CHARACTER SELECT → ALL** to make Kuroko and Mizuki selectable. This option belongs to the base ROM hack.

Example layout after installation:

```text
C:\Games\FBNeo\
    fbneo64.exe                 (or the executable in your build)
    roms\                       (your game and BIOS archives)
    support\blend\samsh2sp.bld   (copied from this project)

C:\Games\SS2-Animalities\
    ultimate.lua                (select this in the Lua Script window)
    animality.lua
    animalities.lua
    animality-foreground.lua
    assets\                     (keep the entire folder)
```

## How to trigger an animality

Win with the game's **blood-fountain finish**. The mod automatically detects a living supported winner and an opponent with zero HP in the native fountain death state (`0318`), then plays that winner's animality.

There is no separate animality button. Ordinary hit blood, regular knockouts and body-splitting finishes do not trigger it. The mod follows the game's finish selection; it does not make every KO a fountain. **F is the weapon-breaking special shortcut, not an animality trigger.**

## Controls

| Key | Action |
| --- | --- |
| F | P1 weapon-breaking ultimate; normal POW and move requirements apply |

## Characters

| Character | Animal |
| --- | --- |
| Haohmaru | Tiger |
| Nakoruru | Hawk |
| Ukyo | Swan |
| Charlotte | Peacock |
| Jubei | Turtle |
| Hanzo | Snake |
| Galford | Wolf |
| Genjuro | Leopard |
| Cham Cham | Monkey |
| Earthquake | Boar |
| Wan-Fu | Elephant |
| Gen-an | Bat |
| Sieger | Rhinoceros |
| Nicotine | Owl |
| Kyoshiro | Fox |
| Mizuki | Spider |
| Kuroko | Raven |

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Game is missing from the list or fails its ROM audit | Use a build that supports `samsh2sp`, configure the ROM path, and supply the specific game, BIOS and parent files requested by the audit. The Lua mod cannot fix a missing ROM set. |
| There is no Lua Script window | Use a Windows standalone FBNeo build with Lua support. |
| Lua reports a missing file or asset | Extract the complete project and keep the original folder structure. Select `ultimate.lua` using Browse rather than entering a quoted path. |
| No animality after a KO | Confirm that the script is running and the finish is the blood fountain. Check the Lua console or `animality.log` beside the script for the trigger or skip reason. |
| Shadows blink or appear opaque | Confirm the script is running, the blend table is in FBNeo's active support path, and alpha blending and 32-bit color are enabled. Reopen the game after changing these settings. |
| DirectDraw7 Software Effects cannot initialize | Select another available video output module in FBNeo's video settings and restart the emulator. This is an emulator video initialization issue. |

## Edit and verify

[ANIMALITY-AUTHORING.md](ANIMALITY-AUTHORING.md) describes sprite creation, transformations, palette mapping, integration and emulator verification. Current sources, frame PNGs, packed GD sprites and palette maps are under `assets/<character>-animality`. `reports` contains development scripts and notes; their generated captures, ROM dumps and local fixtures are excluded.

Building artwork requires Python 3 and Pillow (`python -m pip install Pillow`). Run scripts from the repository root with your installed Python. Some development scripts also require local FBNeo/HBMAME installations and fixtures at the workbench paths documented in the authoring guide; they are not self-contained CI tests.

`romtools.py` optionally prepares a local ROM workbench from your own archives. It is not needed to run the Lua mod. No game/BIOS ROM archives, emulator executables, save states, credentials or old artwork versions are included.

The mod is an emulator overlay; it does not insert the custom animation graphics into the ROM. The full animality renderer requires FBNeo's GUI/Lua API. Historical HBMAME launch instructions in the workbench notes apply to the local development setup.
