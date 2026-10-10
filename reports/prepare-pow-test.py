from pathlib import Path
text=Path('reports/fbneo-test-training-roster.lua').read_text()
text=text.replace("local requested,phase_frame=nil,0","local requested,phase_frame=nil,0\nlocal powvalue=0")
text=text.replace("if before then before() end", "if phase=='pow' or phase=='pow-lower' then local a,b=rd(0x100a46),rd(0x100a4a);ww(a+0x4e,150);ww(b+0x4e,390) end\n if before then before() end")
text=text.replace("assert(T.preview(slot));phase='preview';seen=false","phase='pow';powvalue=0;phase_frame=frame;assert(T.pow(slot,-32))")
text=text.replace("elseif phase=='preview' then","""
 elseif phase=='pow' and frame-phase_frame>=4 then
  local actor=slot==2 and b or a
  assert(rb(actor+0xf0)==powvalue,'wrong intermediate POW '..powvalue..' actual '..rb(actor+0xf0))
  if powvalue<32 then
   assert(T.pow(slot,1));powvalue=powvalue+1;phase_frame=frame
  else
   assert(rw(actor+0xb8)>0,'full POW did not start native rage timer')
   assert(T.pow(slot,-16));phase='pow-lower';phase_frame=frame
  end
 elseif phase=='pow-lower' and frame-phase_frame>=4 then
  local actor=slot==2 and b or a
  assert(rb(actor+0xf0)==16 and rw(actor+0xb8)==0,'intermediate POW did not exit full rage')
  print('PASS native POW 0..32 and back to 16 P'..slot..' '..A.definitions[requested].slug)
  -- Isolate the subsequent preview from character-specific rage/recovery poses.
  for _,p in ipairs({a,b}) do ww(p+0xe6,0);ww(p+0xc4,65535);ww(p+0xba,128);ww(p+0xbc,0) end
  assert(T.preview(slot));phase='preview';seen=false
 elseif phase=='preview' then""")
text=text.replace("print('PASS training preview/restore P'..slot","assert(rb(actor+0xf0)==16,'preview reset lost POW selection')\n   print('PASS training preview/restore P'..slot")
Path('reports/fbneo-test-pow-control.lua').write_text("SS2_TRAINING_TEST_SLUG='pow-control'\n"+text)
