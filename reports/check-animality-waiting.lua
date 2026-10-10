-- Test every built definition using real packed assets, without enabling them for play.
local original_loadfile=loadfile
loadfile=function(path,...)
 if path:match('animalities%.lua$') then path='reports/animalities-all-built.lua' end
 return original_loadfile(path,...)
end
local ram={}
local function rb(a) return ram[a] or 0 end
local function wb(a,v) ram[a]=v end
local function ww(a,v) v=math.floor(v)%65536;wb(a,math.floor(v/256));wb(a+1,v%256) end
local function rd(a) return rb(a)*16777216+rb(a+1)*65536+rb(a+2)*256+rb(a+3) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local factory=assert(loadfile('animality.lua'))(true)
local A=factory({readbyte=rb,readdword=rd,writebyte=wb},{})
loadfile=original_loadfile
local count=0
for id,d in pairs(A.definitions) do
 for _,direction in ipairs({1,-1}) do
  ram={}
  local actor,victim=0x104000,0x106000
  wd(0x100a46,actor);wd(0x100a4a,victim)
  wd(actor,0x25314);wd(victim,0x25314)
  wb(actor+0xf6,id);wb(victim+0xf6,0)
  ww(actor+0xba,128);ww(victim+0xba,0);ww(victim+0xe6,0x318)
  ww(actor+0x4e,direction==1 and 180 or 400);ww(victim+0x4e,290)
  ww(victim+0x66,0xe1);wb(victim+0x7d,31)
  wd(0x102000,0);ww(0x102010,65535)
  local start=rb(actor+0x4e)*256+rb(actor+0x4f)
  A.after();assert(A.status())
  local wait=d.movement=='flight' and 3 or 4
  for tick=1,180 do
   A.before();A.after();local s=assert(A.status())
   assert(rd(actor)==0x25314,'handler restored')
   if tick>=44 then assert(s.frame==wait,d.slug..' wrong waiting pose '..s.frame) end
   assert(rb(actor+0x4e)*256+rb(actor+0x4f)==start,d.slug..' moved before takeoff')
   assert(s.lift==0,d.slug..' lifted before takeoff')
  end
  for native_tick=33,39 do
   wb(victim+0x7d,native_tick);A.before();A.after()
   local s=assert(A.status());assert(s.lift>=0)
   if d.movement~='flight' or native_tick>=38 then assert(s.frame==7,d.slug..' missing approach pose')
   else assert(s.frame==5 or s.frame==6,d.slug..' invalid wingbeat') end
  end
  wd(0x102000,0x4456a);wd(0x1020cc,victim)
  A.before();A.after();assert(A.status().frame==8,'missing strike')
  for h=1,99 do
   A.before();A.after();local s=assert(A.status())
   if h>=25 then assert(rb(actor+0x4e)*256+rb(actor+0x4f)==start,d.slug..' sliding in landing/rest pose') end
  end
  A.before();A.after();assert(not A.status(),'must finish')
  assert(rd(actor)==0x25314)
  A.cancel(false,'next waiting fixture')
 end
 count=count+1;print('PASS waiting/takeoff/landing both directions: '..d.slug)
end
assert(count==17,count)
print('PASS all 17 built animals: stationary waiting, timed takeoff, no resting slide, native cleanup.')
