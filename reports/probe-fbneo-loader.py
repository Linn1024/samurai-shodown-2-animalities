import runpy,subprocess,time,ctypes
from pathlib import Path
n=runpy.run_path('fbneo-ultimate.py')
u=n['u']
startup=subprocess.STARTUPINFO()
startup.dwFlags=subprocess.STARTF_USESHOWWINDOW
startup.wShowWindow=0
if not n['find_main']():
    p=subprocess.Popen([str(Path('tools/FBNeo/fbneo64.exe').resolve()),'samsh2sp','-w'],cwd='tools/FBNeo',startupinfo=startup)
    Path('reports/fbneo-probe-pid.txt').write_text(str(p.pid))
    time.sleep(2)
main=n['find_main']()
print('MAIN',main,flush=True)
u.PostMessageW(main,0x111,11812,0)
time.sleep(1)
for h in n['windows']():
    if n['title'](h)=='Lua Script':
        print('DIALOG',h,flush=True)
        @n['CALLBACK']
        def child(handle,_):
            name=ctypes.create_unicode_buffer(256)
            u.GetClassNameW(handle,name,len(name))
            print(u.GetDlgCtrlID(handle),name.value,ascii(n['title'](handle)),flush=True)
            return True
        u.EnumChildWindows(h,child,0)
        edit=u.GetDlgItem(h,20368)
        print('SETRESULT',u.SetWindowTextW(edit,str(Path('ultimate.lua').resolve())),ctypes.get_last_error(),flush=True)
        print('READBACK',ascii(n['title'](edit)),flush=True)
        u.GetDlgItemTextA.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_char_p,ctypes.c_int]
        buf=ctypes.create_string_buffer(1024)
        print('ANSIRESULT',u.GetDlgItemTextA(h,20368,buf,1024),repr(buf.value),flush=True)
