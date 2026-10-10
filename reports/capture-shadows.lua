local api=dofile('ultimate.lua')
local m=manager.machine
local mem=m.devices[':maincpu'].spaces.program
local vram=emu.item(m.devices[':spritegen'].items['0/m_videoram.get()'])
local fields={}
for _,port in pairs(m.ioport.ports) do for name,field in pairs(port.fields) do fields[name]=field end end
local frame=0
print('SHADOW SCRIPT START')
local tap=mem:install_read_tap(0xe3800,0xe3981,'shadowtrace',function(address,data,mask)
    if frame>=2599 and frame<=2601 then
        print(string.format('SHADOWREAD frame=%d address=%x pc=%x data=%x',frame,address,m.devices[':maincpu'].state.PC.value,data))
        if address==0xe38ea or address==0xe3896 then
            local cpu=m.devices[':maincpu']
            print('OBJECT',string.format('%x',cpu.state.A6.value))
            print('LIVEFRAME',string.format('%x',mem:read_u16(cpu.state.A6.value+0x18)))
            for offset=0,28,4 do print('STACK',offset,string.format('%x',mem:read_u32(cpu.state.SP.value+offset))) end
        end
    end
end)
print('TAP READY')
local writes=mem:install_write_tap(0x101140,0x1011bf,'shadowcreate',function(address,data,mask)
    if frame==2600 and (address==0x101158 or address==0x101198) then
        print(string.format('CREATED address=%x data=%x pc=%x',address,data,m.devices[':maincpu'].state.PC.value))
        local sp=m.devices[':maincpu'].state.SP.value
        for offset=0,16,4 do print('CALLSTACK',offset,string.format('%x',mem:read_u32(sp+offset))) end
    end
end)
local function press(name,value)
    if value then fields[name]:set_value(1) else fields[name]:clear_value() end
end
emu.register_frame_done(function()
    frame=frame+1
    if frame==2606 then tap:remove(); writes:remove() end
    press('Coin 1',frame>1000 and frame<2200 and frame%180<20)
    press('1 Player Start',frame>1100 and frame<2200 and frame%180>=50 and frame%180<60)
    press('P1 Up',frame>=2580 and frame<=2606)
    if frame<=2200 then press('P1 Button 1',frame>1200 and frame<2200 and frame%180>=100 and frame%180<110) end
    if frame>=1700 and frame<2100 then mem:write_u8(0x100d0b,0) end
    local p2=mem:read_u32(0x100a4a)
    if frame>=2200 and p2>=0x100000 and p2<0x10fe00 then mem:write_u16(p2+0xe6,0x2e) end
    if frame>=2600 and frame<2606 then
        local f=assert(io.open(string.format('reports/shadow-vram-%d.bin',frame),'wb'))
        f:write(vram:read_block(0,vram.size*vram.count)); f:close()
        local f=assert(io.open(string.format('reports/shadow-ram-%d.bin',frame),'wb'))
        for a=0x100000,0x10ffff do f:write(string.char(mem:read_u8(a))) end
        f:close()
        m.screens[':screen']:snapshot(string.format('C:/TEMP2/SS2/reports/shadow-%d.png',frame))
        print('CAPTURE',frame)
    end
end)

