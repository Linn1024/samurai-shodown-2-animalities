-- Research fixture: capture each native fighter, isolated to P1's eight palettes.
local m=manager.machine
local mem
local fields={}
local function press(name,on) if on then fields[name]:set_value(1) else fields[name]:clear_value() end end
local roster={{9,'jubei-fixed'}}
local frame=0
local taps={}
local function valid(p) return p>=0x102000 and p<0x10fd00 end
emu.register_frame_done(function()
 if not mem then
  mem=m.devices[':maincpu'].spaces.program
  if not mem then return end
  for _,port in pairs(m.ioport.ports) do for name,f in pairs(port.fields) do fields[name]=f;f:set_input_seq('standard',m.input:seq_from_tokens('')) end end
 end
 frame=frame+1
 press('Coin 1',frame>1000 and frame<2200 and frame%180<20)
 press('1 Player Start',frame>1100 and frame<2200 and frame%180>=50 and frame%180<60)
 press('P1 Button 1',frame>1200 and frame<2200 and frame%180>=100 and frame%180<110)
 if frame>=1700 and frame<2100 then mem:write_u8(0x100d0b,0) end
 local p1,p2=mem:read_u32(0x100a46),mem:read_u32(0x100a4a)
 if frame==2400 and valid(p1) and valid(p2) then
  for _,p in ipairs({p1,p2}) do taps[#taps+1]=mem:install_write_tap(p+0xe8,p+0xeb,'roster-idle-'..p,function() return 0 end) end
  taps[#taps+1]=mem:install_write_tap(0x400000,0x401fff,'roster-isolate',function(a,d,mask) if a<0x400200 or a>=0x400300 then return 0x0f0f end end)
 end
 if frame>=2500 and valid(p1) and valid(p2) then
  local index=math.floor((frame-2500)/90)+1
  local phase=(frame-2500)%90
  local item=roster[index]
  if not item then return end
  local id,name=item[1],item[2]
  mem:write_u32(p2,0x385c) -- project actor position without drawing opponent

  if phase==0 then
   mem:write_u8(p1+0xf6,id);mem:write_u16(p1+0x64,id)
   mem:write_u16(p1+0xe6,0);mem:write_u16(p1+0xc4,0xffff)
   mem:write_u8(p1+0xf9,0);mem:write_u8(p1+0xfb,0)
   mem:write_u16(p1+0xba,128);mem:write_u16(p2+0xba,128)
   mem:write_u16(p1+0x4e,240);mem:write_u16(p2+0x4e,295)
   mem:write_u16(p1+0x50,224);mem:write_u16(p1+0x52,0);mem:write_u16(p1+0x56,0)
   mem:write_u8(p1+0x7f,0)
   local palette_index=mem:read_u8(0xfca4+id)
   local source=mem:read_u32(0xfd10+palette_index*4)
   for bank=0,7 do mem:write_u32(0x10ec40+bank*4,source+bank*32) end
   for a=0x400000,0x401ffe,2 do
    mem:write_u16(a,(a>=0x400200 and a<0x400300) and mem:read_u16(source+a-0x400200) or 0x0f0f)
   end
   print(string.format('CAPTURE %s id=%d palette=%06x p1=%06x',name,id,source,p1))
   local f=assert(io.open('reports/native-'..name..'-palette.txt','w'));f:write(string.format('%06x',source));f:close()
  end
  if phase==20 or phase==45 then m.screens[':screen']:snapshot('C:/TEMP2/SS2/reports/native-'..name..'-roster-'..phase..'.png') end
  if phase==45 then
   local f=assert(io.open('reports/native-'..name..'-anchor.txt','w'))
   f:write(mem:read_u16(p1+0x5c)..' '..(mem:read_u16(p1+0x5e)-16)..' '..mem:read_u8(p1+0x7a));f:close()
  end
 end
end)
