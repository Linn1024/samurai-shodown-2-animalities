-- Samurai Shodown II Special 2017 v1.1: P1 weapon-breaking special on F.
-- F macro leaves gameplay/POW rules unchanged. Shadow fix edits display flags only.
-- FBNeo translucency: support/blend/samsh2sp.bld (reload the game after installing).
-- Supports HBMAME and Windows FinalBurn Neo. Two frames per motion step.
-- Character IDs/facing offsets: FBNeo cheat database and peon2 training mode.
local profiles = {
    [0x00] = {"Haohmaru",   "632146", "A"},
    [0x01] = {"Nakoruru",   "641236", "A"},
    [0x02] = {"Hanzo",      "632146", "D"},
    [0x03] = {"Galford",    "632146", "D"},
    [0x04] = {"Wan-Fu",     "641236", "B"},
    [0x05] = {"Ukyo",       "641236", "AB"},
    [0x06] = {"Kyoshiro",   "641236", "C"},
    [0x07] = {"Gen-An",     "632146", "AB"},
    [0x08] = {"Earthquake", "641236", "CD"},
    [0x09] = {"Jubei",      "632146", "C"},
    [0x0b] = {"Charlotte",  "632146", "B"},
    [0x0c] = {"Genjuro",    "632146", "A"},
    [0x0d] = {"Cham Cham",  "641236", "A"},
    [0x0e] = {"Sieger",     "632146", "CD"},
    [0x0f] = {"Nicotine",   "641236", "D"},
    [0x10] = {"Mizuki",     "632146", "A"},
    [0x11] = {"Kuroko",     "632146", "AB"},
}
local api = { profiles = profiles }
local STEADY_SHADOWS = true -- Set false, then reload the script for original blinking.
local is_mame = manager and manager.machine
local rb, rd, wb, key_pressed, apply, release, register, message, acquire
local controlled = {"Up", "Down", "Left", "Right", "A", "B", "C", "D"}
if is_mame then
    local m = manager.machine
    local mem = m.devices[":maincpu"].spaces["program"]
    rb = function(a) return mem:read_u8(a) end
    rd = function(a) return mem:read_u32(a) end
    wb = function(a,v) mem:write_u8(a,v) end
    local code = m.input:code_from_token("KEYCODE_F")
    key_pressed = function() return m.input:code_pressed(code) end
    local port = assert(m.ioport.ports[":edge:joy:JOY1"], "P1 joystick port missing")
    local fields = {}
    local saved = {}
    local empty = m.input:seq_from_tokens("")
    local masks = {Up=1,Down=2,Left=4,Right=8,A=16,B=32,C=64,D=128}
    for name,mask in pairs(masks) do fields[name] = assert(port:field(mask)) end
    acquire = function()
        for name,field in pairs(fields) do
            saved[name] = field:input_seq("standard")
            field:set_input_seq("standard",empty)
        end
    end
    apply = function(keys)
        for _,name in ipairs(controlled) do fields[name]:set_value(keys[name] and 1 or 0) end
    end
    release = function()
        for name,field in pairs(fields) do
            field:clear_value()
            if saved[name] then field:set_input_seq("standard",saved[name]) end
        end
        saved = {}
    end
    register = emu.register_frame_done
    message = function(text) m:popmessage(text) end
