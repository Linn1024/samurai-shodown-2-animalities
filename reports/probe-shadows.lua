local m=manager.machine
for tag,dev in pairs(m.devices) do
    if tag:find('sprite') then
        print('DEVICE',tag)
        for name,index in pairs(dev.items) do print('ITEM',name,index) end
    end
end
for name,share in pairs(m.memory.shares) do print('SHARE',name,share.size) end
