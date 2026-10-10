local hook
local memory={registerwrite=function(address,size,callback) assert(address==0x3c0000 and size==6);hook=callback end}
local M=assert(loadfile('animality-foreground.lua'))()(memory,'')
-- Check bus-width handling, bank addressing, positive/negative modulo and wrap.
hook(0x3c0000,4,0x82001234)
assert(M.vram[0x8200]==0x1234)
hook(0x3c0004,2,0xffff);hook(0x3c0002,2,0xabcd);hook(0x3c0002,2,0x4567)
assert(M.vram[0x8201]==0xabcd and M.vram[0x8200]==0x4567)
hook(0x3c0000,2,0x8000);hook(0x3c0002,2,0x1357);hook(0x3c0002,2,0x2468)
assert(M.vram[0x8000]==0x1357 and M.vram[0xffff]==0x2468)
M.reset();assert(next(M.vram)==nil)
local f=assert(io.open('reports/foreground-vram.bin','rb'));local raw=f:read('*a');f:close()
for i=0,65535 do M.vram[i]=raw:byte(i*2+1)+raw:byte(i*2+2)*256 end
-- This regression isolates stage props; HUD coverage has its own test.
for i=0x7000,0x74ff do M.vram[i]=nil end
f=assert(io.open('reports/foreground-layers.bin','rb'));local layers=f:read('*a');f:close()
for i=0,380 do M.layers[i]=layers:byte(i*2+1)*256+layers:byte(i*2+2) end
local data=string.char(255,254,1,64,0,224,1,255,255,255,255)..string.rep(string.char(0,17,34,51),320*224)
for _,zoom in ipairs({255,191,127}) do
 for i=0,380 do M.vram[0x8000+i]=(math.floor(zoom/16)*256)+zoom end
 local masked=M.clip(data,0,0)
 assert(M.clipped>0 and #masked==#data and masked:sub(1,11)==data:sub(1,11))
 f=assert(io.open('reports/foreground-mask-'..zoom..'.gd','wb'));f:write(masked);f:close()
 print('PASS foreground zoom='..zoom..' pixels='..M.clipped)
end
M.reset();assert(M.clip(data,0,0)==data and M.clipped==0)
print('PASS video write mirror and reset; GD headers, lengths and no-object behavior.')
