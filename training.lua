-- FBNeo practice controls. Anonymous checkpoints never overwrite numbered slots.
return function(api,memory,joypad,input,savestate,gui)
local T={enabled=false,previewing=false,preparation_frames=180}
local rb,rd,wb=memory.readbyte,memory.readdword,memory.writebyte
local function rw(a) return rb(a)*256+rb(a+1) end
local function ww(a,v) wb(a,math.floor(v/256)%256);wb(a+1,v%256) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local checkpoint,previous,hooked,guard,restoring=nil,{},nil,false,false
local frames,finished,pending=0,nil,nil
local held_victim,wait_remaining=nil,0
local switching=nil
local power_pending=nil
local power_keys={leftbracket={1,-1},rightbracket={1,1},['numpad-']={2,-1},['numpad+']={2,1}}
local power_held={}
local roster={}
for id in pairs(api.animality and api.animality.definitions or {}) do roster[#roster+1]=id end
table.sort(roster)
T.roster=roster
T.held_frames=0
function T.after_frame()
 if held_victim then wd(held_victim,0x25314);held_victim=nil end
end
local notice,notice_until='',0
local function say(s) notice=s;notice_until=frames+240;print('Training: '..s) end
local function players()
 local a,b=rd(0x100a46),rd(0x100a4a)
 local function valid(p) return p>=0x102000 and p<=0x10fd00 and p%2==0 and rd(p)==0x25314 end
 if valid(a) and valid(b) and a~=b then return a,b end
end
local function live()
 local a,b=players()
 if a and rw(a+0xba)>0 and rw(b+0xba)>0 and rw(a+0xe6)<0x300 and rw(b+0xe6)<0x300 then return a,b end
end
local function unhook()
 if hooked and memory.registerwrite then memory.registerwrite(hooked+0xe8,4,nil) end
 hooked=nil
end
local function dummy(p)
 if not memory.registerwrite then return end
 if hooked~=p then
  unhook();hooked=p
  memory.registerwrite(p+0xe8,4,function()
   if not T.enabled or guard then return end
   guard=true;ww(p+0xe8,0);ww(p+0xea,0);guard=false
  end)
 end
 guard=true;ww(p+0xe8,0);ww(p+0xea,0);guard=false
end
local function save()
 checkpoint=savestate.create();savestate.save(checkpoint)
end
function T.restore()
 if not checkpoint then say('No practice position yet. Start a match first.');return false end
 T.after_frame();api.cancel();if api.animality then api.animality.cancel(false,'practice reset') end
 unhook();T.previewing=false;finished=nil;pending=nil;switching=nil;power_pending=nil
 restoring=true;savestate.load(checkpoint);restoring=false
 say('Practice position restored. G=P1 animality, H=P2.');return true
end
function T.on_load()
 held_victim=nil;wait_remaining=0;switching=nil;power_pending=nil
 unhook();T.previewing=false;finished=nil;pending=nil
 if not restoring then checkpoint=nil end
end
function T.stop() T.after_frame();unhook();T.enabled=false;pending=nil;wait_remaining=0;switching=nil;power_pending=nil;power_held={} end
function T.filter_inputs(values)
 if not T.enabled then return end
 for _,key in ipairs({'Up','Down','Left','Right','Button A','Button B','Button C','Button D'}) do values['P2 '..key]=false end
end
function T.toggle()
 if T.enabled then
  if T.previewing then T.restore() end
  T.stop();checkpoint=nil;say('OFF')
 else T.enabled=true;checkpoint=nil;say('ON. G/H preview; J/K P1 hero; N/M P2; O/P palette; R reset.') end
end
-- Let the ROM retire old companions/projectiles and initialize the new fighter.
local function retire_owned(actor,other,slot)
 local nodes,seen={},{}
 local p=0x102000
 for i=1,256 do
  p=0x100000+rw(p+0xe)
  if p<=0x102000 or p>0x10fd00 or p%2~=0 or seen[p] then break end
  seen[p]=true;nodes[#nodes+1]=p
 end
 local owned={[actor]=true}
 for pass=1,4 do
  for _,node in ipairs(nodes) do
   if node~=actor and node~=other and owned[rd(node+0xcc)] then owned[node]=true end
  end
 end
 for node in pairs(owned) do if node~=actor then wd(node,0x3052) end end
 for _,address in ipairs({0x100a4e+(slot-1)*4,0x100a56+(slot-1)*4,
  0x100aa6+(slot-1)*16,0x100aaa+(slot-1)*16,0x100aae+(slot-1)*16,0x100ab2+(slot-1)*16}) do
  if owned[rd(address)] then wd(address,0) end
 end
end
function T.change(slot,step)
 if not T.enabled then say('Press T to enable training first.');return false end
 if switching then return false end
 if T.previewing and not T.restore() then return false end
 if api.animality and api.animality.status() then say('R resets the finish before changing character.');return false end
 local a,b=live()
 if not a or #roster<1 then say('Start a live match before changing character.');return false end
 local actor,other=slot==2 and b or a,slot==2 and a or b
 local current=rb(actor+0xf6);local index=1
 for i,id in ipairs(roster) do if id==current then index=i;break end end
 index=(index-1+step)%#roster+1
 local id=roster[index];local d=api.animality.definitions[id]
 local pointers=slot==2 and 0x10ec60 or 0x10ec40
 local previous_definition=api.animality.definitions[current]
 local variant=previous_definition and rd(pointers)==previous_definition.palette+256 and 1 or 0
 local palette=d.palette and d.palette+variant*256
 if not palette or palette<0x200000 or palette>=0x300000 then say('Character palette is unavailable.');return false end
 api.cancel();unhook();checkpoint=nil
 retire_owned(actor,other,slot)
 wb(0x100d0b+(slot-1)*16,id);wb(actor+0xf6,id);ww(actor+0x64,id)
 ww(actor+0xe6,0);ww(actor+0xc4,65535)
 ww(actor+0xba,128);ww(actor+0xbc,0)
 ww(actor+0x50,224);ww(actor+0x52,0);ww(actor+0x56,0)
 wb(actor+0xf9,0);wb(actor+0xfb,0);wb(actor+0x111,0)
 local colors=slot==2 and 0x400300 or 0x400200
 for bank=0,7 do wd(pointers+bank*4,palette+bank*32) end
 for offset=0,254,2 do ww(colors+offset,rw(palette+offset)) end
 wd(actor,0x252ec)
 switching={slot=slot,id=id,start=frames}
 say('P'..slot..': '..(d.character or d.name)..'. Loading native fighter...')
 return true
end
function T.pow(slot,step)
 if not T.enabled or switching then return false end
 if T.previewing and not T.restore() then return false end
 if api.animality and api.animality.status() then return false end
 local a,b=players();if not a or rw(a+0xba)==0 or rw(b+0xba)==0 then return false end
 local actor=slot==2 and b or a
 local current=math.min(32,rb(actor+0xf0))
 local target=math.max(0,math.min(32,current+step))
 if target==current then return true end
 -- Retire the current rage duration and queued meter changes. Let the ROM
 -- enter full POW itself, including the native tint/timer/animation flags.
 ww(actor+0xb8,0);ww(actor+0x114,0)
 local flag=rb(actor+0x11c);wb(actor+0x11c,flag-flag%2)
 wb(actor+0xf0,target==32 and 31 or target)
 if target==32 then wb(actor+0x114,1) end
 power_pending=frames+3
 say('P'..slot..' POW '..target..'/32 ('..math.floor(target*100/32+.5)..'%).')
 return true
end
function T.palette(slot)
 if not T.enabled then say('Press T to enable training first.');return false end
 if switching then return false end
 if T.previewing and not T.restore() then return false end
 if api.animality and api.animality.status() then say('R resets the finish before changing palette.');return false end
 local a,b=live()
 if not a then say('Start a live match before changing palette.');return false end
 local actor=slot==2 and b or a
 local d=api.animality.definitions[rb(actor+0xf6)]
 if not d or not d.palette then return false end
 local pointers=slot==2 and 0x10ec60 or 0x10ec40
 local alternative=rd(pointers)~=d.palette+256
 local palette=d.palette+(alternative and 256 or 0)
 local colors=slot==2 and 0x400300 or 0x400200
 for bank=0,7 do wd(pointers+bank*4,palette+bank*32) end
 for offset=0,254,2 do ww(colors+offset,rw(palette+offset)) end
 save()
 say('P'..slot..': '..(alternative and 'alternate' or 'main')..' palette.')
 return true
end
function T.preview(slot)
 if not T.enabled then say('Press T to enable training first.');return false end
 if switching then say('Character is loading.');return false end
 if T.previewing or (api.animality and api.animality.status()) then say('Preview already playing. R resets it.');return false end
 local a,b=live()
 if not a then say('Start a live match, then press G or H.');return false end
 local actor,victim=slot==2 and b or a,slot==2 and a or b
 local definition=api.animality and api.animality.definitions[rb(actor+0xf6)]
 if not definition then say('This character has no installed animality yet.');return false end
 api.cancel();save()
 -- Enter the native fountain death state, rather than faking a blood overlay.
 ww(actor+0xe6,0);ww(actor+0xc4,65535)
 ww(actor+0xbc,0);ww(actor+0xba,128)
 ww(victim+0xbc,0);ww(victim+0xba,0)
 ww(victim+0xe6,0x318);ww(victim+0xc4,65535)
 T.previewing=true;finished=nil;pending=frames;wait_remaining=T.preparation_frames;T.held_frames=0
 say('Preview: '..definition.name..'. R resets; returns automatically.');return true
end
function T.before()
 frames=frames+1
 local keys=input.get()
 for key,control in pairs(power_keys) do
  power_held[key]=keys[key] and (power_held[key] or 0)+1 or 0
  local held=power_held[key]
  if held==1 or (held>=25 and (held-25)%8==0) then T.pow(control[1],control[2]) end
 end
 for _,key in ipairs({'T','G','H','R','J','K','N','M','O','P'}) do
  if keys[key] and not previous[key] then
   if key=='T' then T.toggle()
   elseif key=='G' then T.preview(1)
   elseif key=='H' then T.preview(2)
   elseif key=='J' then T.change(1,-1)
   elseif key=='K' then T.change(1,1)
   elseif key=='N' then T.change(2,-1)
   elseif key=='M' then T.change(2,1)
   elseif key=='O' then T.palette(1)
   elseif key=='P' then T.palette(2)
   elseif T.enabled then T.restore() end
  end
  previous[key]=keys[key] and true or false
 end
 if not T.enabled then return end
 if switching then return end
 local a,b=players()
 if not a then unhook();return end
 dummy(b)
 local values={}
 T.filter_inputs(values)
 joypad.set(values)
 local s=api.animality and api.animality.status()
 if T.previewing and s and not s.hit and wait_remaining>0 and rw(s.victim+0x66)==0xe1 then
  -- A shortcut has no lethal-hit stop. Hold the native death pose while the
  -- animal completes its transformation and preparation, then let E1 resume.
  -- The normal native callback is restored before animality.after/save states.
  held_victim=s.victim;wd(held_victim,0x385c)
  wait_remaining=wait_remaining-1;T.held_frames=T.held_frames+1
 end
 if T.previewing or (api.animality and api.animality.status()) then return end
 if live() then
  if not checkpoint then save();say('Practice ready. G=P1 animality, H=P2, R=reset.') end
  for _,p in ipairs({a,b}) do ww(p+0xba,128);ww(p+0xbc,0) end
  wb(0x100ac6,0x99)
 end
end
function T.after()
 if power_pending and frames>=power_pending and not T.previewing and not switching and live() then
  power_pending=nil;save()
 end
 if switching then
  local a,b=live()
  if a and frames-switching.start>=3 then
   local slot=switching.slot;local d=api.animality.definitions[switching.id]
   switching=nil;save();say('P'..slot..': '..(d.character or d.name)..'. G/H preview, R reset.')
  elseif frames-switching.start>120 then
   switching=nil;checkpoint=nil;say('Character load did not finish. Start a new match.')
  end
  return
 end
 if not T.previewing then return end
 local active=api.animality and api.animality.status()
 if active then pending=nil;finished=nil
 elseif not pending then
  finished=finished or frames
  if frames-finished>=45 then T.restore() end
 elseif frames-pending>120 then
  T.restore();say('Preview could not start; practice position restored.')
 end
end
function T.draw()
 if not gui or not gui.text then return end
 if T.enabled then
  gui.text(2,2,'TRAINING T:off G/H:preview R:reset')
  gui.text(2,12,'P1 hero J/K color O | P2 hero N/M color P')
  local a,b=players()
  if a then
   local da,db=api.animality.definitions[rb(a+0xf6)],api.animality.definitions[rb(b+0xf6)]
   gui.text(2,22,'P1 '..(da and (da.character or da.name) or '?')..' | P2 '..(db and (db.character or db.name) or '?'))
   gui.text(2,42,'POW P1 [/] '..math.min(32,rb(a+0xf0))..'/32 | P2 num -/+ '..math.min(32,rb(b+0xf0))..'/32')
  end
 end
 if frames<notice_until then gui.text(2,32,notice) end
end
return T
end
