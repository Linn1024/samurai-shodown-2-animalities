import ctypes
from ctypes import wintypes as w
u=ctypes.WinDLL('user32',use_last_error=True)
CB=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int]
u.GetDlgItem.argtypes=[w.HWND,ctypes.c_int];u.GetDlgItem.restype=w.HWND
u.GetDlgItemTextA.argtypes=[w.HWND,ctypes.c_int,ctypes.c_char_p,ctypes.c_int]
def title(h):
    b=ctypes.create_unicode_buffer(65536);u.GetWindowTextW(h,b,len(b));return b.value
def text(h,i):
    b=ctypes.create_string_buffer(65536);u.GetDlgItemTextA(h,i,b,len(b));return b.value.decode('mbcs',errors='replace')
@CB
def visit(h,_):
    if title(h)=='Lua Script':
        print('WINDOW',h,'PATH',repr(title(u.GetDlgItem(h,20368))),'BUTTON',repr(title(u.GetDlgItem(h,20366))))
        print('OUTPUT',repr(title(u.GetDlgItem(h,20369))))
    return True
u.EnumWindows(visit,0)

