-- Clip overlay pixels under live native foreground tiles.
-- Read-only VRAM mirror: CPU write hooks never modify emulated video registers.
return function(memory,folder)
 local f=assert(io.open(folder..'assets/foreground/sprite-opacity.bin','rb'))
 local opacity=f:read('*a');f:close()
 local f=assert(io.open(folder..'assets/foreground/zoom-y.bin','rb'))
 local zoomy=f:read('*a');f:close()
 local f=assert(io.open(folder..'assets/foreground/fixed-opacity.bin','rb'))
 local fixed=f:read('*a');f:close()
 local M={vram={},layers={},clipped=0}
 local pointer,bank,modulo=nil,0,1
 local floor=math.floor
 local function word(address,value)
  local reg=address%16
  if reg==0 then pointer=value%32768;bank=value>=32768 and 32768 or 0
  elseif reg==4 then modulo=value>=32768 and value-65536 or value
  elseif reg==2 and pointer then
   M.vram[bank+pointer]=value
   pointer=(pointer+modulo)%32768
  end
 end
 local function hook(address,size,value)
  if size==4 then word(address,floor(value/65536)%65536);word(address+2,value%65536)
  elseif size==2 then word(address,value%65536)
  elseif size==1 and address%2==0 then word(address,value*257) end
 end
 if memory.registerwrite then memory.registerwrite(0x3c0000,6,hook) end
 -- The native renderer sorts commands by drawing layer. Capture the layer of
 -- each emitted column, separately for both alternating sprite buffers.
 -- 3330 follows frame-header decoding; 100B78 is the current bank cursor.
 if memory.registerexec and memory.getregister then
  memory.registerexec(0x3330,2,function()
   local node=memory.getregister('m68000.a6')
   if not node or node<0x101040 or node>=0x102000 or node%64~=0 then return end
   local rb=memory.readbyte
   local function rw(a) return rb(a)*256+rb(a+1) end
   local first=rw(0x100b78)+1
   local width=rw(node+6)
   local layer=rw(node+4)
   if first<0x51 or first+width>0x141 then return end
   for column=first,first+width-1 do M.layers[column]=layer end
  end)
 end
 function M.reset() M.vram={};M.layers={};pointer=nil;M.clipped=0 end
 -- Verified Neo Geo horizontal shrink sampling, indexed by width minus one.
 local xt={
  {8},{4,8},{4,8,12},{2,4,8,12},{2,4,8,12,14},
  {2,4,6,8,12,14},{2,4,6,8,10,12,14},{0,2,4,6,8,10,12,14},
  {0,2,4,6,8,9,10,12,14},{0,2,3,4,6,8,9,10,12,14},
  {0,2,3,4,6,8,9,10,12,14,15},{0,2,3,4,6,7,8,9,10,12,14,15},
  {0,2,3,4,6,7,8,9,10,12,13,14,15},{0,1,2,3,4,6,7,8,9,10,12,13,14,15},
  {0,1,2,3,4,6,7,8,9,10,11,12,13,14,15},{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}}
 function M.clip(data,ox,oy)
  local width=data:byte(3)*256+data:byte(4)
  local height=data:byte(5)*256+data:byte(6)
  local v=M.vram
  local animation=memory.readword and memory.readword(0x3c0006)%8 or 0
  local hidden={}
  local x,y,zx,zy,rows=0,0,15,255,0
  for sprite=0,380 do
   local yc=v[0x8200+sprite] or 0
   local z=v[0x8000+sprite] or 0
   if floor(yc/64)%2==1 then x=(x+zx+1)%512
   else x=floor((v[0x8400+sprite] or 0)/128);y=(512-floor(yc/128))%512;rows=yc%64;zy=z%256 end
   zx=floor(z/256)%16
   local sx=x>=480 and x-512 or x
   local layer=M.layers[sprite] or 0
   -- Fighters use 006x; native foreground stage objects use 010x.
   if layer>=0x100 and layer<0xffff and rows>0 and sx<ox+width and sx+zx>=ox then
     for sy=math.max(0,oy),math.min(223,oy+height-1) do
      local line=(sy+16-y)%512
      if rows>=32 or line<rows*16 then
       local zoomline=line%256
       local invert=line>=256
       if invert then zoomline=255-zoomline end
       if rows>32 then
        zoomline=zoomline%((zy+1)*2)
        if zoomline>zy then zoomline=(zy+1)*2-1-zoomline;invert=not invert end
       end
       local lookup=zoomy:byte(zy*256+zoomline+1)
       local row=floor(lookup/16);local ty=lookup%16
       if invert then row=31-row;ty=15-ty end
       local attr=v[sprite*64+row*2+1] or 0
       local tile=(v[sprite*64+row*2] or 0)+floor(attr/16)%16*65536
       if floor(attr/8)%2==1 then tile=tile-tile%8+animation
       elseif floor(attr/4)%2==1 then tile=tile-tile%4+animation%4 end
       if tile*32+32<=#opacity then
        if floor(attr/2)%2==1 then ty=15-ty end
        local offset=tile*32+ty*2+1
        local bits=opacity:byte(offset)+opacity:byte(offset+1)*256
        for dx,sourcex in ipairs(xt[zx+1]) do
         local px=sx+dx-1
         if px>=ox and px<ox+width then
          local tx=attr%2==1 and 15-sourcex or sourcex
          if floor(bits/2^tx)%2==1 then hidden[(sy-oy)*width+px-ox]=true end
         end
        end
       end
      end
     end
   end
  end
  -- The native fixed layer (POW signs, meters and text) draws above sprites.
  -- Its 8x8 tilemap is column-major; visible scanlines begin at hardware y=16.
  for sy=math.max(0,oy),math.min(223,oy+height-1) do
   local ty=floor((sy+16)/8)
   local row=(sy+16)%8
   for tx=math.max(0,floor(ox/8)),math.min(39,floor((ox+width-1)/8)) do
    local entry=v[0x7000+tx*32+ty]
    if entry then
     local bits=fixed:byte((entry%4096)*8+row+1) or 0
     if bits~=0 then
      for px=math.max(ox,tx*8),math.min(ox+width-1,tx*8+7) do
       if floor(bits/2^(px-tx*8))%2==1 then hidden[(sy-oy)*width+px-ox]=true end
      end
     end
    end
   end
  end
  if not next(hidden) then M.clipped=0;return data end
  local result={data:sub(1,11)}
  local cursor,count=12,0
  for i=0,width*height-1 do
   local pos=12+i*4
   if hidden[i] and data:byte(pos)<127 then
    result[#result+1]=data:sub(cursor,pos-1);result[#result+1]=string.char(127)
    cursor=pos+1;count=count+1
   end
  end
  result[#result+1]=data:sub(cursor);M.clipped=count
  return count>0 and table.concat(result) or data
 end
 return M
end
