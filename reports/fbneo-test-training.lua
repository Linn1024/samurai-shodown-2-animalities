SS2_NO_MAIN_LOOP=true
local root='C:/TEMP2/SS2/'
local log=assert(io.open(root..'reports/fbneo-haohmaru-test.log','w'))
local oldprint=print
print=function(...)
 local args={} for i,v in ipairs({...}) do args[i]=tostring(v) end
 log:write(table.concat(args,' ')..'\n');log:flush();oldprint(...)
end
local api=dofile(root..'ultimate.lua')
local T,A=assert(api.training),assert(api.animality)
local before=emu.registerbefore(nil);local after=emu.registerafter(nil)
local function rw(a) return memory.readbyte(a)*256+memory.readbyte(a+1) end
local function ww(a,v) memory.writebyte(a,math.floor(v/256));memory.writebyte(a+1,v%256) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local rd=memory.readdword
local frame,phase,done,seen=0,0,0,false
local ready,started,pause=false,false,false
emu.speedmode('turbo')
emu.registerbefore(function()
 frame=frame+1
 local keys={['P1 Coin']=frame<2500 and frame%180<20,
 ['P1 Start']=frame<2500 and frame%180>=50 and frame%180<60,
 ['P1 Button A']=frame<2500 and frame%180>=100 and frame%180<110}
 if frame>=1000 and frame<2300 then memory.writebyte(0x100d0b,0) end
 joypad.set(keys)
 local a,b=rd(0x100a46),rd(0x100a4a)
 if frame==2501 then
  assert(a>=0x102000 and b>=0x102000)
  ww(a+0x4e,240);ww(b+0x4e,295);ww(a+0xe6,0);ww(b+0xe6,0)
  -- Make P2 a supported fighter, with actual animation bank and matching palette.
  memory.writebyte(b+0xf6,0);ww(b+0x64,0)
  for bank=0,7 do wd(0x10ec60+bank*4,rd(0x10ec40+bank*4)) end
  T.toggle();ready=true
 end
 if frame==2540 then
  assert(T.enabled and rw(a+0xba)==128 and rw(b+0xba)==128)
  assert(memory.readbyte(0x100ac6)==0x99)
  assert(rw(b+0xe8)==0 and rw(b+0xea)==0,'dummy must be passive')
  print('PASS training health, timer and passive opponent')
  assert(T.preview(1));phase=1;emu.speedmode('normal')
 end
 if before then before() end
end)
emu.registerafter(function()
 if after then after() end
 if not ready then return end
 local a,b=rd(0x100a46),rd(0x100a4a)
 local s=A.status()
 if s then
  seen=true
  assert(rd(s.victim)==0x25314,'held native callback must be restored after each frame')
  if s.t==100 then
   assert(not s.hit and s.frame==4 and s.lift==0,'training must include a stationary preparation pose')
   assert(T.held_frames>=80,'training hit-stop preparation missing')
   print('PASS training preparation pose held at frame 100; held='..T.held_frames)
  end
  if s.hit and s.t==s.hit then
   assert(s.hit>=220 and s.hit<=250,'preview is too short or too long: '..s.hit)
   assert(T.held_frames==180,'full preparation delay required')
   print('PASS training native fountain timing: '..s.hit..' frames')
  end
  if not started then
   started=true;local f=assert(io.open(root..'reports/fbneo-haohmaru-started.txt','w'));f:write(frame);f:close()
  end
 end
 if seen and not T.previewing and not s and phase<=3 then
  assert(rw(a+0xba)==128 and rw(b+0xba)==128,'both players restored alive')
  assert(rd(a)==0x25314 and rd(b)==0x25314)
  assert(T.enabled)
  done=done+1;print('PASS training native preview and automatic return '..done)
  seen=false
  if phase<3 then
   phase=phase+1;assert(T.preview(phase==3 and 2 or 1));emu.speedmode('turbo')
  else
   phase=4;assert(T.preview(1))
  end
 elseif phase==4 and s and s.t>=10 then
  assert(T.restore());assert(not A.status() and not T.previewing)
  assert(rw(a+0xba)==128 and rw(b+0xba)==128)
  T.toggle();assert(not T.enabled)
  print('PASS training interrupted preview reset and toggle OFF')
  print('PASS FBNeo haohmaru events=4 handler='..string.format('%x',rd(a)))
  pause=true;phase=5
 end
 if frame>6500 and phase<5 then error('Training fixture did not complete: phase '..phase) end
end)
while true do emu.frameadvance();if pause then pause=false;emu.pause() end end
