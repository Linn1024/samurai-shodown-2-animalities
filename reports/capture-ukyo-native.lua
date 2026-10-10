local m=manager.machine
local mem=m.devices[':maincpu'].spaces.program
local fields={}
for _,port in pairs(m.ioport.ports) do for name,f in pairs(port.fields) do fields[name]=f f:set_input_seq('standard',m.input:seq_from_tokens('')) end end
local function press(name,on) if on then fields[name]:set_value(1) else fields[name]:clear_value() end end
local frame=0
local taps={}
local vram=emu.item(m.devices[':spritegen'].items['0/m_videoram.get()'])
emu.register_frame_done(function()
 frame=frame+1
 press('Coin 1',frame>1000 and frame<2200 and frame%180<20)
 press('1 Player Start',frame>1100 and frame<2200 and frame%180>=50 and frame%180<60)
 if frame<=2200 then press('P1 Button 1',frame>1200 and frame<2200 and frame%180>=100 and frame%180<110) end
 if frame>=1700 and frame<2100 then mem:write_u8(0x100d0b,5) end
 local p1,p2=mem:read_u32(0x100a46),mem:read_u32(0x100a4a)
 if frame==2400 then
  for _,p in ipairs({p1,p2}) do taps[#taps+1]=mem:install_write_tap(p+0xe8,p+0xeb,'no-input-'..p,function(a,d,mask) return 0 end) end
 end
 if frame==2500 then
  for a=0x400000,0x401ffe,2 do if a>=0x400800 then mem:write_u16(a,0x0f0f) end end
  taps[#taps+1]=mem:install_write_tap(0x400000,0x401fff,'isolate-ukyo',function(a,d,mask) if a>=0x400800 then return 0x0f0f end end)
  mem:write_u16(p1+0xe6,0) mem:write_u16(p2+0xe6,0)
 end
 if frame>=2501 and frame<=2530 or frame>=2601 and frame<=2620 or frame>=2701 and frame<=2770 then
  m.screens[':screen']:snapshot(string.format('C:/TEMP2/SS2/reports/native-ukyo-%d.png',frame))
  if frame==2501 then
   local f=assert(io.open('reports/native-ukyo-vram.bin','wb')); f:write(vram:read_block(0,vram.size*vram.count)); f:close()
  end
 end
 if frame==2600 then mem:write_u16(p1+0xe6,2) end
 if frame==2700 then mem:write_u16(p1+0xe6,0x600) end
 if frame==2800 then print('NATIVE CAPTURE DONE') end
end)



