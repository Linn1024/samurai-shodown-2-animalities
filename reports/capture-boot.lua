local frames = 0
emu.register_frame_done(function()
    frames = frames + 1
    if frames == 2400 then
        manager.machine.screens[":screen"]:snapshot("C:/TEMP2/SS2/reports/boot.png")
    end
end)
