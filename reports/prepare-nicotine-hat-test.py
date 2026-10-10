from pathlib import Path
text=Path('reports/fbneo-test-pow-control.lua').read_text()
text=text.replace("SS2_TRAINING_TEST_SLUG='pow-control'","SS2_TRAINING_TEST_SLUG='nicotine-hat'\nSS2_TRAINING_TEST_IDS={15}")
text=text.replace("print('PASS native character switch P'..slot..' '..d.slug)","assert(T.palette(slot));assert(rd(ptr)==d.palette+256)\n  print('PASS native character switch P'..slot..' '..d.slug)")
text=text.replace("assert(T.pow(slot,-16));phase='pow-lower';phase_frame=frame","""
   local f=assert(io.open(root..'reports/nicotine-hat-p'..slot..'-native.gd','wb'));f:write(gui.gdscreenshot());f:close()
   f=assert(io.open(root..'reports/nicotine-hat-p'..slot..'-palette.bin','wb'))
   local base=slot==2 and 0x400300 or 0x400200
   for i=0,255 do f:write(string.char(rb(base+i))) end;f:close()
   assert(rb(actor+0x81)%8==2,'full POW body bank must be 2')
   phase='pow-lower';phase_frame=frame""")
text=text.replace("rb(actor+0xf0)==16 and rw(actor+0xb8)==0","rb(actor+0xf0)==32 and rw(actor+0xb8)>0")
text=text.replace("rb(actor+0xf0)==16,'preview reset lost POW selection'","rb(actor+0xf0)==32,'preview reset lost POW selection'")
text=text.replace("local selected=SS2_TRAINING_TEST_IDS or T.roster","""
local original_overlay=gui.gdoverlay
local captured={}
gui.gdoverlay=function(x,y,data,...)
 local s=A.status()
 if s and s.frame==3 then
  local which=s.actor==memory.readdword(0x100a46) and 1 or 2
  if not captured[which] then
   captured[which]=true
   local f=assert(io.open(root..'reports/nicotine-hat-p'..which..'-animal.gd','wb'));f:write(data);f:close()
  end
 end
 return original_overlay(x,y,data,...)
end
local selected=SS2_TRAINING_TEST_IDS or T.roster""")
Path('reports/fbneo-test-nicotine-hat.lua').write_text(text)
