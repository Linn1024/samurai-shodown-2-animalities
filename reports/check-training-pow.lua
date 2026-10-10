local ram,keys={},{}
local function rb(a) return ram[a] or 0 end
local function wb(a,v) ram[a]=v end
local function ww(a,v) wb(a,math.floor(v/256)%256);wb(a+1,v%256) end
local function rd(a) return rb(a)*16777216+rb(a+1)*65536+rb(a+2)*256+rb(a+3) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local a,b=0x104000,0x106000
local checkpoint
local states={create=function() return {} end,save=function(s) for address,value in pairs(ram) do s[address]=value end;checkpoint=s end}
local T
states.load=function(s) ram={};for address,value in pairs(s) do ram[address]=value end;T.on_load() end
local A={definitions={[0]={name='tiger'}},status=function() return nil end,cancel=function() end}
T=assert(loadfile('training.lua'))()({animality=A,cancel=function() end},{readbyte=rb,readdword=rd,writebyte=wb},{set=function() end},{get=function() return keys end},states,{})
assert(not T.pow(1,1) and next(ram)==nil)
T.toggle();assert(not T.pow(1,1) and next(ram)==nil)
wd(0x100a46,a);wd(0x100a4a,b);wd(a,0x25314);wd(b,0x25314);ww(a+0xba,128);ww(b+0xba,128)
for value=1,31 do assert(T.pow(1,1) and rb(a+0xf0)==value) end
assert(rb(b+0xf0)==0,'P2 untouched')
assert(T.pow(1,1) and rb(a+0xf0)==31 and rb(a+0x114)==1,'full POW must enter through native meter update')
wb(a+0xf0,32);wb(a+0x114,0);ww(a+0xb8,300);wb(a+0x11c,5)
assert(T.pow(1,-1) and rb(a+0xf0)==31 and rb(a+0x11c)==4 and rb(a+0xb8)==0 and rb(a+0xb9)==0)
assert(T.pow(1,-100) and rb(a+0xf0)==0)
keys={rightbracket=true};T.before();assert(rb(a+0xf0)==1)
for i=1,23 do T.before();T.after() end
assert(rb(a+0xf0)==1,'initial hold delay')
T.before();assert(rb(a+0xf0)==2,'slow hold repeat')
keys={['numpad+']=true};T.before();assert(rb(b+0xf0)==1)
keys={};for i=1,4 do T.before();T.after() end
assert(T.restore() and rb(b+0xf0)==1 and rb(a+0xf0)==2,'reset keeps settled POW settings')
T.stop();assert(not T.pow(1,1))
print('PASS POW controls: 0..32, both slots, native max entry, rage exit, clamping, slow key repeat, checkpoints and OFF/menu guards.')
