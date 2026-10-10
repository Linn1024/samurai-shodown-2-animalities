exec(open('reports/check-loader.py').read().split("ctypes.set_last_error(0)")[0])
u.SendMessageA.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]; u.SendMessageA.restype=w.LPARAM
for h in n['windows']():
    if not owned(h): continue
    if n['title'](h)=='Lua load error': u.PostMessageW(h,0x111,2,0)
time.sleep(.3)
dlg=next(h for h in n['windows']() if owned(h) and u.GetDlgItem(h,20368))
edit=u.GetDlgItem(dlg,20368)
for func in [u.SendMessageA,u.SendMessageW]:
    b=ctypes.create_string_buffer(1024); ctypes.set_last_error(0)
    print(func,func(edit,0xd,512,ctypes.addressof(b)),ctypes.get_last_error(),repr(b.raw[:60]))
print('enabled',u.IsWindowEnabled(edit))
