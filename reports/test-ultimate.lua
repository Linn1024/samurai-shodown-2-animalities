local ok,api=pcall(dofile,'ultimate.lua')
if not ok then print('ULTIMATE ERROR: '..tostring(api)); return end
local m=manager.machine
local mem=m.devices[':maincpu'].spaces['program']
local fields={}
for _,port in pairs(m.ioport.ports) do for name,field in pairs(port.fields) do fields[name]=field end end
local frame=0
local config=assert(io.open('reports/test-target.txt','r'))
local settings=config:read('*a')
local target=tonumber(settings:match('^%d+'))
local test_left=settings:find('left')~=nil
local test_no_pow=settings:find('nopow')~=nil
config:close()
local states={}
local function press(name,value)
    if value then fields[name]:set_value(1) else fields[name]:clear_value() end
end
emu.register_frame_done(function()
    frame=frame+1
    press('Coin 1',frame>1000 and frame<2200 and frame%180<20)
    press('1 Player Start',frame>1100 and frame<2200 and frame%180>=50 and frame%180<60)
    if frame<=2200 then press('P1 Button 1',frame>1200 and frame<2200 and frame%180>=100 and frame%180<110) end
    if frame>=1700 and frame<2100 then mem:write_u8(0x100d0b,target) end
    local base,id,left=api.player()
    if frame==2500 and base then
        print(string.format('READY base=%x id=%x facing=%s health=%x state=%x',base,id,tostring(left),mem:read_u8(base+0xbb),mem:read_u16(base+0xe6)))
        -- Test fixture: cross the meter threshold through the game's own
        -- update path so its rage timer/flags are also initialized.
        mem:write_u8(base+0xf0,test_no_pow and 0 or 0x1f)
        mem:write_u8(base+0x114,test_no_pow and 0 or 1)
        if target==16 then mem:write_u8(0x100b00,mem:read_u8(0x100b00)|2) end
    end
    local p2=mem:read_u32(0x100a4a)
    if frame==2600 and test_left and base then
        local x1,x2=mem:read_u16(base+0x4e),mem:read_u16(p2+0x4e)
        mem:write_u16(base+0x4e,x2)
        mem:write_u16(p2+0x4e,x1)
    end
    if frame>=2200 and p2>=0x100000 and p2<0x10fe00 then mem:write_u16(p2+0xe6,0x2e) end
    if frame==2800 then
        print('FACING',left,'POW',base and mem:read_u8(base+0xf0))
        print('TRIGGER', api.trigger())
    end
    if frame>=2800 and frame<=2880 and base then
        local state=mem:read_u16(base+0xe6)
        states[state]=true
    end
    if frame==2835 then m.screens[':screen']:snapshot(string.format('C:/TEMP2/SS2/reports/ultimate-%02x.png',target)) end
    if frame==2881 then
        local result={}
        for state in pairs(states) do result[#result+1]=string.format('%x',state) end
        print(string.format('RESULT target=%x actual=%x states=%s',target,id,table.concat(result,',')))
    end
end)
