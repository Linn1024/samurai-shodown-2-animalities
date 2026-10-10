import ctypes,runpy,time,sys
from ctypes import wintypes as w
from pathlib import Path
n=runpy.run_path('reports/inspect-live-fbneo.py');u=n['u'];CB=n['CB']
u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)]
pid=int(Path('reports/shadow-test-pid.txt').read_text())
@CB
def visit(h,_):
    p=w.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(p))
    if p.value==pid:
        print('TEST WINDOW',h,ascii(n['title'](h)))
        if n['title'](h).startswith('FinalBurn') and len(sys.argv)>1:
            ctypes.set_last_error(0)
            print('COMMAND',u.PostMessageW(h,0x111,int(sys.argv[1]),0),ctypes.get_last_error())
    return True
u.EnumWindows(visit,0)
