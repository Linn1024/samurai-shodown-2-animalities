# Nicotine owl hat palette

The generated straw hat reused skin shades for its stippling and border. Native POW changes skin slots 2–4 to red, which caused red marks on the hat.

`assets/nicotine-animality/hat-palette.bin` tags hat pixels across all 16 frames. The renderer maps these pixels to Nicotine's native straw-hat shades 11–15, following the active body bank and live palette RAM. The remaining owl pixels keep their usual live skin, clothing and weapon mappings. Mirroring happens before camera scaling, so the material tags follow both directions and every camera size.

After changing owl drawings, regenerate the tags with:

```powershell
.\tools\Python\python.exe reports/build-owl-hat-palette.py
```

Review `reports/owl-hat-palette-preview.png`; if the hat moves, adjust the per-frame polygons in that script. The mask includes the straw border and preserves transparency.

Verification: `reports/check-live-animality-palettes.lua` covers all 17 animals, both costumes and player slots, POW bank changes, live red/white flashes and restoration. Its owl-specific checks cover all 16 frames in both directions and assert that tagged pixels use only native hat shades. Actual FBNeo alternate-costume full-POW previews are exercised by `reports/fbneo-test-nicotine-hat.lua` in both player slots.
