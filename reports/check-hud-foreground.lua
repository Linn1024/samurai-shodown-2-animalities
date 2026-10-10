local M=assert(loadfile('animality-foreground.lua'))()({},'')
local function file(path) local f=assert(io.open(path,'rb'));local d=f:read('*a');f:close();return d end
local rom=file('work/hack/063-s1sp.s1')
local checks=0
for _,path in ipairs({'reports/stages/nicotine-2-vram.bin','reports/pow-hud-p1-vram.bin','reports/pow-hud-p2-vram.bin'}) do
 M.reset();local raw=file(path)
 for a=0x7000,0x74ff do
  local w=raw:byte(a*2+1)+raw:byte(a*2+2)*256
  if w~=0 then M.vram[a]=w end
 end
 for _,area in ipairs({{0,0,320,224},{-5,170,128,80},{220,170,128,80},{50,180,64,64},{0,-8,96,64}}) do
  local ox,oy,w,h=(unpack or table.unpack)(area)
  local original=string.char(255,254,math.floor(w/256),w%256,math.floor(h/256),h%256,1,255,255,255,255)..string.rep(string.char(0,17,34,51),w*h)
  local actual=M.clip(original,ox,oy);local hidden=0
  assert(#actual==#original and actual:sub(1,11)==original:sub(1,11))
  for y=0,h-1 do for x=0,w-1 do
   local sx,sy=ox+x,oy+y;local opaque=false
   if sx>=0 and sx<320 and sy>=0 and sy<224 then
    local entry=M.vram[0x7000+math.floor(sx/8)*32+math.floor((sy+16)/8)]
    if entry then
     local tx=sx%8;local offsets={16,24,0,8}
     local packed=rom:byte(entry%4096*32+offsets[math.floor(tx/2)+1]+(sy+16)%8+1)
     opaque=(tx%2==0 and packed%16 or math.floor(packed/16))~=0
    end
   end
   local p=12+(y*w+x)*4
   assert(actual:byte(p)==(opaque and 127 or 0),'HUD opacity or transparent gap mismatch')
   assert(actual:sub(p+1,p+3)==original:sub(p+1,p+3),'HUD masking changed RGB')
   if opaque then hidden=hidden+1 end
   checks=checks+1
  end end
  assert(M.clipped==hidden)
  if ox==0 and oy==0 then
   local f=assert(io.open(path..'-hud-mask.gd','wb'));f:write(actual);f:close()
  end
 end
 print('PASS fixed HUD opacity, POW normal/full, transparent gaps and screen edges: '..path)
end
M.reset()
local data=string.char(255,254,0,1,0,1,1,255,255,255,255,0,1,2,3)
assert(M.clip(data,0,0)==data)
print('PASS HUD '..checks..' independently decoded S-ROM pixel checks; untouched RGB, GD headers and unknown VRAM.')
