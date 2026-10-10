import ctypes,sys,time
from ctypes import wintypes as w
from pathlib import Path
sys.path.insert(0,str(Path('tools/pillow').resolve()))
from PIL import ImageGrab,Image
u=ctypes.WinDLL('user32')
pid=int(Path('reports/fbneo-animality-pid.txt').read_text())
CB=ctypes.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
u.GetWindowTextW.argtypes=[w.HWND,w.LPWSTR,ctypes.c_int]
u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
windows=[]
@CB
def find(h,_):
    p=w.DWORD();u.GetWindowThreadProcessId(h,ctypes.byref(p))
    b=ctypes.create_unicode_buffer(512);u.GetWindowTextW(h,b,len(b))
    if p.value==pid and 'FinalBurn Neo' in b.value:windows.append(h)
    return True
u.EnumWindows(find,0)
assert len(windows)==1
h=windows[0]
u.PostMessageW(h,0x111,10008,0)
frames=[]
for i in range(40):
    im=ImageGrab.grab(window=h)
    if i in (4,12,28):im.save(f'assets/ukyo-animality/fbneo-live-{i:02d}.png')
    frames.append(im.resize((640,492),Image.Resampling.NEAREST))
    time.sleep(.09)
frames[0].save('assets/ukyo-animality/fbneo-live-finish.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
print('Captured real FBNeo finishing sequence.')
