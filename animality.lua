-- Shared animality engine for FBNeo Samurai Shodown II Special 2017.
-- Loaded by ultimate.lua. Graphics are emulator overlays; native fountain and victory remain game animations.
-- FBNeo also allows this file to be selected directly in its Lua window.
local module_only=...
if not module_only and memory and gui and emu and emu.registerbefore then
 local source=debug.getinfo(1,'S').source:sub(2)
 local folder=source:match('^(.*[/\\])') or ''
 print('Animalities: starting ultimate.lua (animality, F button and shadows).')
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
local foreground=assert(loadfile(folder..'animality-foreground.lua'))()(memory,folder)
M.foreground=foreground
local log_path=folder..'animality.log'
local function log(message)
 local line=os.date('%Y-%m-%d %H:%M:%S')..' Animality: '..message
 print(line)
 local f=io.open(log_path,'a')
 if f then f:write(line,'\n');f:close() end
end
local function describe(p)
 return string.format('actor=%06X character=%d HP=%d state=%04X handler=%X',
  p,rb(p+0xf6),rw(p+0xba),rw(p+0xe6),rd(p))
end
local definitions=assert(loadfile(folder..'animalities.lua'))()
M.definitions=definitions
for id,definition in pairs(definitions) do
 definition.id=id
 definition.canvas=definition.canvas or 128
 definition.anchor=definition.anchor or {64,112}
 definition.root=folder..'assets/'..definition.slug..'-animality/'
 definition.sprites={}
 definition.palette_map=assert(loadfile(definition.root..'palette-map.lua'))()
 -- Optional per-pixel material tags: shared RGB shades may belong to skin or clothing.
 local regions=io.open(definition.root..'hat-palette.bin','rb')
 if regions then
  definition.palette_regions=regions:read('*a');regions:close()
  assert(#definition.palette_regions==definition.canvas^2*definition.frames,'Invalid hat palette mask')
 end
 definition.palette_cache={};definition.palette_order={}
 for _,direction in ipairs({'right','left'}) do
  definition.sprites[direction]={}
  for _,zoom in ipairs({64,80,96,112,128}) do
   local frames={};definition.sprites[direction][zoom]=frames
   for i=0,definition.frames-1 do
    local path=definition.root..'gd/'..string.format('%s-%d-%02d.gd',direction,zoom,i)
    local f=assert(io.open(path,'rb'),'Missing animality asset: '..path)
    frames[i]=f:read('*a');f:close()
   end
  end
 end
end
local active,patched,last_fatal=nil,nil,{}
local function palette_rgb(w,palette_map)
 local dark=math.floor(w/32768)%2
 local function channel(nibble,extra)
  return palette_map.rgb[nibble*4+extra*2+dark+1]
 end
 return string.char(channel(math.floor(w/256)%16,math.floor(w/16384)%2),
  channel(math.floor(w/16)%16,math.floor(w/8192)%2),channel(w%16,math.floor(w/4096)%2))
end
local function select_palette(actor,definition)
 local palette_map=definition.palette_map
 local palette_cache,palette_order=definition.palette_cache,definition.palette_order
 -- Read the displayed fighter palette, including POW tints and hit flashes.
 local slot=actor==rd(0x100a46) and 0 or 1
 local base=0x400200+slot*256
 -- POW selects a different skin bank; reading bank zero alone misses it.
 -- Native render commands copy actor+81 for the body and +82 for weapons.
 local skin=math.min(2,rb(actor+0x81)%8)
 local weapon=math.min(1,rb(actor+0x82)%8)
 local words,signature={},{}
 signature[1]=string.char(skin,weapon)
 for bank=0,7 do
  for color=0,15 do
   local w=rw(base+bank*32+color*2)
   words[bank*16+color]=w
   signature[#signature+1]=string.char(math.floor(w/256),w%256)
  end
 end
 local key=table.concat(signature)
 if not palette_cache[key] then
  local replacements={}
  for _,entry in ipairs(palette_map.colors) do
   local index=entry[4]
   if index<48 then index=index%16+skin*16
   elseif index>=48 and index<64 then index=index+weapon*16 end
   replacements[string.char(0,entry[1],entry[2],entry[3])]=string.char(0)..palette_rgb(words[index],palette_map)
  end
  local indexed={}
  for index=0,127 do
   local selected=index
   if index<48 then selected=index%16+skin*16
   elseif index<64 then selected=index+weapon*16 end
   indexed[index]=string.char(0)..palette_rgb(words[selected],palette_map)
  end
  palette_cache[key]={replacements=replacements,indexed=indexed,frames={}}
  palette_order[#palette_order+1]=key
  if #palette_order>4 then palette_cache[table.remove(palette_order,1)]=nil end
 end
 return palette_cache[key]
end
local function colored_sprite(s,direction,zoom)
 local original=s.definition.sprites[direction][zoom][s.frame]
 if not s.palette then return original end
 local key=direction..':'..zoom..':'..s.frame
 local cached=s.palette.frames[key]
 if not cached then
  local regions=s.definition.palette_regions
  local pixel_index=0
  cached=original:sub(1,11)..original:sub(12):gsub('....',function(pixel)
   pixel_index=pixel_index+1
   if regions and zoom==128 then
    local width=s.definition.canvas
    local x=(pixel_index-1)%width
    local y=math.floor((pixel_index-1)/width)
    if direction=='left' then x=width-1-x end
    local index=regions:byte(s.frame*width*width+y*width+x+1)
    if index~=255 then return s.palette.indexed[index] end
   end
   return s.palette.replacements[pixel] or pixel
  end)
  s.palette.frames[key]=cached
 end
 return cached
end
-- Follow every native camera size rather than snapping to five coarse sizes.
-- Always sample the original pixels; never resample an already shrunk frame.
local function camera_sprite(s,direction,compression)
 local size=math.floor(s.definition.canvas*(256-compression)/256+.5)
 if size==s.definition.canvas then return colored_sprite(s,direction,128),size end
 local key=direction..':'..size..':'..s.frame
 s.camera_cache=s.camera_cache or {};s.camera_order=s.camera_order or {}
 if not s.camera_cache[key] then
  local data=colored_sprite(s,direction,128)
  local original=s.definition.canvas
  local rows={};local columns={}
  for x=0,size-1 do columns[x]=math.floor((x+.5)*original/size)*4 end
  for y=0,size-1 do
   local start=12+math.floor((y+.5)*original/size)*original*4
   local pixels={}
   for x=0,size-1 do local p=start+columns[x];pixels[#pixels+1]=data:sub(p,p+3) end
   rows[#rows+1]=table.concat(pixels)
  end
  s.camera_cache[key]=data:sub(1,2)..string.char(math.floor(size/256),size%256,math.floor(size/256),size%256)..data:sub(7,11)..table.concat(rows)
  s.camera_order[#s.camera_order+1]=key
  if #s.camera_order>32 then s.camera_cache[table.remove(s.camera_order,1)]=nil end
 end
 return s.camera_cache[key],size
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
 foreground.reset()
 if active then log(active.definition.name..' cancelled: '..(reason or 'script reset/load/exit')..'; animation frame='..active.t) end
 if active and restore_position and valid(active.actor) and rb(active.actor+0xf6)==active.definition.id then
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
 local definition=definitions[rb(actor+0xf6)]
 if not definition or rw(actor+0xba)==0 or rw(victim+0xba)~=0 then
  log('fountain skipped: winner must be a living supported character; '..describe(actor)..'; victim '..describe(victim));return
 end
 if rd(actor)~=0x25314 or rd(victim)~=0x25314 then
  log('fountain skipped: unexpected actor handler; '..describe(actor)..'; victim '..describe(victim));return
 end
 M.events=M.events+1
 active={actor=actor,victim=victim,definition=definition,t=0,startx=signed(rw(actor+0x4e)),
  direction=signed(rw(actor+0x4e))<=signed(rw(victim+0x4e)) and 1 or -1,frame=0,lift=0}
 active.flight_height=math.max(0,(torso_height[rb(victim+0xf6)] or 43)-definition.contact_y)
 active.palette=select_palette(actor,definition)
 log(string.format('%s live palette enabled: P%d, RAM=%06X.',definition.name,actor==rd(0x100a46) and 1 or 2,actor==rd(0x100a46) and 0x400200 or 0x400300))
 -- Remove the completed attack's collision boxes before suspending its animation.
 ww(actor+0x26,65535);ww(actor+0x3a,65535);ww(actor+0xca,0);wb(actor+0x103,0)
 log(definition.name..': native fountain finish detected. Event='..M.events..'; '..describe(actor)..'; victim '..describe(victim))
end
function M.before()
 if not active then return end
 local a,b=actors()
 if (active.actor~=a and active.actor~=b) or (active.victim~=a and active.victim~=b)
  or rb(active.actor+0xf6)~=active.definition.id or rw(active.victim+0xba)~=0
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
 ww(p+0xe6,active.definition.victory);ww(p+0xc4,65535)
 wb(p+0xf9,0);wb(p+0xfb,0)
 log(active.definition.name..': human form restored; native victory pose.')
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
 if not s.hit and fountain(s.victim) then s.hit=s.t; log(s.definition.name..': torso strike / native blood fountain. Animation frame='..s.t) end
 local scale=(256-rb(s.actor+0x7a))/256
 local target=signed(rw(s.victim+0x4e))-s.direction*s.definition.contact_x/math.max(.5,scale)
 local lead=0
 -- E1's first pose lasts 40 native animation ticks. Begin the short thrust
 -- during its final eight ticks; wait through the game's own hit-stop first.
 if rw(s.victim+0x66)==0xe1 then
  lead=rb(s.victim+0x7c)>0 and 1 or clamp((rb(s.victim+0x7d)-32)/8,0,1)
 end
 -- Preparation is stationary. Locomotion begins with the native death wind-up,
 -- never an elapsed-time running/flapping loop while waiting for hit-stop.
 local travel=lead
 local crouch_pounce=s.definition.movement=='crouch_pounce' or s.definition.movement=='pounce'
 if s.hit then travel=1 end
 s.lift=s.flight_height*lead
 local x=s.startx+(target-s.startx)*travel
 if not s.hit then
  if s.t<8 then s.frame=0
  elseif s.t<20 then s.frame=1
  elseif s.t<32 then s.frame=2
  elseif s.t<44 then s.frame=3
  elseif crouch_pounce then s.frame=lead>0 and 7 or 4
  elseif lead==0 then s.frame=3
  elseif lead>=.75 then s.frame=7
  else s.frame=({5,6})[math.floor(s.t/4)%2+1] end
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
  -- Reach the return position before the planted landing/rest poses.
  local retreat=clamp((h-7)/18,0,1)
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
 local palette=select_palette(s.actor,s.definition)
 if palette~=s.palette then
  s.palette=palette
  s.camera_cache=nil;s.camera_order=nil
 end
 local compression=clamp(rb(s.actor+0x7a),0,128)
 local scale=(256-compression)/256
 local x=signed(rw(s.actor+0x5c))
 local y=signed(rw(s.actor+0x5e))-16 -- Neo Geo visible area starts on line 16.
 local direction=s.direction==1 and 'right' or 'left'
 local sprite,size=camera_sprite(s,direction,compression)
 local draw_scale=size/s.definition.canvas
 local anchorx=(s.direction==1 and s.definition.anchor[1] or s.definition.canvas-1-s.definition.anchor[1])*draw_scale
 local ox=math.floor(x-anchorx+.5)
 local oy=math.floor(y-s.definition.anchor[2]*draw_scale-s.lift*scale+.5)
 gui.gdoverlay(ox,oy,foreground.clip(sprite,ox,oy))
end
function M.status() return active end
clear_overlay()
local ready={}
for _,definition in pairs(definitions) do ready[#ready+1]=definition.name end
table.sort(ready);M.ready=table.concat(ready,', ')
log('loaded: '..M.ready..'; live fighter palettes and native foreground masking enabled (all stages). Trigger: living supported winner, opponent HP=0 and state=0318. Log: '..log_path)
return M
end
