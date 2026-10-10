local function file(path) local f=assert(io.open(path,'rb'));local d=f:read('*a');f:close();return d end
local saved=file('reports/native-palette-fixture-ram.bin')
local rom=file('work/hack/063sp.p2')
local factory=assert(loadfile('animality.lua'))(true)
local test_id=SS2_TEST_ID or 5
local source_palette=SS2_TEST_PALETTE or 0x214600
local file_prefix=SS2_TEST_SLUG and ('palette-'..SS2_TEST_SLUG) or 'palette'
for slot=1,2 do
 for variant=0,1 do
  local ram={}
  for i=1,#saved do ram[0x100000+i-1]=saved:byte(i) end
  local function rb(a)
   if a>=0x200000 and a<0x300000 then return rom:byte((a-0x200000)%2==0 and a-0x200000+2 or a-0x200000) end
   return ram[a] or 0
  end
  local function wb(a,v) ram[a]=v end
  local function ww(a,v) wb(a,math.floor(v/256)%256);wb(a+1,v%256) end
  local function rd(a) return rb(a)*16777216+rb(a+1)*65536+rb(a+2)*256+rb(a+3) end
  local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
  local actor,victim=rd(0x100a46),rd(0x100a4a)
  wb(actor+0xf6,test_id)
  wb(actor+0x81,0);wb(actor+0x82,0)
  if slot==2 then wd(0x100a46,victim);wd(0x100a4a,actor) end
  wd(actor,0x25314);wd(victim,0x25314)
  ww(actor+0xba,37);ww(victim+0xba,0);ww(victim+0xe6,0x318)
  for bank=0,7 do wd(0x10ec40+(slot-1)*32+bank*4,source_palette+variant*256+bank*32) end
  for offset=0,254,2 do ww(0x400200+(slot-1)*256+offset,rb(source_palette+variant*256+offset)*256+rb(source_palette+variant*256+offset+1)) end
  local last,cleared
  local gui={clearuncommitted=function() last=nil;cleared=true end,gdoverlay=function(x,y,data) last=data end}
  local A=factory({readbyte=rb,readdword=rd,writebyte=wb},gui)
  A.after();assert(A.status() and A.status().palette,'must select costume palette')
  for _,direction in ipairs({1,-1}) do
   for _,zoom in ipairs({64,80,96,112,128}) do
    wb(actor+0x7a,256-zoom*2)
    for frame=0,15 do
     A.status().frame=frame;A.status().direction=direction
     A.draw();assert(last,'sprite must draw')
     local path=string.format('reports/%s-p%d-v%d-%s-%d-%02d.gd',file_prefix,slot,variant,direction==1 and 'right' or 'left',zoom,frame)
     local f=assert(io.open(path,'wb'));f:write(last);f:close()
    end
   end
  end
  A.cancel(true,'palette verification completed');assert(last==nil and cleared)
  print(string.format('PASS P%d costume %d: 160 sprites rendered and cleared.',slot,variant))
 end
end
