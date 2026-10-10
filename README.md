# Samurai Shodown II animalities

FBNeo Lua mod for **Samurai Shodown II Special 2017 v1.1** (`samsh2sp`), with animalities for all 17 playable characters, a training mode, a one-button ultimate, and steady translucent shadows.

## Play

1. Install the Windows version of [FinalBurn Neo](https://github.com/finalburnneo/FBNeo) with Lua support. Supply your own compatible game ROMs and Neo Geo BIOS.
2. Clone or download this repository. Keep the Lua files and `assets` directory together.
3. Copy `support/blend/samsh2sp.bld` to FBNeo's `support/blend` directory. Enable alpha blending and 32-bit color, then reopen the emulator/game.
4. Load `samsh2sp`, open FBNeo's Lua Script window, and run `ultimate.lua` from this repository. Opening `animality.lua` also launches the complete mod.
5. For playable Kuroko and Mizuki, set **CHARACTER SELECT → ALL** in the hack's start menu.

Animalities activate when a supported living winner's opponent reaches zero HP and the game's blood-fountain finish state (`0318`). They return to human form and the native victory animation. Training previews reproduce the same sequence without needing to earn the finish.

## Controls

| Key | Action |
| --- | --- |
| F | P1 weapon-breaking ultimate; normal POW and move requirements apply |
| T | Toggle training during a match |
| G / H | Preview P1 / P2 animality |
| R | Restore the practice position |
| J / K | Previous / next P1 character |
| N / M | Previous / next P2 character |
| O / P | Toggle P1 / P2 main and alternate palettes |
| [ / ] | Decrease / increase P1 POW by one level |
| Numpad − / + | Decrease / increase P2 POW by one level |

POW ranges from 0 to 32. Hold its controls to repeat. Character switching preserves costume selection; animals follow the displayed live palette and POW bank. Animalities appear behind native foreground props and HUD graphics, including POW signs.

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

## Edit and verify

[ANIMALITY-AUTHORING.md](ANIMALITY-AUTHORING.md) describes sprite creation, transformations, palette mapping, integration and emulator verification. Current sources, frame PNGs, packed GD sprites and palette maps are under `assets/<character>-animality`. `reports` contains development scripts and notes; their generated captures, ROM dumps and local fixtures are excluded.

Building artwork requires Python 3 and Pillow (`python -m pip install Pillow`). Run scripts from the repository root with your installed Python. Some development scripts also require local FBNeo/HBMAME installations and fixtures at the workbench paths documented in the authoring guide; they are not self-contained CI tests.

`romtools.py` optionally prepares a local ROM workbench from your own archives. It is not needed to run the Lua mod. No game/BIOS ROM archives, emulator executables, save states, credentials or old artwork versions are included.

The mod is an emulator overlay; it does not insert the custom animation graphics into the ROM. The full animality renderer requires FBNeo's GUI/Lua API. Historical HBMAME launch instructions in the workbench notes apply to the local development setup.
