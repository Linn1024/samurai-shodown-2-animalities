local function run_fixture()
local m=manager.machine
local mem=m.devices[':maincpu'].spaces.program
memory={readbyte=function(a) return mem:read_u8(a) end,readdword=function(a) return mem:read_u32(a) end,writebyte=function(a,v) mem:write_u8(a,v) end}
local ok,factory=pcall(dofile,'animality.lua')
if not ok then print('ANIMALITY ERROR '..tostring(factory));return end
local gui={}
local ok,A=pcall(factory,memory,gui)
if not ok then print('ANIMALITY FACTORY ERROR '..tostring(A));return end
local log=assert(io.open('reports/animality-timeline.tsv','w'))
log:write('frame\tpose\tx\ty\tevents\tstate\n')
gui.gdoverlay=function(x,y,data) local f=assert(io.open('reports/animality-overlay.gd','wb'));f:write(data);f:close() end
local fields={}
for _,port in pairs(m.ioport.ports) do for name,f in pairs(port.fields) do fields[name]=f;f:set_input_seq('standard',m.input:seq_from_tokens('')) end end
local frame=0
local taps={}
local cfg=io.open('reports/animality-test-config.txt','r')
local mode=cfg and cfg:read('*a') or ''
if cfg then cfg:close() end
local function press(name,on) if on then fields[name]:set_value(1) else fields[name]:clear_value() end end
emu.register_frame_done(function()
 frame=frame+1
 if mode:find('normal') and A.events==0 then
  local victim=mem:read_u32(0x100a4a)
  if victim>=0x102000 and victim<0x10fd00 and mem:read_u16(victim+0xba)==0 then mem:write_u16(victim+0xe6,0x316) end
 end
 A.after()
 press('Coin 1',frame>1000 and frame<2200 and frame%180<20)
 press('1 Player Start',frame>1100 and frame<2200 and frame%180>=50 and frame%180<60)
 if frame<=2200 then press('P1 Button 1',frame>1200 and frame<2200 and frame%180>=100 and frame%180<110) end
if frame>=1700 and frame<2100 then mem:write_u8(0x100d0b,SS2_TEST_ID or 5) end
 local p1,p2=mem:read_u32(0x100a46),mem:read_u32(0x100a4a)
 if frame>=2200 and frame<2750 and p2>=0x102000 and p2<0x10fe00 then mem:write_u16(p2+0xe6,0x2e) end
 if frame>=2750 and frame<2800 then
  mem:write_u8(p2+0xbb,1)
  mem:write_u16(p1+0x4e,240);mem:write_u16(p2+0x4e,295)
  mem:write_u16(p1+0xe6,0);mem:write_u16(p2+0xe6,0)
  if frame==2750 then taps[#taps+1]=mem:install_write_tap(p2+0xe8,p2+0xeb,'idle-opponent',function(a,d,mask) return 0 end) end
  if mode:find('left') then mem:write_u16(p1+0x4e,350);mem:write_u16(p2+0x4e,295);mem:write_u8(p1+0x7f,1);mem:write_u8(p2+0x7f,0) end
  if mode:find('other') then mem:write_u8(p1+0xf6,1);mem:write_u16(p1+0x64,1) end
 end
 if frame>2200 then press('P1 Button 1',frame>=2800 and frame<2804);press('P1 Button 2',frame>=2800 and frame<2804) end
 -- Fixture picks the native fountain fatality instead of the game's random death variant.
 if not mode:find('normal') and ((mode:find('p2') and frame==2812)
  or (not mode:find('p2') and frame>=2812 and frame<3000 and (mem:read_u16(p2+0xba)==0 or (SS2_TEST_FORCE_FINISH and frame==2812)) and A.events==0)) then
  if mode:find('p2') then
   mem:write_u8(p1+0xf6,0);mem:write_u16(p1+0x64,0)
   mem:write_u8(p2+0xf6,SS2_TEST_ID or 5);mem:write_u16(p2+0x64,SS2_TEST_ID or 5)
   for bank=0,7 do
    local pointer=mem:read_u32(0x10ec40+bank*4)
    mem:write_u32(0x10ec60+bank*4,pointer)
    for color=0,15 do mem:write_u16(0x400300+bank*32+color*2,mem:read_u16(pointer+color*2)) end
   end
   mem:write_u16(p2+0xba,128);mem:write_u16(p2+0xe6,0)
   mem:write_u16(p1+0xba,0);mem:write_u16(p1+0xe6,0x318);mem:write_u8(p1+0x107,1)
  else mem:write_u16(p2+0xba,0);mem:write_u16(p2+0xe6,0x318) end
 end
 if frame==2900 and mode:find('cancel') then A.enabled=false;A.cancel(true) end
 if frame>=2800 and frame<=3250 then
  local s=A.status()
  log:write(string.format('%d\t%d\t%d\t%d\t%d\t%x\n',frame,s and s.frame or -1,mem:read_u16(p1+0x5c),mem:read_u16(p1+0x5e),A.events,mem:read_u16(p1+0xe6)))
  if frame%10==0 and SS2_TEST_CAPTURE~=false then
   if not s then
    os.remove('reports/animality-game-'..frame..'.gd');os.remove('reports/animality-game-'..frame..'.xy')
   end
   m.screens[':screen']:snapshot('C:/TEMP2/SS2/reports/animality-game-'..frame..'.png')
   if s then
    gui.gdoverlay=function(x,y,data)
     local f=assert(io.open('reports/animality-game-'..frame..'.gd','wb'));f:write(data);f:close()
     local f=assert(io.open('reports/animality-game-'..frame..'.xy','w'));f:write(x..' '..y);f:close()
    end
    A.draw()
   end
  end
 end
 if frame==3251 then log:close();print('ANIMALITY TEST events='..A.events..' active='..tostring(A.status()~=nil)..' handler='..string.format('%x',mem:read_u32(p1))) end
 if frame==4200 then
  print(string.format('CONTINUE p1=%x hp=%d state=%x p2hp=%d',p1,mem:read_u16(p1+0xba),mem:read_u16(p1+0xe6),mem:read_u16(p2+0xba)))
  m.screens[':screen']:snapshot('C:/TEMP2/SS2/reports/animality-continue.png')
 end
 A.before()
end)
end
local started=false
emu.register_frame_done(function()
 if not started and manager.machine.devices[':maincpu'].spaces.program then
  started=true;run_fixture()
 end
end)
