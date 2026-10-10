# Two distinct transformation stages and a fresh Sieger rhinoceros

Every character uses human (00), early hybrid (01), late hybrid (02), and
complete animal (03). Both intermediate drawings remain on screen for 12
game frames each. There are still 16 drawings in the complete animality.
Runtime timing, POW rules, training controls and foreground masking are unchanged.

The seven weak transitions were replaced using built-in imagegen:

| Character | Early stage | Late stage |
| --- | --- | --- |
| Hanzo | Human ninja upper body, one remaining human leg, emerging tail | Snake head and coiled body, one remaining reduced human arm |
| Nicotine | Human monk face and hands, feathered forearms | Owl face and wing structure, remaining hand and robe |
| Wan-Fu | Human body, legs and hands, early trunk and ears | Broad elephant body and longer trunk, remaining changing fingers |
| Mizuki | Human face and clothes, extra limbs emerging | Spider body and abdomen, remaining human forearms and face detail |
| Cham Cham | Human face and torso, changing hands and crouching legs | Monkey muzzle, elongated limbs and monkey haunches |
| Jubei | Human samurai head and arms, emerging shell | Turtle head and broad shell, remaining white-sleeved front limbs |
| Kuroko | Human hooded referee with hands, feathered sleeves | Raven beak and wings, remaining fingertips and changing legs |

Haohmaru, Nakoruru, Galford, Ukyo, Kyoshiro, Gen-an, Earthquake, Charlotte
and Genjuro retain their existing distinct early/late stages. Their files
were visually reviewed alongside all replacements in transformation-review-v2.png.

Sieger's entire twelve-drawing source was generated afresh, using ONLY his
original native game sprite as the initial image reference. The discarded
animal was not supplied to the generator. The new design has living purple
rhino anatomy, a red neck sash and a small brass foreleg cuff. It attacks with
its horn. Both initial human/rhino hybrids are new. A second imagegen pass
fixed sheet spacing using only the newly generated sheet.

All requested game assets are installed under assets/<slug>-animality/.
Seven transition pairs: transform-v2.generated.png (raw), transform-v2-01.png
and transform-v2-02.png (normalized), prompt-transform-v2.txt, build-config.json.
Sieger: source-v2.generated.png (raw 1447x1087), source-v2.png (723x543),
prompt-transform-v2.txt (initial generation), prompt-v2-spacing.txt, reel.png.
Sources are generated bitmap art, normalized by nearest-neighbor reduction,
hard alpha and native palette quantization; no procedural drawing substitutes.

Exact prompt set and original generator paths: transformation-generation-v2.json.
Importer: prepare-distinct-transformations.py; run without arguments to stage
candidates, inspect transformation-review-v2.png, then --install to install.
The roster builder supports transformation_overrides in build-config.json,
applies them before the reversed return frames and includes them in palette maps.
The existing attack frames 03-12 are byte-identical for the seven pair-only
replacements. Original human frames 00/15 remain byte-identical for all eight.
Sieger's new sizing baseline is versions/fresh-rhino-v2-size-reference.
Backups are versions/before-distinct-transformations-v2 in each changed folder.

Validation logs: distinct-transformations-verification.txt (eight changed
sets and 5,120 runtime costume variants), test-sieger-animality-default.log,
test-sieger-animality-left.log, test-sieger-animality-p2.log,
distinct-transformations-fbneo-live.log, complete-training-guard-verification.log.
All eight changed sets passed packed-asset checks and all 5,120 costume
variants. All 17 passed exact reversed-transformation checks, stationary
waiting, takeoff and landing checks. A fresh actual FBNeo training run passed
34 previews/switches/restores: all 17 animalities for each player. Sieger's
native finish passed default, left-facing and P2 fixtures using direct
native death-state entry. The older single-character FBNeo attack fixture
did not earn Sieger's KO; the subsequent complete training run above verifies
his actual FBNeo sequence successfully for both players.
