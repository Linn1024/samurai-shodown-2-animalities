-- Dedicated FBNeo process; config line: numeric ID and asset slug.
SS2_NO_MAIN_LOOP=true
local root='C:/TEMP2/SS2/'
local config=assert(io.open(root..'reports/fbneo-roster-config.txt','r'))
local config_text=config:read('*a');config:close()
local id,slug=config_text:match('(%d+)%s+([%w-]+)');id=tonumber(id)
local stage=tonumber(config_text:match('^%d+%s+[%w-]+%s+(%d+)'))
assert(id and slug)
local log=assert(io.open(root..'reports/fbneo-'..slug..'-test.log','w'))
local oldprint=print
print=function(...)
 local s={} for i,v in ipairs({...}) do s[i]=tostring(v) end
 log:write(table.concat(s,' ')..'\n');log:flush();oldprint(...)
end
local api=dofile(root..'ultimate.lua')
assert(api.animality,'animality did not load')
local stage_hook=false
local before=emu.registerbefore(nil)
local after=emu.registerafter(nil)
local frame,attack=0,0
local setup,in_hook,finished,pause_wanted=false,false,false,false
local startx,covered,best=240,0,0
local propstart=240
if stage then
 local draw=gui.register(nil)
 gui.register(function()
  if draw then draw() end
  local A=api.animality
  if A.status() and A.foreground.clipped>0 then
   covered=covered+1
   if A.foreground.clipped>best then
    best=A.foreground.clipped
    local f=assert(io.open(root..'reports/fbneo-stage-'..stage..'-best.gd','wb'));f:write(gui.gdscreenshot());f:close()
   end
  end
 end)
end
emu.speedmode('turbo')
local function ww(a,v) memory.writebyte(a,math.floor(v/256));memory.writebyte(a+1,v%256) end
local function rd(a) return memory.readdword(a) end
local function valid(p) return p>=0x102000 and p<0x10fe00 end
emu.registerbefore(function()
 frame=frame+1
 if stage and frame==1000 then
  memory.registerwrite(0x100ad8,2,function()
   if stage_hook then return end
   stage_hook=true;memory.writebyte(0x100ad9,stage);stage_hook=false
  end)
 end
 if stage and frame>=1000 and frame<2500 then memory.writebyte(0x100ad9,stage) end
 if frame==2500 then emu.speedmode('normal') end
 local keys={}
 keys['P1 Coin']=frame<2500 and frame%180<20
 keys['P1 Start']=frame<2500 and frame%180>=50 and frame%180<60
 keys['P1 Button A']=frame<2500 and frame%180>=100 and frame%180<110
 keys['P1 Button B']=false
 if frame>=1000 and frame<2300 then memory.writebyte(0x100d0b,id) end
 local p1,p2=rd(0x100a46),rd(0x100a4a)
 if frame>2500 and valid(p1) and valid(p2) and memory.readbyte(p1+0xf6)==id then
  if not setup then
   if stage then
    local node=0x101000
    for i=1,120 do
     node=0x100000+memory.readbyte(node+2)*256+memory.readbyte(node+3)
     if node<0x101040 or node>=0x101fc0 then break end
     local layer=memory.readbyte(node+4)*256+memory.readbyte(node+5)
     local x=memory.readbyte(node+0x10)*256+memory.readbyte(node+0x11)
     if layer>=0x100 and layer<0xffff and x<320 then
      local playerx=memory.readbyte(p1+0x5c)*256+memory.readbyte(p1+0x5d)
      local worldx=memory.readbyte(p1+0x4e)*256+memory.readbyte(p1+0x4f)
      local scale=(256-memory.readbyte(p1+0x7a))/256
      propstart=math.floor(worldx+(x-playerx)/math.max(.5,scale));break
     end
    end
    print('STAGE '..stage..' selected; propstart='..propstart)
   end
   memory.registerwrite(p2+0xe8,4,function()
    if in_hook then return end
    in_hook=true;memory.writebyte(p2+0xe9,0);memory.writebyte(p2+0xeb,0);in_hook=false
   end)
   setup=true;attack=frame+60;print('FIXTURE '..slug..' ready',frame)
  end
  if frame<attack then
   ww(p1+0x4e,startx);ww(p2+0x4e,startx+55);ww(p1+0xe6,0);ww(p2+0xe6,0)
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
 if s and s.t==1 then
  if stage then
   -- First earn a native KO at the proven combat spacing, then position the
   -- finishing sequence over the prop without depending on stage wall bounds.
   s.startx=propstart;ww(s.actor+0x4e,propstart);ww(s.victim+0x4e,propstart+55)
  end
  local f=assert(io.open(root..'reports/fbneo-'..slug..'-started.txt','w'));f:write(frame);f:close()
 end
 if api.animality.events>0 and not s and not finished then
  finished=true
  if stage then assert(covered>0,'No foreground overlap on stage '..stage);print('PASS STAGE '..stage..' covered_frames='..covered..' max_pixels='..best) end
  print('PASS FBNeo '..slug..' events='..api.animality.events..' handler='..string.format('%x',rd(p1)))
  pause_wanted=true
 end
 if frame%600==0 then
  print('FRAME',frame,setup,api.animality.events,'p1='..string.format('%x',p1),'id='..(valid(p1) and memory.readbyte(p1+0xf6) or -1))
 end
end)
while true do
 emu.frameadvance()
 if pause_wanted then pause_wanted=false;emu.pause() end
end
