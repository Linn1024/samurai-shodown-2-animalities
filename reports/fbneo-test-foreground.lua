-- Owned test emulator: replay a copy of the user's barrel-stage save.
SS2_NO_MAIN_LOOP=true
local root='C:/TEMP2/SS2/'
local log=assert(io.open(root..'reports/fbneo-haohmaru-test.log','w'))
local original_print=print
print=function(...)
 local words={} for _,v in ipairs({...}) do words[#words+1]=tostring(v) end
 log:write(table.concat(words,' ')..'\n');log:flush();original_print(...)
end
local api=dofile(root..'ultimate.lua')
assert(api.animality)
local A=api.animality
local frame,loaded,finished,covered,best=0,false,false,0,0
local rb,rd=memory.readbyte,memory.readdword
local function ww(a,v) memory.writebyte(a,math.floor(v/256)%256);memory.writebyte(a+1,v%256) end
local oldbefore=emu.registerbefore(nil)
local oldafter=emu.registerafter(nil)
local olddraw=gui.register(nil)
emu.registerbefore(function()
 frame=frame+1
 if loaded and frame==204 then
  local p1,p2=rd(0x100a46),rd(0x100a4a)
  ww(p1+0xba,128);ww(p1+0xe6,0);ww(p1+0x4e,128);ww(p1+0x50,224)
  ww(p1+0x52,0);ww(p1+0x56,0);ww(p1+0x60,0);ww(p1+0x62,0)
  ww(p2+0xba,0);ww(p2+0xe6,0x318);ww(p2+0x4e,230);ww(p2+0x50,224)
 end
 if oldbefore then oldbefore() end
end)
emu.registerafter(function()
 if oldafter then oldafter() end
 local s=A.status()
 if s and s.t==1 then
  local f=assert(io.open(root..'reports/fbneo-haohmaru-started.txt','w'));f:write(frame);f:close()
 end
 if loaded and A.events==1 and not s and not finished then
  finished=true
  assert(covered>0,'No barrel occlusion pixels were produced')
  print('PASS FOREGROUND covered_frames='..covered)
  print('PASS FBNeo haohmaru events=1 handler='..string.format('%x',rd(rd(0x100a46))))
 end
end)
gui.register(function()
 gui.clearuncommitted()
 local native=gui.gdscreenshot()
 if olddraw then olddraw() end
 if A.status() and A.foreground.clipped>0 then
  covered=covered+1
  if covered==1 then print('FOREGROUND first clip pixels='..A.foreground.clipped) end
  if A.foreground.clipped>best then
   best=A.foreground.clipped
   local f=assert(io.open(root..'reports/foreground-best.gd','wb'));f:write(gui.gdscreenshot());f:close()
   local f=assert(io.open(root..'reports/foreground-native.gd','wb'));f:write(native);f:close()
   local f=assert(io.open(root..'reports/foreground-vram.bin','wb'))
   for i=0,65535 do local w=A.foreground.vram[i] or 0;f:write(string.char(w%256,math.floor(w/256))) end
   f:close()
   f=assert(io.open(root..'reports/foreground-layers.bin','wb'))
   for i=0,380 do local layer=A.foreground.layers[i] or 0;f:write(string.char(math.floor(layer/256),layer%256)) end
   f:close()
  end
 end
end)
while true do
 emu.frameadvance()
 if frame==200 and not loaded then
  savestate.load(root..'reports/barrel-stage-test.fs');loaded=true
 end
 if finished then emu.pause() end
end
