import ctypes
from ctypes import wintypes as w
from pathlib import Path
u = ctypes.windll.user32
pid = int(Path(__file__).with_name('fbneo-test-pid.txt').read_text(encoding='utf-8-sig').strip())
CB = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
def show(hwnd, _):
    p = w.DWORD()
    u.GetWindowThreadProcessId(hwnd, ctypes.byref(p))
    if p.value == pid:
        buf = ctypes.create_unicode_buffer(2048)
        u.GetWindowTextW(hwnd, buf, 2048)
        print(hwnd, repr(buf.value), 'visible=', bool(u.IsWindowVisible(hwnd)))
        @CB
        def child(h, _):
            b = ctypes.create_unicode_buffer(2048)
            u.GetWindowTextW(h, b, 2048)
            if b.value:
                print('  ', repr(b.value))
            return True
        u.EnumChildWindows(hwnd, child, 0)
    return True
u.EnumWindows(CB(show), 0)
