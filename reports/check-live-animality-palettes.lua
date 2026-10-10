local function file(path) local f=assert(io.open(path,'rb'));local d=f:read('*a');f:close();return d end
local saved=file('reports/native-palette-fixture-ram.bin')
local rom=file('work/hack/063sp.p2')
local ram={}
local function rb(a)
 if a>=0x200000 and a<0x300000 then return rom:byte((a-0x200000)%2==0 and a-0x200000+2 or a-0x200000) end
 return ram[a] or 0
end
local function wb(a,v) ram[a]=v end
local function rw(a) return rb(a)*256+rb(a+1) end
local function ww(a,v) wb(a,math.floor(v/256)%256);wb(a+1,v%256) end
local function rd(a) return rw(a)*65536+rw(a+2) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local last
local A=assert(loadfile('animality.lua'))(true)({readbyte=rb,readdword=rd,writebyte=wb},
 {clearuncommitted=function() last=nil end,gdoverlay=function(x,y,data) last=data end})
local count=0
for id,d in pairs(A.definitions) do
 for slot=1,2 do for variant=0,1 do
  ram={};for i=1,#saved do ram[0x100000+i-1]=saved:byte(i) end
  local actor,victim=rd(0x100a46),rd(0x100a4a)
  if slot==2 then wd(0x100a46,victim);wd(0x100a4a,actor) end
  wb(actor+0xf6,id);wd(actor,0x25314);wd(victim,0x25314)
  wb(actor+0x81,0);wb(actor+0x82,0)
  ww(actor+0xba,128);ww(victim+0xba,0);ww(victim+0xe6,0x318)
  local base=0x400200+(slot-1)*256
  -- ROM pointers deliberately stay on main while the displayed palette is alternate.
  for bank=0,7 do wd(0x10ec40+(slot-1)*32+bank*4,d.palette+bank*32) end
  local words={}
  for index=0,127 do words[index]=rw(d.palette+variant*256+index*2);ww(base+index*2,words[index]) end
  A.after();assert(A.status())
  -- Verify native body/weapon bank selection, not just changes to RGB words.
  local native_views={}
  for skin=0,2 do for weapon=0,1 do
   wb(actor+0x81,(slot-1)*8+skin);wb(actor+0x82,(slot-1)*8+weapon)
   local s=A.status();s.frame=3;s.direction=1;wb(actor+0x7a,0);A.draw()
   local lut=d.palette_map.rgb
   local function color(w)
    local dark=math.floor(w/32768)%2
    local function ch(n,e) return lut[n*4+e*2+dark+1] end
    return string.char(0,ch(math.floor(w/256)%16,math.floor(w/16384)%2),ch(math.floor(w/16)%16,math.floor(w/8192)%2),ch(w%16,math.floor(w/4096)%2))
   end
   local expected={}
   for _,entry in ipairs(d.palette_map.colors) do
    local index=entry[4]
    if index<48 then index=index%16+skin*16 elseif index>=48 and index<64 then index=index+weapon*16 end
    expected[string.char(0,entry[1],entry[2],entry[3])]=color(words[index])
   end
   local original=d.sprites.right[128][3]
   for p=12,#original,4 do
    local pixel=original:sub(p,p+3);local target=expected[pixel] or pixel
    if d.palette_regions then
     local index=d.palette_regions:byte(3*d.canvas*d.canvas+(p-12)/4+1)
     if index~=255 then target=color(words[index%16+skin*16]) end
    end
    assert(last:sub(p,p+3)==target,d.slug..' incorrect native bank')
   end
   if d.palette_regions and weapon==0 then
    for frame=0,d.frames-1 do for _,direction in ipairs({1,-1}) do
     local s=A.status();s.frame=frame;s.direction=direction;wb(actor+0x7a,0);A.draw()
     local original=d.sprites[direction==1 and 'right' or 'left'][128][frame]
     for p=12,#original,4 do
      local offset=(p-12)/4;local x=offset%d.canvas;local y=math.floor(offset/d.canvas)
      if direction==-1 then x=d.canvas-1-x end
      local index=d.palette_regions:byte(frame*d.canvas*d.canvas+y*d.canvas+x+1)
      local target=expected[original:sub(p,p+3)] or original:sub(p,p+3)
      if index~=255 then
       assert(index>=11 and index<=15,'hat must use only native hat shades')
       target=color(words[index+skin*16])
      end
      assert(last:sub(p,p+3)==target,'owl hat or non-hat material incorrectly mapped')
     end
     count=count+1
    end end
   end
   if weapon==0 then native_views[skin]=last end
   count=count+1
  end end
  if id==7 then assert(native_views[0]~=native_views[1] and native_views[1]~=native_views[2],'Gen-an POW skin colors must change') end
  wb(actor+0x81,(slot-1)*8);wb(actor+0x82,(slot-1)*8)
  local baseline={}
  for phase=1,4 do
   for index=0,127 do ww(base+index*2,phase==2 and 0x0f00 or phase==3 and 0x7fff or words[index]) end
   for _,direction in ipairs({1,-1}) do for _,zoom in ipairs({80,112,128}) do for _,frame in ipairs({0,3,8}) do
    local s=A.status();s.frame=frame;s.direction=direction;wb(actor+0x7a,256-zoom*2)
    A.draw();assert(last)
    local key=direction..':'..zoom..':'..frame
    if phase==1 then baseline[key]=last
    elseif phase==4 then assert(last==baseline[key],d.slug..' stale tint after returning to live base palette')
    else
     local original=baseline[key];assert(last:sub(1,11)==original:sub(1,11))
     local w=phase==2 and 0x0f00 or 0x7fff;local lut=d.palette_map.rgb
     local function channel(n,e) return lut[n*4+e*2+math.floor(w/32768)%2+1] end
     local expected=string.char(0,channel(math.floor(w/256)%16,math.floor(w/16384)%2),channel(math.floor(w/16)%16,math.floor(w/8192)%2),channel(w%16,math.floor(w/4096)%2))
     for pos=12,#last,4 do
      assert(last:byte(pos)==original:byte(pos),'alpha changed')
      if original:byte(pos)==0 then assert(last:sub(pos,pos+3)==expected,d.slug..' stale/incorrect live flash') end
     end
    end
    count=count+1
   end end end
  end
  A.cancel(false,'live palette test complete')
 end end
 print('PASS live palette '..d.slug..': both slots/costumes, red/white transitions and restoration, both directions, three camera sizes.')
end
print('PASS live palette total '..count..' render checks; ROM palette deliberately differs from live colors.')
