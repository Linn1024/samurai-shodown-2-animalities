-- Capture live render queues and VRAM on each native stage.
local stage=assert(SS2_STAGE)
local slug=assert(SS2_STAGE_SLUG)
local m=manager.machine
local mem,vram,fields,taps
local frame=0
local layers={}
local function press(name,value) fields[name]:set_value(value and 1 or 0) end
emu.register_frame_done(function()
 if not mem then
  mem=m.devices[':maincpu'].spaces.program;if not mem then return end
  vram=emu.item(m.devices[':spritegen'].items['0/m_videoram.get()'])
  fields={};taps={}
  for _,port in pairs(m.ioport.ports) do for name,f in pairs(port.fields) do fields[name]=f;f:set_input_seq('standard',m.input:seq_from_tokens('')) end end
  taps[#taps+1]=mem:install_read_tap(0x100ad8,0x100ad9,'stage-background',function(a,d,mask) return math.floor(d/256)*256+stage end)
  taps[#taps+1]=mem:install_write_tap(0x100ad8,0x100ad9,'stage-background-write',function(a,d,mask) return math.floor(d/256)*256+stage end)
  taps[#taps+1]=mem:install_read_tap(0x3330,0x3331,'foreground-layer',function()
   local node=m.devices[':maincpu'].state.A6.value
   if node>=0x101040 and node<0x102000 and node%64==0 then
    local first=mem:read_u16(0x100b78)+1
    local count=mem:read_u16(node+6)
    if first>=0x51 and first+count<=0x141 then
     for column=first,first+count-1 do layers[column]=mem:read_u16(node+4) end
    end
   end
  end)
 end
 frame=frame+1
 if frame<2400 then mem:write_u8(0x100ad9,stage) end
 press('Coin 1',frame>1000 and frame<2200 and frame%180<20)
 press('1 Player Start',frame>1100 and frame<2200 and frame%180>=50 and frame%180<60)
 press('P1 Button 1',frame>1200 and frame<2200 and frame%180>=100 and frame%180<110)
 if frame>=1700 and frame<2100 then mem:write_u8(0x100d0b,0) end
 local p1,p2=mem:read_u32(0x100a46),mem:read_u32(0x100a4a)
 if frame==2400 then
  for _,p in ipairs({p1,p2}) do
   assert(p>=0x102000 and p<0x10fe00)
   taps[#taps+1]=mem:install_write_tap(p+0xe8,p+0xeb,'stage-idle-'..p,function() return 0 end)
  end
 end
 if frame>=2450 then
  local index=math.min(3,math.floor((frame-2450)/150)+1)
  local position=({{96,176},{240,320},{464,544}})[index]
  for i,p in ipairs({p1,p2}) do
   mem:write_u16(p+0x4e,position[i]);mem:write_u16(p+0xe6,0);mem:write_u16(p+0xba,128)
  end
  if frame==2550 or frame==2700 or frame==2850 then
   local root='C:/TEMP2/SS2/reports/stages/'..slug..'-'..index
   m.screens[':screen']:snapshot(root..'.png')
   local f=assert(io.open(root..'-vram.bin','wb'));f:write(vram:read_block(0,vram.size*vram.count));f:close()
   f=assert(io.open(root..'-ram.bin','wb'))
   for a=0x100000,0x10ffff do f:write(string.char(mem:read_u8(a))) end
   f:close()
   f=assert(io.open(root..'-layers.bin','wb'))
   for i=0,380 do local layer=layers[i] or 0;f:write(string.char(math.floor(layer/256),layer%256)) end
   f:close()
   f=assert(io.open(root..'-animation.txt','w'));f:write(mem:read_u16(0x3c0006)%8);f:close()
   print('STAGE CAPTURE '..slug..' '..index..' background='..mem:read_u8(0x100ad9))
  end
 end
end)
