SS2_NO_MAIN_LOOP=true
local root='C:/TEMP2/SS2/'
local log=assert(io.open(root..'reports/fbneo-animality-test.log','w'))
local oldprint=print
print=function(...)
 local s={} for i,v in ipairs({...}) do s[i]=tostring(v) end
 log:write(table.concat(s,' ')..'\n');log:flush();oldprint(...)
end
local api=dofile(root..'ultimate.lua')
assert(api.animality,'animality did not load')
local before=emu.registerbefore(nil)
local after=emu.registerafter(nil)
local frame=0
local setup=false
local attack=0
local in_hook=false
local pause_wanted=false
local finished=false
emu.speedmode('turbo')
local function ww(a,v) memory.writebyte(a,math.floor(v/256));memory.writebyte(a+1,v%256) end
local function rd(a) return memory.readdword(a) end
local function valid(p) return p>=0x102000 and p<0x10fe00 end
emu.registerbefore(function()
 frame=frame+1
 if frame==2500 then emu.speedmode('normal') end
 local keys={}
 keys['P1 Coin']=frame<2500 and frame%180<20
 keys['P1 Start']=frame<2500 and frame%180>=50 and frame%180<60
 keys['P1 Button A']=frame<2500 and frame%180>=100 and frame%180<110
 keys['P1 Button B']=false
 if frame>=1000 and frame<2300 then memory.writebyte(0x100d0b,5) end
 local p1,p2=rd(0x100a46),rd(0x100a4a)
 if frame>2500 and valid(p1) and valid(p2) and memory.readbyte(p1+0xf6)==5 then
  if not setup then
   memory.registerwrite(p2+0xe8,4,function()
    if in_hook then return end
    in_hook=true;memory.writebyte(p2+0xe9,0);memory.writebyte(p2+0xeb,0);in_hook=false
   end)
   setup=true;attack=frame+60;print('FIXTURE Ukyo match ready',frame,string.format('%x %x',p1,p2))
  end
  if frame<attack then
   ww(p1+0x4e,240);ww(p2+0x4e,295);ww(p1+0xe6,0);ww(p2+0xe6,0)
   memory.writebyte(p2+0xbb,1)
  end
  keys['P1 Button A']=frame>=attack and frame<attack+4
  keys['P1 Button B']=keys['P1 Button A']
 end
 joypad.set(keys)
 if before then before() end
end)
emu.registerafter(function()
 local p1,p2=rd(0x100a46),rd(0x100a4a)
 if setup and valid(p2) and memory.readbyte(p2+0xbb)==0 and api.animality.events==0 then ww(p2+0xe6,0x318) end
 if after then after() end
 local s=api.animality.status()
 if s and s.frame==8 then
  local f=assert(io.open(root..'reports/fbneo-animality-strike.txt','w'));f:write('frame '..frame);f:close()
  -- Hold an actual rendered strike for inspection of this owned test instance.
  if not SS2_STRIKE_CAPTURED then SS2_STRIKE_CAPTURED=true;pause_wanted=true end
 end
 if api.animality.events>0 and not s and not finished then
  finished=true
  print('PASS FBNeo events='..api.animality.events..' handler='..string.format('%x',rd(p1)))
 end
 if frame%600==0 then print('FRAME',frame,setup,api.animality.events) end
end)
while true do
 emu.frameadvance()
 if pause_wanted then pause_wanted=false;emu.pause() end
end
