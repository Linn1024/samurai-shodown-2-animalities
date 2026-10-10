local M=assert(loadfile('animality-foreground.lua'))()({},'')
local function file(path) local f=assert(io.open(path,'rb'));local d=f:read('*a');f:close();return d end
local slugs={'haohmaru','nakoruru','hanzo','galford','wan-fu','ukyo','kyoshiro','gen-an','earthquake','jubei','charlotte','genjuro','cham-cham','sieger','nicotine','mizuki','kuroko'}
local data=string.char(255,254,1,64,0,224,1,255,255,255,255)..string.rep(string.char(0,17,34,51),320*224)
for _,slug in ipairs(slugs) do
 for index=1,3 do
  local root='reports/stages/'..slug..'-'..index
  M.reset()
  local v=file(root..'-vram.bin')
  for i=0,#v/2-1 do M.vram[i]=v:byte(i*2+1)+v:byte(i*2+2)*256 end
  -- Isolate stage-object regression; check-hud-foreground covers the fixed layer.
  for i=0x7000,0x74ff do M.vram[i]=nil end
  local layers=file(root..'-layers.bin')
  for i=0,380 do M.layers[i]=layers:byte(i*2+1)*256+layers:byte(i*2+2) end
  local masked=M.clip(data,0,0)
  assert(#masked==#data and masked:sub(1,11)==data:sub(1,11))
  local f=assert(io.open(root..'-mask.gd','wb'));f:write(masked);f:close()
  print('PASS stage '..slug..' '..index..' foreground_pixels='..M.clipped)
 end
end
