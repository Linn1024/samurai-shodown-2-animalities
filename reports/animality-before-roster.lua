-- Ukyo Swan animality for FBNeo Samurai Shodown II Special 2017.
-- Loaded by ultimate.lua. Graphics are emulator overlays; native fountain and victory remain game animations.
-- FBNeo also allows this file to be selected directly in its Lua window.
local module_only=...
if not module_only and memory and gui and emu and emu.registerbefore then
 local source=debug.getinfo(1,'S').source:sub(2)
 local folder=source:match('^(.*[/\\])') or ''
 print('Ukyo Swan: starting ultimate.lua (animality, F button and shadows).')
 return dofile(folder..'ultimate.lua')
end
return function(memory,gui)
local M={enabled=true,events=0}
local rb,rd,wb=memory.readbyte,memory.readdword,memory.writebyte
local function rw(a) return rb(a)*256+rb(a+1) end
local function ww(a,v) v=math.floor(v)%65536;wb(a,math.floor(v/256));wb(a+1,v%256) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local function valid(p) return p and p>=0x102000 and p<=0x10fd00 and p%2==0 end
local function signed(v) return v>=32768 and v-65536 or v end
local function clamp(v,a,b) return math.max(a,math.min(b,v)) end
local source=(debug and debug.getinfo and debug.getinfo(1,'S').source:sub(2)) or ''
local folder=source:match('^(.*[/\\])') or ''
local root=folder..'assets/ukyo-animality/gd/'
local log_path=folder..'animality.log'
local function log(message)
 local line=os.date('%Y-%m-%d %H:%M:%S')..' Ukyo Swan: '..message
 print(line)
 local f=io.open(log_path,'a')
 if f then f:write(line,'\n');f:close() end
end
local function describe(p)
 return string.format('actor=%06X character=%d HP=%d state=%04X handler=%X',
  p,rb(p+0xf6),rw(p+0xba),rw(p+0xe6),rd(p))
end
local sprites={}
for _,direction in ipairs({'right','left'}) do
 sprites[direction]={}
 for _,zoom in ipairs({64,80,96,112,128}) do
  local frames={};sprites[direction][zoom]=frames
  for i=0,15 do
   local path=root..string.format('%s-%d-%02d.gd',direction,zoom,i)
   local f=assert(io.open(path,'rb'),'Missing animality asset: '..path)
   frames[i]=f:read('*a');f:close()
  end
 end
end
local active,patched,last_fatal=nil,nil,{}
local palette_map=assert(loadfile(folder..'assets/ukyo-animality/palette-map.lua'))()
local palette_cache,palette_order={},{}
local function palette_rgb(w)
 local dark=math.floor(w/32768)%2
 local function channel(nibble,extra)
  return palette_map.rgb[nibble*4+extra*2+dark+1]
 end
 return string.char(channel(math.floor(w/256)%16,math.floor(w/16384)%2),
  channel(math.floor(w/16)%16,math.floor(w/8192)%2),channel(w%16,math.floor(w/4096)%2))
