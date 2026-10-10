from pathlib import Path
text=Path('reports/fbneo-test-training-roster.lua').read_text()
text=text.replace("assert(rd(ptr)==d.palette,'wrong costume pointer')", """
  local prior=rd(ptr)
  assert(prior==d.palette or prior==d.palette+256,'invalid initial costume')
  assert(T.palette(slot))
  assert(rd(ptr)==(prior==d.palette and d.palette+256 or d.palette),'toggle did not change costume')
  assert(T.palette(slot) and rd(ptr)==prior,'toggle back failed')
  if prior==d.palette then assert(T.palette(slot)) end
  assert(rd(ptr)==d.palette+256,'alternate palette required for preview')
  for bank=0,7 do assert(rd(ptr+bank*4)==d.palette+256+bank*32,'palette bank not toggled') end
  print('PASS palette toggle P'..slot..' '..d.slug)
""")
text=text.replace("print('PASS training preview/restore P'..slot", """
   assert(rd(slot==2 and 0x10ec60 or 0x10ec40)==A.definitions[requested].palette+256,'reset lost toggled palette')
   print('PASS training preview/restore P'..slot""")
Path('reports/fbneo-test-palette-toggle.lua').write_text("SS2_TRAINING_TEST_SLUG='palette-toggle'\n"+text)
