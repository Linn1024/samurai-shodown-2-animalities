SS2_TRAINING_TEST_SLUG='pow-control'
SS2_NO_MAIN_LOOP=true
local root='C:/TEMP2/SS2/'
local test_slug=SS2_TRAINING_TEST_SLUG or 'haohmaru'
local log=assert(io.open(root..'reports/fbneo-'..test_slug..'-test.log','w'))
local oldprint=print
print=function(...)
 local v={} for i,x in ipairs({...}) do v[i]=tostring(x) end
 log:write(table.concat(v,' ')..'\n');log:flush();oldprint(...)
end
input.get=function() return {} end -- Isolate this owned test from physical typing.
local api=dofile(root..'ultimate.lua');local T,A=assert(api.training),assert(api.animality)
local selected=SS2_TRAINING_TEST_IDS or T.roster
local before=emu.registerbefore(nil);local after=emu.registerafter(nil)
local rb,rd=memory.readbyte,memory.readdword
local function rw(a) return rb(a)*256+rb(a+1) end
local function ww(a,v) memory.writebyte(a,math.floor(v/256)%256);memory.writebyte(a+1,v%256) end
local frame,index,slot,phase=0,1,1,'boot'
local changed,seen,started,stop=false,false,false,false
local requested,phase_frame=nil,0
local powvalue=0
local function guarded(fn)
 return function()
  local ok,err=xpcall(fn,debug.traceback)
  if not ok then print('TEST ERROR '..tostring(err));emu.pause();error(err) end
 end
end
local function select_fighter(which,id)
 local actor=rd(which==1 and 0x100a46 or 0x100a4a)
 local current,target
 for i,v in ipairs(T.roster) do if v==rb(actor+0xf6) then current=i end;if v==id then target=i end end
 assert(current and target)
 assert(T.change(which,target-current),'character change rejected')
 requested=id;phase='loading';phase_frame=frame
end
emu.speedmode('turbo')
emu.registerbefore(guarded(function()
 frame=frame+1
 joypad.set({['P1 Coin']=frame<2500 and frame%180<20,
 ['P1 Start']=frame<2500 and frame%180>=50 and frame%180<60,
 ['P1 Button A']=frame<2500 and frame%180>=100 and frame%180<110})
 if frame>=1000 and frame<2300 then memory.writebyte(0x100d0b,0) end
 if frame==2501 then
  if SS2_TRAINING_TEST_NORMAL_SPEED then emu.speedmode('normal') end
  local a,b=rd(0x100a46),rd(0x100a4a)
  for _,p in ipairs({a,b}) do
   ww(p+0xe6,0);ww(p+0xc4,65535);ww(p+0xba,128);ww(p+0xbc,0)
   ww(p+0x50,224);ww(p+0x52,0);ww(p+0x56,0)
  end
  ww(a+0x4e,240);ww(b+0x4e,295)
  T.toggle();phase='ready'
 end
 if frame%500==0 then print('TEST FRAME '..frame..' phase='..phase) end
 if phase=='pow' or phase=='pow-lower' then local a,b=rd(0x100a46),rd(0x100a4a);ww(a+0x4e,150);ww(b+0x4e,390) end
 if before then before() end
end))
emu.registerafter(guarded(function()
 if after then after() end
 local a,b=rd(0x100a46),rd(0x100a4a)
 if phase=='ready' and frame>=2540 and frame-phase_frame>=8 then
  assert(#T.roster==17,'all 17 characters must be selectable')
  assert(T.enabled and rw(a+0xba)==128 and rw(b+0xba)==128,
   string.format('ready enabled=%s P1=%x callback=%x hp=%d state=%x P2=%x callback=%x hp=%d state=%x',
   tostring(T.enabled),a,rd(a),rw(a+0xba),rw(a+0xe6),b,rd(b),rw(b+0xba),rw(b+0xe6)))
  select_fighter(slot,selected[index])
 elseif phase=='loading' and frame-phase_frame>=8 then
  local actor=slot==2 and b or a
  assert(rd(a)==0x25314 and rd(b)==0x25314,'native character initialization not complete')
  assert(rb(actor+0xf6)==requested and rw(actor+0x64)==requested,'wrong fighter/animation bank')
  assert(rw(a+0xba)==128 and rw(b+0xba)==128,'health must remain full')
  local d=A.definitions[requested];local ptr=slot==2 and 0x10ec60 or 0x10ec40
  assert(rd(ptr)==d.palette,'wrong costume pointer')
  print('PASS native character switch P'..slot..' '..d.slug)
  phase='pow';powvalue=0;phase_frame=frame;assert(T.pow(slot,-32))
 
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
 elseif phase=='preview' then
  local s=A.status()
  if s then
   seen=true
   assert(rd(s.victim)==0x25314,'paused native callback leaked')
   if not started then
    started=true;local f=assert(io.open(root..'reports/fbneo-'..test_slug..'-started.txt','w'));f:write(frame);f:close()
   end
  elseif seen and not T.previewing then
   assert(rd(a)==0x25314 and rd(b)==0x25314)
   assert(rw(a+0xba)==128 and rw(b+0xba)==128)
   local actor=slot==2 and b or a;assert(rb(actor+0xf6)==requested,'checkpoint restored old fighter')
   assert(rb(actor+0xf0)==16,'preview reset lost POW selection')
   print('PASS training preview/restore P'..slot..' '..A.definitions[requested].slug)
   index=index+1
   if index<=#selected then select_fighter(slot,selected[index])
   elseif slot==1 then
    -- A regular human opponent guarantees an ordinary fountain death bank.
    local current,target
    for i,v in ipairs(T.roster) do if v==rb(a+0xf6) then current=i end;if v==0 then target=i end end
    assert(current and target and T.change(1,target-current));slot=2;index=1;phase='ready';phase_frame=frame
   else
    assert(A.events==#selected*2,'selected previews for both player slots required')
    assert(T.restore());T.toggle();assert(not T.enabled)
    print('PASS FBNeo '..test_slug..' events='..A.events..' handler='..string.format('%x',rd(a)))
    phase='done';stop=true
   end
  end
 end
 if frame>28000 and phase~='done' then error('Training roster timeout: '..phase..' P'..slot..' index '..index) end
end))
print('TEST hooks ready; selected='..#selected..' slug='..test_slug)
while true do emu.frameadvance();if stop then stop=false;emu.pause() end end
