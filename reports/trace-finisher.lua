local m=manager.machine
local mem=m.devices[':maincpu'].spaces.program
local fields={}
for _,port in pairs(m.ioport.ports) do for name,field in pairs(port.fields) do fields[name]=field field:set_input_seq('standard',m.input:seq_from_tokens('')) end end
local frame=0
local seen={}
local taps={}
local trace=mem:install_read_tap(0x2a2a2,0x2a2a3,'fountain-logic',function(a,d,mask)
 if frame>=2800 then local p=mem:read_u32(0x100a4a) print(string.format('FOUNTAIN %d idx=%04x fa=%02x phase=%02x',frame,mem:read_u16(p+0x7c),mem:read_u8(p+0xfa),mem:read_u8(p+0xf9))) end
end)
local function press(name,value) if value then fields[name]:set_value(1) else fields[name]:clear_value() end end
local function objects()
 local o=0x102000 local visited={}
 for count=1,256 do
  if o<0x102000 or o>0x10fd00 or o%2~=0 or visited[o] then break end
  visited[o]=true
  local h=mem:read_u32(o) local a=mem:read_u32(o+0x64) local state=mem:read_u16(o+0xe6)
  local desc=string.format('%06x:%08x:%04x',h,a,state)
  if seen[o]~=desc then
   print(string.format('OBJ %d %06x %s parent=%06x hp=%02x x=%d y=%d',frame,o,desc,mem:read_u32(o+0xcc),mem:read_u8(o+0xbb),mem:read_u16(o+0x4e),mem:read_u16(o+0x50)))
   seen[o]=desc
  end
  if mem:read_u16(o+0x10)==0xffff then break end
  o=0x100000+mem:read_u16(o+0xe)
 end
end
emu.register_frame_done(function()
 frame=frame+1
 press('Coin 1',frame>1000 and frame<2200 and frame%180<20)
 press('1 Player Start',frame>1100 and frame<2200 and frame%180>=50 and frame%180<60)
 if frame<=2200 then press('P1 Button 1',frame>1200 and frame<2200 and frame%180>=100 and frame%180<110) end
 if frame>=1700 and frame<2100 then mem:write_u8(0x100d0b,5) end
 local p1,p2=mem:read_u32(0x100a46),mem:read_u32(0x100a4a)
 if frame>=2200 and frame<2800 and p2>=0x102000 and p2<0x10fe00 then mem:write_u16(p2+0xe6,0x2e) end
 if frame>=2750 and frame<2800 then
  mem:write_u8(p2+0xbb,1)
  mem:write_u16(p1+0x4e,240) mem:write_u16(p2+0x4e,295)
  mem:write_u16(p1+0xe6,0)
  mem:write_u16(p2+0xe6,0)
  if frame==2750 then
   -- Leave the opponent's original character graphics intact.
   taps[#taps+1]=mem:install_write_tap(p2+0xe8,p2+0xeb,'no-p2-input',function(a,d,mask) return 0 end)
  end
 end
 if frame>2200 then
  press('P1 Button 1',frame>=2800 and frame<2804 or frame>=3500 and frame%150<4)
  press('P1 Button 2',frame>=2800 and frame<2804 or frame>=3500 and frame%150<4)
 end
 if frame>=2750 then objects() end
 if frame>=2925 and frame<3010 then print(string.format('FRAME %d idx=%04x phase=%02x state=%04x',frame,mem:read_u16(p2+0x7c),mem:read_u8(p2+0xf9),mem:read_u16(p2+0xe6))) end
 if frame==2935 or frame==2980 then local ptr=mem:read_u32(p2+0x6c) print(string.format('ANIM ptr=%x end=%x data=%08x next=%08x flags=%x',ptr,mem:read_u32(p2+0x70),mem:read_u32(ptr),mem:read_u32(ptr+4),mem:read_u8(p2+0x88))) end
 if frame==2812 then mem:write_u16(p2+0xe6,0x318) end
 if frame>=2800 and frame%5==0 and frame<3200 then m.screens[':screen']:snapshot('C:/TEMP2/SS2/reports/finish-'..frame..'.png') end
end)



