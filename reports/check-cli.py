import runpy,ctypes,time
from pathlib import Path
n=runpy.run_path('fbneo-ultimate.py'); u=n['u']
pid=int(Path('reports/fbneo-cli-pid.txt').read_text())
for h in n['windows']():
    p=ctypes.c_ulong(); u.GetWindowThreadProcessId(h,ctypes.byref(p))
    if p.value==pid and n['title'](h).startswith('FinalBurn'):
        print(h,u.PostMessageW(h,0x111,10617,0))
        u.ShowWindow(h,9); u.SetForegroundWindow(h)
time.sleep(3)
print('file',Path('reports/fbneo-smoke-ok.txt').exists())