else
    assert(memory and joypad and input and emu, "Run this script inside HBMAME or FinalBurn Neo")
    assert(emu.romname() == "samsh2sp" or emu.romname() == "samsho2sp", "Load the Special 2017 hack first")
    rb, rd = memory.readbyte, memory.readdword
    wb = memory.writebyte
    key_pressed = function() return input.get().F == true end
    apply = function(keys)
        local values = {}
        for _,name in ipairs(controlled) do
            local label = (#name == 1) and ("Button " .. name) or name
            values["P1 " .. label] = keys[name] or false
        end
        joypad.set(values)
    end
    release = function() end -- FBNeo overrides last one frame only.
    acquire = function() end
    register = emu.registerbefore
    message = function(text) print(text) end
end

local sequence, frame, previous, actor = nil, 0, false, nil
local shadow_flags = {}
local function is_shadow(object)
    local handler=rd(object)
    if handler==0x44790 or handler==0x124d4 then return true end
    -- Shadow animation family: includes small airborne and large variants.
    return rb(object+0x64)==0 and rb(object+0x65)==0x13
        and rb(object+0x66)==0 and rb(object+0x67)>=0xe8
end
function api.shadows()
    if not STEADY_SHADOWS then return end
    -- Walk the game's live object list, not character-specific RAM addresses.
    -- Match both shadow handlers and their complete animation family.
    local object = 0x102000
    local visited = {}
    for count=1,256 do
        if object < 0x102000 or object > 0x10fd00 or object%2~=0 or visited[object] then break end
        visited[object] = true
        if is_shadow(object) then
            if not shadow_flags[object] then shadow_flags[object] = rb(object+0x22) end
            if rb(object+0x22)~=0 then wb(object+0x22,0) end
            local flags=rb(object+0x88)
            if flags>=128 then wb(object+0x88,flags-128) end
        end
        if rb(object+0x10)==255 and rb(object+0x11)==255 then break end
        object = 0x100000 + rb(object+0x0e)*256 + rb(object+0x0f)
    end
end
function api.restore_shadows()
    for object,blink in pairs(shadow_flags) do
        if is_shadow(object) then wb(object+0x22,blink) end
    end
    shadow_flags = {}
end
function api.player()
    local base = rd(0x100a46)
    if base < 0x100000 or base > 0x10fe00 or base % 2 ~= 0 then return nil end
    local id = rb(base + 0xf6)
    if not profiles[id] then return nil end
    return base, id, rb(base + 0x7f) == 1
end
function api.trigger()
    if sequence then return false end
    local base,id,left = api.player()
    if not base then return false end
    actor = base
    acquire()
    local profile = profiles[id]
    sequence = {}
    -- Clear held controls before entering a fresh motion.
    sequence[1],sequence[2] = {},{}
    for pos=1,#profile[2] do
        local direction = profile[2]:sub(pos,pos)
        local keys = {}
        if direction == "1" or direction == "2" or direction == "3" then keys.Down=true end
        if direction == "1" or direction == "4" then keys[left and "Right" or "Left"]=true end
        if direction == "3" or direction == "6" then keys[left and "Left" or "Right"]=true end
        sequence[#sequence+1],sequence[#sequence+2] = keys, keys
    end
    -- The ROM parser consumes direction and button edges in separate steps.
    -- Press attacks AFTER the last direction has been recognized.
    local finish = {}
    for key,value in pairs(sequence[#sequence]) do finish[key]=value end
    for button in profile[3]:gmatch(".") do finish[button]=true end
    sequence[#sequence+1],sequence[#sequence+2] = finish,finish
    sequence[#sequence+1] = {}
    frame = 0
    return true
end
function api.cancel()
    sequence,actor = nil,nil
    release()
end
function api.tick()
    api.shadows()
    local pressed = key_pressed()
    if pressed and not previous then api.trigger() end
    previous = pressed
    if not sequence then return end
    local base = api.player()
    if base ~= actor then api.cancel(); return end
    frame = frame+1
    if frame > #sequence then api.cancel() else apply(sequence[frame]) end
end
register(api.tick)
if is_mame then
    -- Keep subscriptions alive for the lifetime of the script.
    api.stop_subscription = emu.add_machine_stop_notifier(function() api.cancel(); api.restore_shadows() end)
    api.reset_subscription = emu.add_machine_reset_notifier(api.cancel)
    api.load_subscription = emu.add_machine_post_load_notifier(api.cancel)
else
    emu.registerexit(function() api.cancel(); api.restore_shadows() end)
end
message("Ultimate button ready: F (P1). Normal POW and move rules apply.")
if STEADY_SHADOWS then message("Shadows v2: steady ground/airborne shadows, all sizes. FBNeo blend table: 50%.") end
if not is_mame then
    while true do emu.frameadvance() end
end
return api