end
local function select_palette(actor)
 -- The game's palette loader stores the eight selected ROM palette pointers
 -- at 10EC40 (P1) and 10EC60 (P2). Read those, not transient hit/POW flashes.
 local slot=actor==rd(0x100a46) and 0 or 1
 local base=0x10ec40+slot*32
 local words,signature={},{}
 for bank=0,7 do
  local pointer=rd(base+bank*4)
  if pointer<0x200000 or pointer>=0x300000 or pointer%2~=0 then
   log('palette unavailable; using original colors. P'..(slot+1));return nil
  end
  for color=0,15 do
   local w=rw(pointer+color*2)
   words[bank*16+color]=w
   signature[#signature+1]=string.char(math.floor(w/256),w%256)
  end
 end
 local key=table.concat(signature)
 if not palette_cache[key] then
  local replacements={}
  for _,entry in ipairs(palette_map.colors) do
   replacements[string.char(0,entry[1],entry[2],entry[3])]=string.char(0)..palette_rgb(words[entry[4]])
  end
  palette_cache[key]={replacements=replacements,frames={}}
  palette_order[#palette_order+1]=key
  if #palette_order>4 then palette_cache[table.remove(palette_order,1)]=nil end
 end
 log(string.format('costume palette selected: P%d, ROM=%06X.',slot+1,rd(base)))
 return palette_cache[key]
end
local function colored_sprite(s,direction,zoom)
 local original=sprites[direction][zoom][s.frame]
 if not s.palette then return original end
 local key=direction..':'..zoom..':'..s.frame
 local cached=s.palette.frames[key]
 if not cached then
  cached=original:sub(1,11)..original:sub(12):gsub('....',function(pixel)
   return s.palette.replacements[pixel] or pixel
  end)
  s.palette.frames[key]=cached
 end
 return cached
end
local function clear_overlay()
 if gui.clearuncommitted then gui.clearuncommitted() end
end
local torso_height={[0]=44,[1]=32,[2]=44,[3]=44,[4]=49,[5]=43,[6]=50,
 [7]=35,[8]=63,[9]=44,[11]=43,[12]=44,[13]=32,[14]=53,[15]=31,[16]=49,[17]=43}
local function actors()
 local a,b=rd(0x100a46),rd(0x100a4a)
 if valid(a) and valid(b) then return a,b end
end
local function restore_handler()
 if patched then
  if valid(patched.actor) and rd(patched.actor)==0x385c then wd(patched.actor,patched.handler) end
  patched=nil
 end
end
function M.cancel(restore_position,reason)
 restore_handler()
 clear_overlay()
 if active then log('cancelled: '..(reason or 'script reset/load/exit')..'; animation frame='..active.t) end
 if active and restore_position and valid(active.actor) and rb(active.actor+0xf6)==5 then
  ww(active.actor+0x4e,active.startx)
 end
 active=nil;last_fatal={}
end
local function fountain(victim)
 local o=0x102000 local seen={}
 for count=1,256 do
  if not valid(o) or seen[o] then break end
  seen[o]=true
  if (rd(o)==0x4456a or rd(o)==0x4452a) and rd(o+0xcc)==victim then return o end
  if rw(o+0x10)==65535 then break end
  o=0x100000+rw(o+0xe)
 end
end
local function begin(actor,victim)
 if rb(actor+0xf6)~=5 or rw(actor+0xba)==0 or rw(victim+0xba)~=0 then
  log('fountain skipped: winner must be living Ukyo; '..describe(actor)..'; victim '..describe(victim));return
 end
 if rd(actor)~=0x25314 or rd(victim)~=0x25314 then
  log('fountain skipped: unexpected actor handler; '..describe(actor)..'; victim '..describe(victim));return
 end
 M.events=M.events+1
 active={actor=actor,victim=victim,t=0,startx=signed(rw(actor+0x4e)),
  direction=rw(actor+0x4e)<=rw(victim+0x4e) and 1 or -1,frame=0,lift=0}
 active.flight_height=(torso_height[rb(victim+0xf6)] or 43)-16
 active.palette=select_palette(actor)
 -- Remove the completed attack's collision boxes before suspending its animation.
 ww(actor+0x26,65535);ww(actor+0x3a,65535);ww(actor+0xca,0);wb(actor+0x103,0)
 log('native fountain finish detected. Event='..M.events..'; '..describe(actor)..'; victim '..describe(victim))
end
function M.before()
 if not active then return end
 local a,b=actors()
 if (active.actor~=a and active.actor~=b) or (active.victim~=a and active.victim~=b)
  or rb(active.actor+0xf6)~=5 or rw(active.victim+0xba)~=0
  or rd(active.actor)~=0x25314 then M.cancel(false,'actor changed, victim revived, or handler changed');return end
 local p=active.actor
 -- Change the callback ONLY during this emulated frame. after() restores it,
 -- so states saved between frames retain the original executable callback.
 patched={actor=p,handler=rd(p)}
 wd(p,0x385c) -- native camera projection, no body drawing or attack logic
 ww(p+0x26,65535);ww(p+0x3a,65535);ww(p+0xca,0);wb(p+0x103,0)
end
local function finish()
 local p=active.actor
 ww(p+0x4e,active.startx)
 ww(p+0x52,0);ww(p+0x56,0);ww(p+0x60,0);ww(p+0x62,0)
 ww(p+0xe6,0x600);ww(p+0xc4,65535)
 wb(p+0xf9,0);wb(p+0xfb,0)
 log('human form restored; native victory pose.')
 active=nil
 clear_overlay()
end
function M.after()
 restore_handler()
 if not M.enabled then return end
 local a,b=actors()
 if not a then M.cancel(false,'player pointers unavailable');return end
 if not active then
  for _,pair in ipairs({{a,b},{b,a}}) do
   local actor,victim=pair[1],pair[2]
   local fatal=rw(victim+0xe6)==0x318 and rw(victim+0xba)==0
   local dead=rd(victim)==0x25314 and rd(actor)==0x25314 and rw(victim+0xba)==0
   if dead and not last_fatal['death'..victim] then
    log('KO observed: '..describe(victim)..'; opponent '..describe(actor)..'; requires fountain state=0318')
   end
   last_fatal['death'..victim]=dead
   if fatal and not last_fatal[victim] then begin(actor,victim) end
   last_fatal[victim]=fatal
  end
  return
 end
 local s=active
 s.t=s.t+1
 if s.t>600 then M.cancel(true,'timeout after 600 frames');return end
 if not s.hit and fountain(s.victim) then s.hit=s.t; log('torso strike / native blood fountain. Animation frame='..s.t) end
 local scale=(256-rb(s.actor+0x7a))/256
 local target=signed(rw(s.victim+0x4e))-s.direction*34/math.max(.5,scale)
 local approach=clamp((s.t-66)/36,0,1)
 local lead=0
 -- E1's first pose lasts 40 native animation ticks. Begin the short thrust
 -- during its final eight ticks; wait through the game's own hit-stop first.
 if rw(s.victim+0x66)==0xe1 then
  lead=rb(s.victim+0x7c)>0 and 1 or clamp((rb(s.victim+0x7d)-32)/8,0,1)
 end
 local travel=approach*(.55+.45*lead)
 if s.hit then travel=1 end
 s.lift=s.flight_height*clamp((s.t-56)/24,0,1)
 local x=s.startx+(target-s.startx)*travel
 if not s.hit then
  if s.t<8 then s.frame=0
  elseif s.t<20 then s.frame=1
  elseif s.t<32 then s.frame=2
  elseif s.t<44 then s.frame=3
  elseif s.t<54 then s.frame=4
  elseif s.t<64 then s.frame=5
  elseif s.t<74 then s.frame=6
  else s.frame=({5,7,6,7})[math.floor((s.t-74)/7)%4+1] end
 else
  local h=s.t-s.hit
  if h<7 then s.frame=8
  elseif h<16 then s.frame=9
  elseif h<25 then s.frame=10
  elseif h<34 then s.frame=11
  elseif h<68 then s.frame=12
  elseif h<80 then s.frame=13
  elseif h<92 then s.frame=14
  elseif h<100 then s.frame=15
  else finish();return end
  local retreat=clamp((h-7)/40,0,1)
  x=target+(s.startx-target)*retreat
  s.lift=s.flight_height*(1-clamp((h-16)/18,0,1))
 end
 ww(s.actor+0x4e,x)
end
function M.draw()
 -- FBNeo retains the last GUI bitmap until another drawing command clears it.
 -- Clear even when inactive, so the last transformation pose cannot linger.
 clear_overlay()
 if not active then return end
 local s=active
 local scale=clamp((256-rb(s.actor+0x7a))/256,.5,1)
 local zoom=math.floor((128*scale+8)/16)*16
 zoom=clamp(zoom,64,128)
 local x=signed(rw(s.actor+0x5c))
 local y=signed(rw(s.actor+0x5e))-16 -- Neo Geo visible area starts on line 16.
 local direction=s.direction==1 and 'right' or 'left'
 local anchorx=(s.direction==1 and 64 or 63)*zoom/128
 gui.gdoverlay(math.floor(x-anchorx+.5),math.floor(y-112*zoom/128-s.lift*scale+.5),colored_sprite(s,direction,zoom))
end
function M.status() return active end
clear_overlay()
log('loaded; sprites ready; automatic costume palettes enabled. Trigger: living Ukyo, opponent HP=0 and state=0318. Log: '..log_path)
return M
end
