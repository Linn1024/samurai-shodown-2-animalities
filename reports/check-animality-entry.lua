assert(loadfile('ultimate.lua'))
local chunk=assert(loadfile('animality.lua'))
assert(type(chunk(true))=='function','module entry must return factory')
local original_dofile=dofile
local original_memory,original_gui,original_emu=memory,gui,emu
local loaded
memory={};gui={};emu={registerbefore=function() end}
dofile=function(path) loaded=path;return 'entry-ok' end
local ok,result=pcall(chunk)
dofile=original_dofile
memory,gui,emu=original_memory,original_gui,original_emu
assert(ok,result)
assert(result=='entry-ok' and loaded=='ultimate.lua','direct entry must launch ultimate.lua')
print('PASS: module returns factory; direct Lua entry launches ultimate.lua; both files compile.')
