local ram,keys,hooks,writes={}, {}, {},0
local function rb(a) return ram[a] or 0 end
local function wb(a,v) ram[a]=v;writes=writes+1 end
local function ww(a,v) wb(a,math.floor(v/256)%256);wb(a+1,v%256) end
local function rd(a) return rb(a)*16777216+rb(a+1)*65536+rb(a+2)*256+rb(a+3) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local active=nil
local A={definitions={[0]={name='test tiger'}}}
A.status=function() return active end
A.cancel=function() active=nil end
local api={animality=A,cancel=function() end}
local T,saves,loads=nil,0,0
local states={create=function() return {} end}
states.save=function(s) saves=saves+1;for a,v in pairs(ram) do s[a]=v end end
states.load=function(s)
 loads=loads+1;ram={};for a,v in pairs(s) do ram[a]=v end
 A.cancel();T.on_load()
end
T=assert(loadfile('training.lua'))() (api,{readbyte=rb,readdword=rd,writebyte=wb,
 registerwrite=function(a,n,f) hooks[a]=f end},{set=function() end},{get=function() return keys end},states,{})
T.before();assert(writes==0 and not T.enabled)
keys.T=true;T.before();assert(T.enabled and writes==0)
for i=1,5 do T.before() end;assert(T.enabled,'held T must not repeat')
assert(not T.preview(1) and saves==0 and writes==0,'menus/BIOS must not be modified')
keys={};T.before()
local a,b=0x104000,0x106000
wd(0x100a46,a);wd(0x100a4a,b);wd(a,0x25314);wd(b,0x25314)
ww(a+0xba,100);ww(b+0xba,100);wb(a+0xf6,0);wb(b+0xf6,4)
T.before();assert(saves==1 and rb(a+0xbb)==128 and rb(b+0xbb)==128)
local count=writes
assert(not T.preview(2) and saves==1 and writes==count,'unsupported character must not kill anyone')
local values={['P1 Button A']=true};T.filter_inputs(values)
assert(values['P1 Button A'] and values['P2 Button A']==false,'F macro must preserve passive P2')
assert(T.preview(1));assert(T.previewing and rb(b+0xbb)==0 and rb(b+0xe7)==0x18)
assert(T.restore());assert(not T.previewing and rb(b+0xbb)==128 and loads==1)
assert(T.restore() and loads==2,'checkpoint survives internal loads')
T.on_load();assert(not T.restore(),'external load invalidates old checkpoint')
T.stop();assert(next(hooks)==nil,'all dummy input hooks removed')
count=writes;keys={};T.before();assert(writes==count,'training OFF leaves game RAM untouched')
print('PASS training: disabled/menu guards, hotkey debounce, unsupported character, input merge, checkpoint reuse, external load and hook cleanup.')
