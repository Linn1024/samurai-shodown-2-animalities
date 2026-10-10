local file=assert(io.open('C:/TEMP2/SS2/reports/fbneo-smoke-ok.txt','w'))
file:write('Lua started successfully\n'); file:close()
while true do emu.frameadvance() end
