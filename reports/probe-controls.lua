local m=manager.machine
for tag,port in pairs(m.ioport.ports) do
  for name,field in pairs(port.fields) do
    print(string.format('INPUT %s %s %x',tag,name,field.mask))
  end
end
local frames=0
local fields={}
for _,port in pairs(m.ioport.ports) do
  for name,field in pairs(port.fields) do fields[name]=field end
end
emu.register_frame_done(function()
  frames=frames+1
  local function press(name,yes)
    if fields[name] then if yes then fields[name]:set_value(1) else fields[name]:clear_value() end end
  end
  press('Coin 1',frames>1000 and frames%180<20)
  press('1 Player Start',frames>1100 and frames%180>=50 and frames%180<60)
  press('P1 Button 1',frames>1200 and frames%180>=100 and frames%180<110)
  local mem=m.devices[':maincpu'].spaces['program']
  if frames%300==0 then
    local base=mem:read_u32(0x100a46)
    print(string.format('FRAME %d PTR %x char %x facing %x state %x',frames,base,mem:read_u8(base+0xf6),mem:read_u8(base+0x7f),mem:read_u16(base+0xe6)))
  end
  if frames==2500 or frames==3500 or frames==5000 or frames==6500 then m.screens[':screen']:snapshot('C:/TEMP2/SS2/reports/probe-'..frames..'.png') end
end)
