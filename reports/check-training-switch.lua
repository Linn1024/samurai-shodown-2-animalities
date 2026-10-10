local ram,keys,hooks={}, {}, {}
local function rb(a) return ram[a] or 0 end
local function wb(a,v) ram[a]=v end
local function ww(a,v) wb(a,math.floor(v/256)%256);wb(a+1,v%256) end
local function rd(a) return rb(a)*16777216+rb(a+1)*65536+rb(a+2)*256+rb(a+3) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local A={definitions={[0]={name='Tiger',palette=0x214a00},[1]={name='Hawk',palette=0x214400}}}
local active=nil
A.status=function() return active end;A.cancel=function() active=nil end
local T,loads=nil,0
local states={create=function() return {} end}
states.save=function(s) for a,v in pairs(ram) do s[a]=v end end
states.load=function(s) loads=loads+1;ram={};for a,v in pairs(s) do ram[a]=v end;A.cancel();T.on_load() end
T=assert(loadfile('training.lua'))()({animality=A,cancel=function() end},
 {readbyte=rb,readdword=rd,writebyte=wb,registerwrite=function(a,n,f) hooks[a]=f end},
 {set=function() end},{get=function() return keys end},states,{})
assert(not T.change(1,1) and next(ram)==nil,'OFF must not touch RAM')
assert(not T.palette(1) and next(ram)==nil,'palette OFF must not touch RAM')
T.toggle();assert(not T.change(1,1) and next(ram)==nil,'menus must not touch RAM')
local a,b=0x104000,0x106000
wd(0x100a46,a);wd(0x100a4a,b);wd(a,0x25314);wd(b,0x25314)
ww(a+0xba,128);ww(b+0xba,128);wb(a+0xf6,0);wb(b+0xf6,1)
-- Two owned nodes, plus a different player's companion, in the real list layout.
ww(0x10200e,0x3000);ww(0x10300e,0x3200);ww(0x10320e,0x3400)
ww(0x10340e,0x4000);ww(a+0xe,0x6000);ww(b+0xe,0x2000)
wd(0x103000,0x1234);wd(0x103200,0x1234);wd(0x103400,0x1234)
wd(0x1030cc,a);wd(0x1032cc,0x103000);wd(0x1034cc,b);wd(0x100a4e,0x103000)
T.before();keys.K=true;T.before()
assert(rb(a+0xf6)==1 and rb(a+0x65)==1 and rd(a)==0x252ec)
assert(rd(0x103000)==0x3052 and rd(0x103200)==0x3052 and rd(0x103400)==0x1234,'retire only selected fighter descendants')
assert(rd(0x100a4e)==0 and rd(0x10ec40)==0x214400)
wd(a,0x25314)
for i=1,10 do T.before();T.after() end
assert(rb(a+0xf6)==1,'held K must not repeat')
assert(T.restore() and rb(a+0xf6)==1,'new checkpoint must contain changed fighter')
keys={};T.before();keys.J=true;T.before();assert(rb(a+0xf6)==0)
wd(a,0x25314);for i=1,4 do T.before();T.after() end
keys={};T.before();keys.M=true;T.before();assert(rb(b+0xf6)==0,'P2 next wraps')
wd(b,0x25314);for i=1,4 do T.before();T.after() end
keys={};T.before();keys.N=true;T.before();assert(rb(b+0xf6)==1,'P2 previous wraps')
wd(b,0x25314);for i=1,4 do T.before();T.after() end
keys={};T.before();assert(T.preview(1));active={victim=b}
local oldloads=loads
assert(T.change(1,1) and loads==oldloads+1 and not T.previewing and not active,'switch during preview restores and cancels first')
wd(a,0x25314);for i=1,4 do T.before();T.after() end
assert(T.restore() and rb(a+0xf6)==1,'R must keep new character after interrupted preview')
-- Costume follows the player slot through forward/backward changes and reset.
wd(0x10ec40,A.definitions[rb(a+0xf6)].palette+256)
assert(T.change(1,1));assert(rd(0x10ec40)==A.definitions[rb(a+0xf6)].palette+256)
wd(a,0x25314);for i=1,4 do T.before();T.after() end
assert(T.restore() and rd(0x10ec40)==A.definitions[rb(a+0xf6)].palette+256)
wd(0x10ec60,A.definitions[rb(b+0xf6)].palette+256)
assert(T.change(2,-1));assert(rd(0x10ec60)==A.definitions[rb(b+0xf6)].palette+256)
assert(rd(0x10ec40)==A.definitions[rb(a+0xf6)].palette+256,'other slot costume untouched')
wd(b,0x25314);for i=1,4 do T.before();T.after() end
local initial_a=rd(0x10ec40);local initial_b=rd(0x10ec60)
keys={O=true};T.before();assert(rd(0x10ec40)==A.definitions[rb(a+0xf6)].palette)
for i=1,4 do T.before() end
assert(rd(0x10ec40)~=initial_a,'held O must toggle only once')
assert(rd(0x10ec60)==initial_b,'O must not change P2')
assert(T.restore() and rd(0x10ec40)==A.definitions[rb(a+0xf6)].palette,'reset keeps toggled palette')
keys={};T.before();keys={P=true};T.before()
assert(rd(0x10ec60)==A.definitions[rb(b+0xf6)].palette)
assert(T.preview(1));active={victim=b};local prior_loads=loads
assert(T.palette(1) and loads==prior_loads+1 and not active and not T.previewing,'palette change cancels preview safely')
assert(rd(0x10ec40)==A.definitions[rb(a+0xf6)].palette+256)
T.stop();assert(next(hooks)==nil)
print('PASS character switching: menu/OFF guards, J/K and N/M, held-key debounce, wrap, native initialization, palette, owned-helper retirement, preview interruption and checkpoint update.')
