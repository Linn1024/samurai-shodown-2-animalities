local f=assert(io.open('reports/fbneo-state-game-ram.bin','rb'))
local data=f:read('*a');f:close()
local ram={}
for i=1,#data do ram[0x100000+i-1]=data:byte(i) end
local function rb(a) return ram[a] or 0 end
local function wb(a,v) ram[a]=v end
local function ww(a,v) wb(a,math.floor(v/256)%256);wb(a+1,v%256) end
local function rd(a) return rb(a)*16777216+rb(a+1)*65536+rb(a+2)*256+rb(a+3) end
local function wd(a,v) ww(a,math.floor(v/65536));ww(a+2,v%65536) end
local bitmap=false
local gui={clearuncommitted=function() bitmap=false end,gdoverlay=function() bitmap=true end}
local factory=assert(loadfile('animality.lua'))(true)
local A=factory({readbyte=rb,readdword=rd,writebyte=wb},gui)
local actor,victim=rd(0x100a46),rd(0x100a4a)
assert(A.definitions[rb(actor+0xf6)],'saved player must have a supported animality')
wd(actor,0x25314);wd(victim,0x25314)
ww(actor+0xba,37);ww(victim+0xba,0);ww(victim+0xe6,0x318)
A.after();assert(A.status(),'animality should begin')
A.draw();assert(bitmap,'active animality must draw')
wd(0x102000,0x4456a);wd(0x102000+0xcc,victim)
for i=1,101 do A.before();A.after();A.draw() end
assert(not A.status() and not bitmap,'completion must clear last sprite')
bitmap=true;A.cancel(false,'save-state load test')
assert(not bitmap,'save-state cancellation must clear overlay')
bitmap=true;A.draw();assert(not bitmap,'inactive GUI callback must clear overlay')
assert(rd(actor)==0x25314,'native handler must be restored')
print('PASS saved-slot RAM: start, draw, finish, load cancellation and inactive redraw clear overlay; handler restored.')
