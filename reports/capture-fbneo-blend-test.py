import ctypes,time
from ctypes import wintypes as w
from pathlib import Path
u=ctypes.WinDLL('user32',use_last_error=True)
CB=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int]
u.GetWindowThreadProcessId.argtypes=[w.HWND,ctypes.POINTER(w.DWORD)]
u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
pid=int(Path('reports/shadow-test-pid.txt').read_text())
main=None
@CB
def visit(h,_):
    global main
    p=w.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(p))
    if p.value==pid:
        b=ctypes.create_unicode_buffer(1024);u.GetWindowTextW(h,b,len(b))
        if b.value.startswith('FinalBurn') and 'Special 2017' in b.value:main=h
    return True
deadline=time.monotonic()+55
while main is None and time.monotonic()<deadline:
    u.EnumWindows(visit,0);time.sleep(.5)
if main is None:raise SystemExit('Test instance did not finish loading')
before=set(Path('reports/fbneo-shadow-test/screenshots').glob('*.png'))
assert u.PostMessageW(main,0x111,10318,0),ctypes.get_last_error()
deadline=time.monotonic()+5
while time.monotonic()<deadline:
    added=set(Path('reports/fbneo-shadow-test/screenshots').glob('*.png'))-before
    if added:
        print(next(iter(added)),flush=True);break
    time.sleep(.1)
else:raise SystemExit('No screenshot appeared')
